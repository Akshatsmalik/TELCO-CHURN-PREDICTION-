"""
clean.py

Loads raw Telco Customer Churn CSV data, cleans column names, standardises text fields,
handles missing total charges, encodes binary flags, adds tenure buckets, and exports to Parquet.
"""

from pathlib import Path
import re
import pandas as pd
import numpy as np


def camel_to_snake(column_name: str) -> str:
    """
    Converts CamelCase column names to snake_case.
    Explicitly maps 'customerID' to 'customer_id' to prevent 'customer_i_d'.
    """
    if column_name == "customerID":
        return "customer_id"
    # Insert underscore before capital letters and lowercase everything
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', column_name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def clean_data(input_path: Path = None, output_path: Path = None) -> pd.DataFrame:
    """
    Cleans raw Telco Customer Churn data and writes the output as a Parquet file.
    
    Args:
        input_path: Path to the raw CSV file.
        output_path: Path to write the cleaned Parquet file.
        
    Returns:
        pd.DataFrame: Cleaned pandas DataFrame.
    """
    # Define default relative paths based on project root
    project_root = Path(__file__).parent.parent
    if input_path is None:
        input_path = project_root / "data" / "raw" / "telco.csv"
    if output_path is None:
        output_path = project_root / "data" / "processed" / "telco_clean.parquet"

    # Step 1: Load raw CSV dataset
    df = pd.read_csv(input_path)
    
    # Step 2: Standardise column names to lowercase snake_case
    df.columns = [camel_to_snake(col) for col in df.columns]

    # Step 3: Clean TotalCharges field
    # TotalCharges is loaded as object/string due to 11 empty space entries (" ").
    # Coercing errors turns blanks into NaN.
    # WHY: Customers with blank TotalCharges all have tenure = 0 (new sign-ups who haven't completed 
    # their first monthly billing cycle). Setting their total_charges to 0.0 reflects actual billed revenue.
    df["total_charges"] = pd.to_numeric(df["total_charges"], errors="coerce").fillna(0.0)

    # Step 4: Standardise redundant service status text
    # "No internet service" and "No phone service" represent the absence of a service, 
    # which is conceptually identical to "No" for individual feature add-ons.
    replace_cols = [
        "multiple_lines", "online_security", "online_backup", 
        "device_protection", "tech_support", "streaming_tv", "streaming_movies"
    ]
    for col in replace_cols:
        df[col] = df[col].replace({"No internet service": "No", "No phone service": "No"})

    # Step 5: Map binary Yes/No columns to numeric 1/0 flags
    # Keeping gender, internet_service, contract, and payment_method as descriptive text for star schema dimensions.
    binary_cols = [
        "partner", "dependents", "phone_service", "multiple_lines",
        "online_security", "online_backup", "device_protection", "tech_support",
        "streaming_tv", "streaming_movies", "paperless_billing", "churn"
    ]
    for col in binary_cols:
        df[col] = df[col].map({"Yes": 1, "No": 0}).astype(int)

    # Step 6: Create tenure buckets
    # Categorising tenure into meaningful operational cohorts (0-6m, 7-12m, 13-24m, 25-48m, 49-72m)
    # to analyse retention patterns across customer lifecycle stages.
    bins = [-1, 6, 12, 24, 48, np.inf]
    labels = ["0-6", "7-12", "13-24", "25-48", "49-72"]
    df["tenure_bucket"] = pd.cut(df["tenure"], bins=bins, labels=labels).astype(str)

    # Ensure output directory exists and export to Parquet for efficient storage and schema preservation
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    
    return df


if __name__ == "__main__":
    cleaned_df = clean_data()
    print(f"Cleaned dataset shape: {cleaned_df.shape}")
