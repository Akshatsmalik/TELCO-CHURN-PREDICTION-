# telco-churn-pipeline

A clean, beginner-readable, end-to-end data engineering pipeline built with Python, Pandas, PyArrow, and SQLite. This project ingests raw Telco customer data, cleans and standardises it, enforces strict data quality validations, loads it into a star schema database, runs analytical SQL queries to evaluate churn drivers and revenue impact, and provides a Tableau Executive Dashboard.

---

## Problem Statement

Customer churn poses a significant financial challenge for telecommunications service providers. Acquiring new customers is often significantly more expensive than retaining existing subscribers. The objective of this data engineering project is to extract, transform, clean, validate, and analyze customer subscription records from the IBM Telco Customer Churn dataset (7,043 rows, 21 columns) to understand subscriber drop-off patterns, quantify annualised revenue loss, and pinpoint high-risk customer segments.

---

## Project Structure

```text
telco-churn-pipeline/
├── data/
│   ├── raw/
│   │   └── telco.csv
│   └── processed/
│       └── telco_clean.parquet
├── sql/
│   ├── 01_create_star_schema.sql
│   └── 02_churn_analysis.sql
├── src/
│   ├── clean.py
│   ├── validate.py
│   ├── load.py
│   ├── run_sql.py
│   └── create_tableau_twb.py
├── outputs/
│   ├── analysis_results.csv
│   └── tableau_dashboard.html
├── tableau_churn_dashboard.twb
├── run_pipeline.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Architecture Flow

```text
Raw CSV -> Clean (pandas) -> Validate -> Parquet -> SQLite staging -> Star Schema DDL -> SQL Analysis -> CSV Outputs -> Tableau Dashboard
```

1. **Clean (`src/clean.py`)**: Loads raw CSV, normalises column names to `snake_case`, handles blank string values in `TotalCharges`, unifies redundant category labels ("No internet service" / "No phone service" -> "No"), maps Yes/No fields to binary 1/0 flags, and creates tenure cohorts (`tenure_bucket`). Saves output to `data/processed/telco_clean.parquet`.
2. **Validate (`src/validate.py`)**: Asserts primary key uniqueness, checks zero null count, verifies positive charges/tenure values, enforces allowed categorical domains, and reports soft warnings for pricing anomalies.
3. **Load (`src/load.py`)**: Stages cleaned Parquet data into SQLite database `churn.db` as `stg_customers`.
4. **Star Schema (`sql/01_create_star_schema.sql`)**: Transforms staging records into a dimensional model consisting of 1 central Fact table (`fact_subscription`) and 3 Dimension tables (`dim_customer`, `dim_contract`, `dim_services`).
5. **SQL Analysis (`sql/02_churn_analysis.sql` & `src/run_sql.py`)**: Executes 9 analytical queries joining facts and dimensions. Formats query outputs into readable terminal tables and saves results as CSV files in `outputs/`.
6. **Tableau Integration (`tableau_churn_dashboard.twb` & `outputs/tableau_dashboard.html`)**: Generates an interactive web dashboard and a Tableau Desktop workbook file pre-connected to the pipeline outputs.

---

## Tableau Executive Dashboard

The project includes two Tableau dashboard options:

### 1. Interactive Web Dashboard (`outputs/tableau_dashboard.html`)
- Open `outputs/tableau_dashboard.html` directly in any web browser.
- Displays interactive KPI scorecards (**Overall Churn Rate 26.54%**, **Annual Revenue Loss \$1.67M**, **M2M Churn 42.71%**, **Top Risk Segment 54.61%**).
- Includes visual progress charts for Contract Type Churn, Retention Curves across Tenure Cohorts, Payment Method Friction, Tech Support Value Add, and a Top 5 Riskiest Segment Matrix.

### 2. Tableau Desktop Workbook (`tableau_churn_dashboard.twb`)
- Double-click `tableau_churn_dashboard.twb` to open in **Tableau Desktop** or **Tableau Public**.
- Pre-configured data source connecting directly to `outputs/analysis_results.csv` and `churn.db`.

---

## Star Schema Design

| Table Name | Type | Description | Key Attributes |
| :--- | :--- | :--- | :--- |
| `fact_subscription` | Fact | Central event table storing subscription metrics and churn status | `customer_key` (FK), `contract_key` (FK), `services_key` (FK), `tenure`, `tenure_bucket`, `monthly_charges`, `total_charges`, `churn` |
| `dim_customer` | Dimension | Customer demographic profiles | `customer_key` (PK), `customer_id`, `gender`, `senior_citizen`, `partner`, `dependents` |
| `dim_contract` | Dimension | Contract terms, payment methods, and paperless billing preference | `contract_key` (PK), `contract`, `payment_method`, `paperless_billing` |
| `dim_services` | Dimension | Phone, internet, and value-added security/entertainment services | `services_key` (PK), `phone_service`, `multiple_lines`, `internet_service`, `online_security`, `online_backup`, `device_protection`, `tech_support`, `streaming_tv`, `streaming_movies` |

---

## How to Run

### 1. Prerequisites
- Python 3.10+ installed on your system.

### 2. Setup Virtual Environment
```bash
# Navigate to project directory
cd telco-churn-pipeline

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Run Pipeline
```bash
python run_pipeline.py
```

### 4. View Tableau Dashboard
- **Web Browser**: Open `outputs/tableau_dashboard.html` in Chrome/Edge/Firefox.
- **Tableau Desktop**: Double-click `tableau_churn_dashboard.twb`.

---

## Data Quality Issues Found & Resolved

During pipeline execution and exploratory validation, the following data quality issues were identified and addressed:

1. **Blank `TotalCharges` Text Values**:
   - **Issue**: 11 records in the raw CSV contained a blank string space `" "` for `TotalCharges`, causing Pandas to read the entire column as text (`object`).
   - **Root Cause & Fix**: All 11 records corresponded to new customers with `tenure = 0` who had signed up but not yet completed a monthly billing cycle. `src/clean.py` coerced blank spaces to `0.0` with explicit documentation explaining the business rationale.
2. **Redundant Service Category Labels**:
   - **Issue**: Columns such as `online_security`, `tech_support`, and `multiple_lines` contained redundant values like `"No internet service"` or `"No phone service"` alongside `"No"`.
   - **Fix**: Standardised these values to a clean binary `"No"` before mapping Yes/No strings to numerical `1`/`0` flags.
3. **Historical Price Fluctuation Warnings**:
   - **Issue**: Validation flagged 2 records (0.03%) where `total_charges` deviated by >50% from `tenure * monthly_charges`.
   - **Handling**: Retained as valid data; the variance reflects legitimate historical price changes and plan upgrades over long subscriber tenures.

---

## Key Findings (Real Analysis Results)

All figures below are generated directly from executing `run_pipeline.py` against `sql/02_churn_analysis.sql`:

1. **Overall Churn Baseline**:
   - **26.54%** overall churn rate across the customer base (1,869 churned customers out of 7,043 total subscribers).
2. **Contract Type Impact**:
   - **Month-to-month contracts**: **42.71%** churn rate (1,655 churned out of 3,875).
   - **One year contracts**: **11.27%** churn rate (166 churned out of 1,473).
   - **Two year contracts**: **2.83%** churn rate (48 churned out of 1,695).
   - *Insight*: Month-to-month subscribers are ~15x more likely to churn than two-year contract subscribers.
3. **Lifecycle & Retention Curve**:
   - **0–6 Months Tenure**: **52.94%** churn rate (only **47.06%** retention rate).
   - **49–72 Months Tenure**: **9.51%** churn rate (**90.49%** retention rate).
   - *Insight*: The first 6 months are the critical drop-off window. Retention stabilizes dramatically after 24 months.
4. **Payment Method Friction**:
   - **Electronic check**: **45.29%** churn rate (1,071 churned out of 2,365).
   - **Automatic Credit Card / Bank Transfer**: **15.24% – 16.71%** churn rate.
   - *Insight*: Manual electronic check payment methods suffer from 3x higher churn than automated billing setup.
5. **Service Tier & Support Value**:
   - **Fiber Optic Subscribers**: **41.89%** churn rate vs **18.96%** for DSL subscribers.
   - **Tech Support Impact**: Subscribers without Tech Support churn at **31.19%**, whereas subscribers with Tech Support churn at **15.17%** (more than 50% reduction in churn).
6. **Financial Loss**:
   - Monthly lost revenue: **\$139,130.85**
   - **Annualised Revenue Lost to Churn**: **\$1,669,570.20** per year.
7. **Top Riskiest Customer Segment**:
   - **Fiber Optic + Month-to-month Contract**: Rank #1 riskiest segment with a **54.61%** churn rate (1,162 churned subscribers out of 2,128).

---

## Next Steps

1. **Statistical Hypothesis Testing & A/B Testing**: Run Chi-Square tests of independence and simulate A/B test campaigns offering targeted contract upgrade discounts to Month-to-month subscribers.
2. **Predictive Machine Learning Model**: Build an XGBoost / Logistic Regression model using `data/processed/telco_clean.parquet` to calculate real-time churn risk scores per customer.
3. **Workflow Orchestration**: Port the pipeline orchestration from `run_pipeline.py` to Apache Airflow or Prefect for scheduled daily ingestion and data freshness monitoring.
