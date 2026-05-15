#!/usr/bin/env python3
"""SQL for data science — Polars + DuckDB rewrite (real SQL replaces pandas substitutes)."""

import yaml
import logging
from pathlib import Path

from core import create_sample_database, execute_sql_query, analyze_sql_results

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_config(config_path: Path = None) -> dict:
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def main():
    config   = load_config()
    output_dir = Path(config.get("output", {}).get("figures_dir", "images"))
    output_dir.mkdir(exist_ok=True)

    db = create_sample_database()
    customers, orders = db["customers"], db["orders"]
    logging.info(f"Customers: {customers.height:,} rows  |  Orders: {orders.height:,} rows")

    # ── JOIN ─────────────────────────────────────────────────────────────────
    joined = execute_sql_query(customers, orders, "join")
    stats  = analyze_sql_results(joined)
    logging.info(f"\nJOIN  → {stats['n_rows']:,} rows  {stats['n_columns']} cols  "
                 f"{stats['memory_mb']:.2f} MB")
    logging.info(f"{joined.head(3)}")

    # ── GROUP BY aggregate ───────────────────────────────────────────────────
    agg = execute_sql_query(customers, orders, "aggregate")
    logging.info(f"\nGROUP BY  → top spenders:\n{agg.head(5)}")

    # ── WHERE filter ─────────────────────────────────────────────────────────
    completed = execute_sql_query(customers, orders, "filter")
    logging.info(f"\nWHERE status='completed'  → {completed.height:,} orders")

    # ── window: revenue rank per region ──────────────────────────────────────
    import duckdb
    ranked = duckdb.sql("""
        SELECT
            c.region,
            c.customer_id,
            SUM(o.amount) AS total_spend,
            RANK() OVER (PARTITION BY c.region ORDER BY SUM(o.amount) DESC) AS region_rank
        FROM customers c
        JOIN orders o USING (customer_id)
        WHERE o.status = 'completed'
        GROUP BY c.region, c.customer_id
        QUALIFY region_rank <= 3
        ORDER BY c.region, region_rank
    """).pl()
    logging.info(f"\nTop 3 spenders per region (RANK OVER PARTITION):\n{ranked}")


if __name__ == "__main__":
    main()
