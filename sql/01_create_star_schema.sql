-- 01_create_star_schema.sql
-- Builds a dimensional star schema (dim_customer, dim_contract, dim_services, fact_subscription)
-- from staging table stg_customers in SQLite churn.db.

-- Drop tables if they exist to ensure script re-runnability
DROP TABLE IF EXISTS fact_subscription;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_contract;
DROP TABLE IF EXISTS dim_services;

-- 1. Create dim_customer (Customer demographic dimension)
CREATE TABLE dim_customer (
    customer_key INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    gender TEXT NOT NULL,
    senior_citizen INTEGER NOT NULL,
    partner INTEGER NOT NULL,
    dependents INTEGER NOT NULL
);

INSERT INTO dim_customer (customer_id, gender, senior_citizen, partner, dependents)
SELECT customer_id, gender, senior_citizen, partner, dependents
FROM stg_customers;

-- 2. Create dim_contract (Contract & billing dimension, unique combinations)
CREATE TABLE dim_contract (
    contract_key INTEGER PRIMARY KEY AUTOINCREMENT,
    contract TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    paperless_billing INTEGER NOT NULL
);

INSERT INTO dim_contract (contract, payment_method, paperless_billing)
SELECT DISTINCT contract, payment_method, paperless_billing
FROM stg_customers;

-- 3. Create dim_services (Subscribed services dimension, unique combinations)
CREATE TABLE dim_services (
    services_key INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_service INTEGER NOT NULL,
    multiple_lines INTEGER NOT NULL,
    internet_service TEXT NOT NULL,
    online_security INTEGER NOT NULL,
    online_backup INTEGER NOT NULL,
    device_protection INTEGER NOT NULL,
    tech_support INTEGER NOT NULL,
    streaming_tv INTEGER NOT NULL,
    streaming_movies INTEGER NOT NULL
);

INSERT INTO dim_services (
    phone_service, multiple_lines, internet_service,
    online_security, online_backup, device_protection,
    tech_support, streaming_tv, streaming_movies
)
SELECT DISTINCT
    phone_service, multiple_lines, internet_service,
    online_security, online_backup, device_protection,
    tech_support, streaming_tv, streaming_movies
FROM stg_customers;

-- 4. Create fact_subscription (Subscription fact table linking customer, contract, services dimensions)
CREATE TABLE fact_subscription (
    customer_key INTEGER NOT NULL,
    contract_key INTEGER NOT NULL,
    services_key INTEGER NOT NULL,
    tenure INTEGER NOT NULL,
    tenure_bucket TEXT NOT NULL,
    monthly_charges REAL NOT NULL,
    total_charges REAL NOT NULL,
    churn INTEGER NOT NULL,
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (contract_key) REFERENCES dim_contract(contract_key),
    FOREIGN KEY (services_key) REFERENCES dim_services(services_key)
);

INSERT INTO fact_subscription (
    customer_key, contract_key, services_key,
    tenure, tenure_bucket, monthly_charges, total_charges, churn
)
SELECT
    dc.customer_key,
    dcon.contract_key,
    ds.services_key,
    s.tenure,
    s.tenure_bucket,
    s.monthly_charges,
    s.total_charges,
    s.churn
FROM stg_customers s
JOIN dim_customer dc ON s.customer_id = dc.customer_id
JOIN dim_contract dcon ON s.contract = dcon.contract
    AND s.payment_method = dcon.payment_method
    AND s.paperless_billing = dcon.paperless_billing
JOIN dim_services ds ON s.phone_service = ds.phone_service
    AND s.multiple_lines = ds.multiple_lines
    AND s.internet_service = ds.internet_service
    AND s.online_security = ds.online_security
    AND s.online_backup = ds.online_backup
    AND s.device_protection = ds.device_protection
    AND s.tech_support = ds.tech_support
    AND s.streaming_tv = ds.streaming_tv
    AND s.streaming_movies = ds.streaming_movies;

-- Final verification check query confirming fact row count matches input dataset (7,043)
SELECT COUNT(*) AS fact_count FROM fact_subscription;
