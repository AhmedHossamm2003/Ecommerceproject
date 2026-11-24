-- Phase 6 Power BI-facing views. Repeatable and read-only over pipeline data.

CREATE OR REPLACE VIEW analytics.vw_executive_kpis AS
SELECT
    ROUND(SUM(item_price), 2) AS delivered_sales_revenue,
    COUNT(DISTINCT order_id)::BIGINT AS delivered_orders,
    COUNT(*)::BIGINT AS delivered_items,
    COUNT(DISTINCT customers.customer_unique_id)::BIGINT AS purchasing_customers,
    ROUND(SUM(freight_value), 2) AS delivered_freight_value,
    ROUND(SUM(item_price) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS average_order_item_revenue,
    MIN(order_purchase_timestamp)::DATE AS first_purchase_date,
    MAX(order_purchase_timestamp)::DATE AS last_purchase_date
FROM warehouse.fact_order_items AS items
JOIN warehouse.dim_customers AS customers
    ON customers.customer_key = items.customer_key
WHERE items.order_status = 'delivered';

CREATE OR REPLACE VIEW analytics.vw_pipeline_health AS
WITH latest_transform AS (
    SELECT transformation_run_id, status, clean_records, fact_records,
           rejected_records, finished_at
    FROM clean_data.transformation_runs
    ORDER BY started_at DESC
    LIMIT 1
),
latest_gate AS (
    SELECT gate_run_id, status, rules_evaluated, blocking_failures,
           warning_failures, finished_at
    FROM quality.gate_runs
    ORDER BY started_at DESC
    LIMIT 1
)
SELECT
    transform.transformation_run_id,
    transform.status AS transformation_status,
    transform.clean_records,
    transform.fact_records,
    transform.rejected_records,
    transform.finished_at AS transformation_finished_at,
    gate.gate_run_id,
    gate.status AS quality_gate_status,
    gate.rules_evaluated,
    gate.blocking_failures,
    gate.warning_failures,
    gate.finished_at AS quality_gate_finished_at
FROM latest_transform AS transform
LEFT JOIN latest_gate AS gate ON TRUE;

COMMENT ON VIEW analytics.vw_executive_kpis IS
    'Single-row delivered-sales KPI source for the Power BI executive page.';
COMMENT ON VIEW analytics.vw_pipeline_health IS
    'Latest transformation and quality-gate status for dashboard freshness.';
