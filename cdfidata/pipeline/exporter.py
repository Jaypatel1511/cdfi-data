"""
Export cleaned CDFI Fund DataFrames to CSV, SQLite, and Parquet formats.
"""
import pandas as pd
from pathlib import Path


def to_csv(df: pd.DataFrame, path: str, **kwargs) -> None:
    """Export DataFrame to CSV."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, **kwargs)
    print(f"Exported {len(df):,} rows to {path}")


def to_sqlite(df: pd.DataFrame, db_path: str, table_name: str,
              if_exists: str = "replace") -> None:
    """
    Export DataFrame to a SQLite database table.

    Args:
        df:         DataFrame to export
        db_path:    Path to SQLite database file
        table_name: Table name to write to
        if_exists:  'replace', 'append', or 'fail'
    """
    import sqlite3
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as conn:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
    print(f"Exported {len(df):,} rows to {path} (table: {table_name})")


def to_parquet(df: pd.DataFrame, path: str, **kwargs) -> None:
    """Export DataFrame to Parquet format."""
    try:
        import pyarrow
    except ImportError:
        raise ImportError(
            "pyarrow is required for parquet export. "
            "Install it with: pip install pyarrow"
        )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False, **kwargs)
    print(f"Exported {len(df):,} rows to {path}")


def export_all(df: pd.DataFrame, base_path: str, table_name: str) -> None:
    """
    Export to all three formats at once.

    Args:
        df:         DataFrame to export
        base_path:  Base path without extension
        table_name: SQLite table name
    """
    to_csv(df, f"{base_path}.csv")
    to_sqlite(df, f"{base_path}.db", table_name)
    try:
        to_parquet(df, f"{base_path}.parquet")
    except ImportError:
        print("Skipping parquet export — pyarrow not installed")
