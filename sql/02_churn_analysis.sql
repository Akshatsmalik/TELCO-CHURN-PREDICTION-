-- 02_churn_analysis.sql
-- Analytical SQL queries performing churn analysis across dimension attributes and fact metrics.

-- Query 1: Overall Churn Rate
-- Measures the overall baseline percentage of lost customers across the entire subscriber base.
SELECT
    COUNT(*) AS total_customers,
    SUM(churn) AS churned_customers,
    COUNT(*) - SUM(churn) AS retained_customers,
    ROUND(AVG(churn) * 100.0, 2) AS churn_rate_pct
FROM fact_subscription;

-- Query 2: Churn Rate by Contract Type
-- Joins fact with dim_contract to compare churn risk across short-term vs long-term contracts.
SELECT
    c.contract,
    COUNT(*) AS total_customers,
    SUM(f.churn) AS churned_customers,
    ROUND(AVG(f.churn) * 100.0, 2) AS churn_rate_pct
FROM fact_subscription f
JOIN dim_contract c ON f.contract_key = c.contract_key
GROUP BY c.contract
ORDER BY churn_rate_pct DESC;

-- Query 3: Churn Rate by Tenure Bucket
-- Evaluates churn rates across customer lifecycle cohorts to identify early subscriber drop-off windows.
SELECT
    f.tenure_bucket,
    COUNT(*) AS total_customers,
    SUM(f.churn) AS churned_customers,
    ROUND(AVG(f.churn) * 100.0, 2) AS churn_rate_pct
FROM fact_subscription f
GROUP BY f.tenure_bucket
ORDER BY 
    CASE f.tenure_bucket
        WHEN '0-6' THEN 1
        WHEN '7-12' THEN 2
        WHEN '13-24' THEN 3
        WHEN '25-48' THEN 4
        WHEN '49-72' THEN 5
        ELSE 6
    END;

-- Query 4: Churn Rate by Payment Method
-- Analyzes how payment friction (e.g. manual electronic check vs automated bank draft) correlates with churn.
SELECT
    c.payment_method,
    COUNT(*) AS total_customers,
    SUM(f.churn) AS churned_customers,
    ROUND(AVG(f.churn) * 100.0, 2) AS churn_rate_pct
FROM fact_subscription f
JOIN dim_contract c ON f.contract_key = c.contract_key
GROUP BY c.payment_method
ORDER BY churn_rate_pct DESC;

-- Query 5: Churn Rate by Internet Service Type
-- Compares churn rates across Fiber Optic, DSL, and No Internet service tiers.
SELECT
    s.internet_service,
    COUNT(*) AS total_customers,
    SUM(f.churn) AS churned_customers,
    ROUND(AVG(f.churn) * 100.0, 2) AS churn_rate_pct
FROM fact_subscription f
JOIN dim_services s ON f.services_key = s.services_key
GROUP BY s.internet_service
ORDER BY churn_rate_pct DESC;

-- Query 6: Churn Rate With vs Without Tech Support
-- Measures the impact of value-added customer support services on subscriber retention.
SELECT
    CASE WHEN s.tech_support = 1 THEN 'With Tech Support' ELSE 'No Tech Support' END AS tech_support_status,
    COUNT(*) AS total_customers,
    SUM(f.churn) AS churned_customers,
    ROUND(AVG(f.churn) * 100.0, 2) AS churn_rate_pct
FROM fact_subscription f
JOIN dim_services s ON f.services_key = s.services_key
GROUP BY s.tech_support
ORDER BY churn_rate_pct DESC;

-- Query 7: Annualised Revenue Lost to Churn
-- Calculates total financial revenue loss per year resulting from churned customer subscriptions.
SELECT
    SUM(f.churn) AS churned_customers,
    ROUND(SUM(f.monthly_charges), 2) AS monthly_revenue_lost,
    ROUND(SUM(f.monthly_charges * 12), 2) AS annualised_revenue_lost
FROM fact_subscription f
WHERE f.churn = 1;

-- Query 8: Top 5 Riskiest Segments (Internet Service + Contract)
-- Employs a CTE and RANK() window function to isolate the top 5 highest-risk customer segments.
WITH segment_churn AS (
    SELECT
        s.internet_service,
        c.contract,
        COUNT(*) AS total_customers,
        SUM(f.churn) AS churned_customers,
        ROUND(AVG(f.churn) * 100.0, 2) AS churn_rate_pct,
        RANK() OVER (ORDER BY AVG(f.churn) DESC, COUNT(*) DESC) AS risk_rank
    FROM fact_subscription f
    JOIN dim_services s ON f.services_key = s.services_key
    JOIN dim_contract c ON f.contract_key = c.contract_key
    GROUP BY s.internet_service, c.contract
)
SELECT
    risk_rank,
    internet_service,
    contract,
    total_customers,
    churned_customers,
    churn_rate_pct
FROM segment_churn
WHERE risk_rank <= 5
ORDER BY risk_rank;

-- Query 9: Retention Curve (Active Customer Percentage by Tenure Bucket)
-- Analyzes active subscriber survival percentage across tenure cohorts.
SELECT
    f.tenure_bucket,
    COUNT(*) AS total_customers,
    COUNT(*) - SUM(f.churn) AS active_customers,
    ROUND((COUNT(*) - SUM(f.churn)) * 100.0 / COUNT(*), 2) AS retention_rate_pct
FROM fact_subscription f
GROUP BY f.tenure_bucket
ORDER BY 
    CASE f.tenure_bucket
        WHEN '0-6' THEN 1
        WHEN '7-12' THEN 2
        WHEN '13-24' THEN 3
        WHEN '25-48' THEN 4
        WHEN '49-72' THEN 5
        ELSE 6
    END;
