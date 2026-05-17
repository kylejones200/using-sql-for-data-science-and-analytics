"""Core functions for using SQL for data science and analytics."""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_config(config_path=None):
    """Load configuration from YAML file."""
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        return {}
    with open(config_path) as _f:
        import yaml as _yaml

        return _yaml.safe_load(_f) or {}


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")


def create_sample_database(
    n_customers: int = 1000, n_orders: int = 5000, seed: int = 42
) -> dict:
    """Create sample database tables for SQL demonstration."""
    np.random.seed(seed)

    customers = pd.DataFrame(
        {
            "customer_id": range(1, n_customers + 1),
            "name": [f"Customer_{i}" for i in range(1, n_customers + 1)],
            "region": np.random.choice(["North", "South", "East", "West"], n_customers),
            "signup_date": pd.date_range("2020-01-01", periods=n_customers, freq="D"),
        }
    )

    orders = pd.DataFrame(
        {
            "order_id": range(1, n_orders + 1),
            "customer_id": np.random.choice(customers["customer_id"], n_orders),
            "order_date": pd.date_range("2023-01-01", periods=n_orders, freq="H"),
            "amount": np.random.normal(100, 30, n_orders),
            "status": np.random.choice(["completed", "pending", "cancelled"], n_orders),
        }
    )

    return {"customers": customers, "orders": orders}


def execute_sql_query(
    customers: pd.DataFrame, orders: pd.DataFrame, query_type: str = "join"
) -> pd.DataFrame:
    """Execute SQL-like query on DataFrames."""
    if query_type == "join":
        return pd.merge(customers, orders, on="customer_id", how="inner")
    elif query_type == "aggregate":
        return (
            orders.groupby("customer_id")
            .agg({"amount": ["sum", "mean", "count"]})
            .reset_index()
        )
    elif query_type == "filter":
        return orders[orders["status"] == "completed"]
    return pd.DataFrame()


def analyze_sql_results(df: pd.DataFrame) -> dict:
    """Analyze SQL query results."""
    return {
        "n_rows": len(df),
        "n_columns": len(df.columns),
        "memory_mb": df.memory_usage(deep=True).sum() / 1024**2,
    }


def plot_sql_analysis(
    df: pd.DataFrame, title: str, output_path: Path, plot: bool = False
):
    """Plot SQL analysis results"""
    if not plot:
        return

    fig, ax = plt.subplots(
        figsize=tuple(config.get("output", {}).get("figsize", [10, 6]))
    )

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        col = numeric_cols[0]
        ax.hist(
            df[col].dropna(), bins=30, color="#4A90A4", alpha=0.7, edgecolor="none"
        )
        ax.set_xlabel(col)
    else:
        categorical_cols = df.select_dtypes(include=["object"]).columns
        if len(categorical_cols) > 0:
            value_counts = df[categorical_cols[0]].value_counts().head(10)
            ax.bar(
                range(len(value_counts)),
                value_counts.values,
                color="#4A90A4",
                alpha=0.7,
                edgecolor="none",
            )
            ax.set_xticks(range(len(value_counts)))
            ax.set_xticklabels(value_counts.index, rotation=45, ha="right")
            ax.set_xlabel(categorical_cols[0])

    ax.set_ylabel("Frequency")

    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close()
