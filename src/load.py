"""
load.py

Loads the cleaned Parquet dataset into SQLite database `churn.db` as staging table `stg_customers`.
"""

from pathlib import Path
import sqlite3
import pandas as pd


def load_staging(parquet_path: Path = None, db_path: Path = None) -> int:
    """
    Reads telco_clean.parquet and writes it into churn.db under the stg_customers table.
    
    Args:
        parquet_path: Path to input cleaned Parquet file.
        db_path: Path to SQLite database.
        
    Returns:
        int: Number of rows inserted into stg_customers.
    """
    project_root = Path(__file__).parent.parent
    if parquet_path is None:
        parquet_path = project_root / "data" / "processed" / "telco_clean.parquet"
    if db_path is None:
        db_path = project_root / "churn.db"

    # Step 1: Read cleaned parquet dataset
    df = pd.read_parquet(parquet_path)

    # Step 2: Write to SQLite database as staging table `stg_customers`
    # replacing the table if it already exists to ensure idempotent pipeline runs
    with sqlite3.connect(db_path) as conn:
        df.to_sql("stg_customers", conn, if_exists="replace", index=False)
        
        # Verify row count in SQLite
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM stg_customers;")
        row_count = cursor.fetchone()[0]

    print(f"[LOAD] Successfully loaded {row_count:,} rows into SQLite staging table 'stg_customers' ({db_path.name}).")
    return row_count


if __name__ == "__main__":
    load_staging()
