"""Generated from Jupyter notebook: notebook

Magics and shell lines are commented out. Run with a normal Python interpreter."""

import sqlite3

import pandas as pd


def main():
    conn = sqlite3.connect(":memory:")
    df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "score": [85, 90, 95]})
    df.to_sql("students", conn, index=False, if_exists="replace")
    result = pd.read_sql("SELECT * FROM students WHERE score > 88", conn)
    print(result)


def main() -> None:
    main()


if __name__ == "__main__":
    main()
