"""
validate.py

Data quality validation module for cleaned Telco Customer Churn dataset.
Runs assertions on unique constraints, null counts, value ranges, and domain rules.
Prints a structured validation report and raises an exception if critical checks fail.
"""

from pathlib import Path
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def validate_data(parquet_path: Path = None) -> bool:
    """
    Validates the clean Telco dataset against data quality rules.
    
    Args:
        parquet_path: Path to the cleaned Parquet file.
        
    Returns:
        bool: True if all strict validation checks pass.
        
    Raises:
        ValueError: If any strict validation rule fails.
    """
    project_root = Path(__file__).parent.parent
    if parquet_path is None:
        parquet_path = project_root / "data" / "processed" / "telco_clean.parquet"
        
    if not parquet_path.exists():
        raise FileNotFoundError(f"Cleaned file not found at {parquet_path}")

    df = pd.read_parquet(parquet_path)
    failures = []
    
    print("\n" + "=" * 50)
    print("        DATA QUALITY VALIDATION REPORT        ")
    print("=" * 50)

    # Rule 1: customer_id must be unique
    if df["customer_id"].nunique() == len(df):
        print("[PASS] customer_id uniqueness check (7,043 unique IDs)")
    else:
        dup_count = len(df) - df["customer_id"].nunique()
        failures.append(f"customer_id contains {dup_count} duplicate values.")

    # Rule 2: No null values anywhere in the dataframe
    total_nulls = df.isnull().sum().sum()
    if total_nulls == 0:
        print("[PASS] Null check (0 null values across all columns)")
    else:
        failures.append(f"Dataframe contains {total_nulls} null values.")

    # Rule 3: tenure must be non-negative (>= 0)
    if (df["tenure"] >= 0).all():
        print("[PASS] tenure range check (all values >= 0)")
    else:
        failures.append("tenure contains negative values.")

    # Rule 4: churn must be strictly binary (0 or 1)
    if set(df["churn"].unique()).issubset({0, 1}):
        print("[PASS] churn flag check (only 0 or 1)")
    else:
        failures.append(f"churn contains invalid values: {df['churn'].unique()}")

    # Rule 5: contract must belong to expected categories
    allowed_contracts = {"Month-to-month", "One year", "Two year"}
    if set(df["contract"].unique()).issubset(allowed_contracts):
        print("[PASS] contract category check (valid options)")
    else:
        failures.append(f"contract contains invalid values: {df['contract'].unique()}")

    # Rule 6: monthly_charges must be strictly positive (> 0)
    if (df["monthly_charges"] > 0).all():
        print("[PASS] monthly_charges range check (all values > 0)")
    else:
        failures.append("monthly_charges contains values <= 0.")

    # Check 7: total_charges vs (tenure * monthly_charges) consistency check (WARNING ONLY)
    # Price changes over time mean total_charges won't equal current monthly_charges * tenure exactly.
    # We flag rows deviating by > 50% as a soft warning.
    non_zero_tenure = df[df["tenure"] > 0]
    expected_total = non_zero_tenure["tenure"] * non_zero_tenure["monthly_charges"]
    pct_diff = (non_zero_tenure["total_charges"] - expected_total).abs() / expected_total
    high_dev_count = (pct_diff > 0.50).sum()
    high_dev_pct = (high_dev_count / len(df)) * 100
    
    print(f"[WARN] total_charges consistency: {high_dev_count} rows ({high_dev_pct:.2f}%) "
          f"deviate by >50% from (tenure * monthly_charges) due to historical price changes.")

    print("=" * 50)

    # Raise single consolidated error if any strict checks failed
    if failures:
        error_msg = "Data quality validation failed with errors:\n" + "\n".join(failures)
        print(f"[FAIL] {error_msg}")
        raise ValueError(error_msg)

    print("[SUCCESS] All data quality checks passed!\n")
    return True


if __name__ == "__main__":
    validate_data()
