"""SQL for data science and analytics using DuckDB natively.

The original uses pandas as a SQL substitute:
  pd.merge()             → DuckDB JOIN
  groupby().agg()        → DuckDB GROUP BY
  df[df['col'] == val]   → DuckDB WHERE

Here those operations are expressed as actual SQL executed by DuckDB,
with Polars as the in-memory DataFrame format.
"""

import duckdb
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta
from pathlib import Path
from typing import Dict


def create_sample_database(
    n_customers: int = 1000,
    n_orders: int = 5000,
    seed: int = 42,
) -> Dict[str, pl.DataFrame]:
    rng = np.random.default_rng(seed)
    start = date(2020, 1, 1)

    customers = pl.DataFrame({
        "customer_id": list(range(1, n_customers + 1)),
        "name":        [f"Customer_{i}" for i in range(1, n_customers + 1)],
        "region":      rng.choice(["North", "South", "East", "West"], n_customers).tolist(),
        "signup_date": [start + timedelta(days=i) for i in range(n_customers)],
    })

    order_start = date(2023, 1, 1)
    orders = pl.DataFrame({
        "order_id":    list(range(1, n_orders + 1)),
        "customer_id": rng.integers(1, n_customers + 1, n_orders).tolist(),
        "order_date":  [order_start + timedelta(hours=i) for i in range(n_orders)],
        "amount":      rng.normal(100, 30, n_orders).tolist(),
        "status":      rng.choice(["completed", "pending", "cancelled"], n_orders).tolist(),
    })

    return {"customers": customers, "orders": orders}


def execute_sql_query(
    customers: pl.DataFrame,
    orders: pl.DataFrame,
    query_type: str = "join",
) -> pl.DataFrame:
    """
    Real DuckDB SQL replaces pandas substitutes:
      'join'      → INNER JOIN
      'aggregate' → GROUP BY with SUM / AVG / COUNT
      'filter'    → WHERE status = 'completed'
    """
    if query_type == "join":
        return duckdb.sql("""
            SELECT c.customer_id, c.name, c.region, c.signup_date,
                   o.order_id, o.order_date, o.amount, o.status
            FROM customers c
            JOIN orders o USING (customer_id)
        """).pl()

    if query_type == "aggregate":
        return duckdb.sql("""
            SELECT
                customer_id,
                SUM(amount)   AS sum_amount,
                AVG(amount)   AS mean_amount,
                COUNT(*)      AS count_orders
            FROM orders
            GROUP BY customer_id
            ORDER BY sum_amount DESC
        """).pl()

    if query_type == "filter":
        return duckdb.sql(
            "SELECT * FROM orders WHERE status = 'completed' ORDER BY order_date"
        ).pl()

    return pl.DataFrame()


def analyze_sql_results(df: pl.DataFrame) -> Dict:
    return {
        "n_rows":    df.height,
        "n_columns": df.width,
        "memory_mb": df.estimated_size() / 1024 ** 2,
    }


def plot_sql_analysis(df: pl.DataFrame, title: str, output_path: Path, plot: bool = False):
    if not plot:
        return
    numeric_cols = [c for c, t in zip(df.columns, df.dtypes) if t.is_numeric()]
    cat_cols     = [c for c, t in zip(df.columns, df.dtypes) if t == pl.String]

    fig, ax = plt.subplots(figsize=(10, 6))
    if numeric_cols:
        col  = numeric_cols[0]
        data = df[col].drop_nulls().to_numpy()
        ax.hist(data, bins=30, color="#4A90A4", alpha=0.7, edgecolor="none")
        ax.set_xlabel(col)
    elif cat_cols:
        counts = (
            duckdb.sql(f'SELECT "{cat_cols[0]}", COUNT(*) AS n FROM df '
                       f'GROUP BY "{cat_cols[0]}" ORDER BY n DESC LIMIT 10').pl()
        )
        ax.bar(counts[cat_cols[0]].to_list(), counts["n"].to_list(),
               color="#4A90A4", alpha=0.7, edgecolor="none")
        ax.tick_params(axis="x", rotation=45)
        ax.set_xlabel(cat_cols[0])
    ax.set_ylabel("Frequency")
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close()
