"""SQL for data science — Polars + DuckDB rewrite (real SQL replaces pandas substitutes)."""

import logging
from pathlib import Path

import duckdb
import yaml
from core import analyze_sql_results, create_sample_database, execute_sql_query


def load_config(config_path: Path = None) -> dict:
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def main() -> None:
    config = load_config()

    output_dir = Path(config.get("output", {}).get("figures_dir", "images"))

    output_dir.mkdir(exist_ok=True)

    db = create_sample_database()

    customers, orders = (db["customers"], db["orders"])

    logging.info(
        f"Customers: {customers.height:,} rows  |  Orders: {orders.height:,} rows"
    )

    joined = execute_sql_query(customers, orders, "join")

    stats = analyze_sql_results(joined)

    logging.info(
        f"\nJOIN  → {stats['n_rows']:,} rows  {stats['n_columns']} cols  {stats['memory_mb']:.2f} MB"
    )

    logging.info(f"{joined.head(3)}")

    agg = execute_sql_query(customers, orders, "aggregate")

    logging.info(f"\nGROUP BY  → top spenders:\n{agg.head(5)}")

    completed = execute_sql_query(customers, orders, "filter")

    logging.info(f"\nWHERE status='completed'  → {completed.height:,} orders")

    ranked = duckdb.sql(
        "\n        SELECT\n            c.region,\n            c.customer_id,\n            SUM(o.amount) AS total_spend,\n            RANK() OVER (PARTITION BY c.region ORDER BY SUM(o.amount) DESC) AS region_rank\n        FROM customers c\n        JOIN orders o USING (customer_id)\n        WHERE o.status = 'completed'\n        GROUP BY c.region, c.customer_id\n        QUALIFY region_rank <= 3\n        ORDER BY c.region, region_rank\n    "
    ).pl()

    logging.info(f"\nTop 3 spenders per region (RANK OVER PARTITION):\n{ranked}")


if __name__ == "__main__":
    main()
