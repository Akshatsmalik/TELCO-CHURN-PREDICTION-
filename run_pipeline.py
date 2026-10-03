"""
run_pipeline.py

Main entry point for the Telco Customer Churn Data Engineering Pipeline.
Executes end-to-end steps: Clean -> Validate -> Load Staging -> Build Star Schema -> Run SQL Analysis.
Tracks execution times and row counts with structured logging.
"""

import logging
import sys
import time
from pathlib import Path

# Add project root directory to path for clean imports
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.clean import clean_data
from src.validate import validate_data
from src.load import load_staging
from src.run_sql import execute_sql_file

# Configure logging format and stream
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("telco_churn_pipeline")


def run():
    """Executes the full Telco Churn Data Pipeline with error handling and performance tracking."""
    raw_csv = PROJECT_ROOT / "data" / "raw" / "telco.csv"
    clean_parquet = PROJECT_ROOT / "data" / "processed" / "telco_clean.parquet"
    db_path = PROJECT_ROOT / "churn.db"
    schema_sql = PROJECT_ROOT / "sql" / "01_create_star_schema.sql"
    analysis_sql = PROJECT_ROOT / "sql" / "02_churn_analysis.sql"

    total_start = time.time()
    logger.info("==================================================")
    logger.info(" Starting Telco Customer Churn Data Pipeline")
    logger.info("==================================================")

    try:
        # Stage 1: Data Cleaning
        t0 = time.time()
        logger.info("STAGE 1: Cleaning raw CSV dataset...")
        df_clean = clean_data(raw_csv, clean_parquet)
        t1 = time.time()
        logger.info(f"STAGE 1 PASSED: Processed {len(df_clean):,} rows in {t1 - t0:.2f}s.")

        # Stage 2: Data Quality Validation
        t0 = time.time()
        logger.info("STAGE 2: Running data quality validations...")
        validate_data(clean_parquet)
        t1 = time.time()
        logger.info(f"STAGE 2 PASSED: Validation passed in {t1 - t0:.2f}s.")

        # Stage 3: Load to SQLite Staging
        t0 = time.time()
        logger.info("STAGE 3: Loading parquet data into SQLite staging...")
        stg_count = load_staging(clean_parquet, db_path)
        t1 = time.time()
        logger.info(f"STAGE 3 PASSED: Staged {stg_count:,} records in {t1 - t0:.2f}s.")

        # Stage 4: Star Schema DDL/DML
        t0 = time.time()
        logger.info("STAGE 4: Building Star Schema dimension and fact tables...")
        execute_sql_file(schema_sql, db_path)
        t1 = time.time()
        logger.info(f"STAGE 4 PASSED: Star schema created in {t1 - t0:.2f}s.")

        # Stage 5: Analytical SQL Queries
        t0 = time.time()
        logger.info("STAGE 5: Executing SQL churn analysis queries...")
        query_results = execute_sql_file(analysis_sql, db_path)
        t1 = time.time()
        logger.info(f"STAGE 5 PASSED: Ran {len(query_results)} analytical queries in {t1 - t0:.2f}s.")

        total_elapsed = time.time() - total_start
        logger.info("==================================================")
        logger.info(f" PIPELINE SUCCESS: Completed in {total_elapsed:.2f}s!")
        logger.info("==================================================")

    except Exception as e:
        logger.error("==================================================")
        logger.error(f" PIPELINE FAILED at stage! Error: {e}")
        logger.error("==================================================")
        sys.exit(1)


if __name__ == "__main__":
    run()
