-- Read-only Phase 3 verification queries.

-- 1. Required schemas.
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name IN ('clean_data', 'warehouse', 'analytics')
ORDER BY schema_name;

-- 2. Latest transformation status and selected raw run lineage.
SELECT
    transformation_run_id,
    status,
    clean_records,
    fact_records,
    rejected_records,
    started_at,
    finished_at,
    source_ingestion_runs
FROM clean_data.transformation_runs
ORDER BY started_at DESC
LIMIT 5;

-- 3. Typed clean table counts.
SELECT *
FROM (
    VALUES
        ('customers', (SELECT COUNT(*) FROM clean_data.customers)),
        ('orders', (SELECT COUNT(*) FROM clean_data.orders)),
        ('order_items', (SELECT COUNT(*) FROM clean_data.order_items)),
        ('products', (SELECT COUNT(*) FROM clean_data.products)),
        ('order_payments', (SELECT COUNT(*) FROM clean_data.order_payments)),
        ('order_reviews', (SELECT COUNT(*) FROM clean_data.order_reviews)),
        ('sellers', (SELECT COUNT(*) FROM clean_data.sellers)),
        ('geolocation_unique', (SELECT COUNT(*) FROM clean_data.geolocation)),
        ('category_translation', (SELECT COUNT(*) FROM clean_data.category_translation))
) AS counts(table_name, row_count)
ORDER BY table_name;

-- 4. Auditable rejects for the latest successful run.
WITH latest AS (
    SELECT transformation_run_id
    FROM clean_data.transformation_runs
    WHERE status = 'success'
    ORDER BY finished_at DESC
    LIMIT 1
)
SELECT source_file, reason_code, COUNT(*) AS rejected_rows
FROM clean_data.rejected_records
WHERE transformation_run_id = (SELECT transformation_run_id FROM latest)
GROUP BY source_file, reason_code
ORDER BY source_file, reason_code;

-- 5. Measured quality metrics for the latest successful run.
WITH latest AS (
    SELECT transformation_run_id
    FROM clean_data.transformation_runs
    WHERE status = 'success'
    ORDER BY finished_at DESC
    LIMIT 1
)
SELECT metric_name, metric_value, details
FROM clean_data.quality_metrics
WHERE transformation_run_id = (SELECT transformation_run_id FROM latest)
ORDER BY metric_name;

-- 6. Star-schema table counts and unknown members.
SELECT *
FROM (
    VALUES
        ('dim_customers', (SELECT COUNT(*) FROM warehouse.dim_customers)),
        ('dim_products', (SELECT COUNT(*) FROM warehouse.dim_products)),
        ('dim_sellers', (SELECT COUNT(*) FROM warehouse.dim_sellers)),
        ('dim_date', (SELECT COUNT(*) FROM warehouse.dim_date)),
        ('fact_order_items', (SELECT COUNT(*) FROM warehouse.fact_order_items))
) AS counts(table_name, row_count)
ORDER BY table_name;

-- 7. Row and revenue reconciliation between clean and warehouse grains.
SELECT
    (SELECT COUNT(*) FROM clean_data.order_items) AS clean_item_rows,
    (SELECT COUNT(*) FROM warehouse.fact_order_items) AS fact_item_rows,
    (SELECT SUM(price) FROM clean_data.order_items) AS clean_item_revenue,
    (SELECT SUM(item_price) FROM warehouse.fact_order_items) AS fact_item_revenue,
    (SELECT COUNT(*) FROM warehouse.fact_order_items
     WHERE customer_key = 0 OR product_key = 0 OR seller_key = 0 OR purchase_date_key = 0
    ) AS fact_rows_with_unknown_key;

-- 8. Geolocation deduplication preserves total source occurrences.
SELECT
    COUNT(*) AS unique_normalized_rows,
    SUM(source_occurrence_count) AS represented_source_rows,
    SUM(source_occurrence_count - 1) AS collapsed_duplicate_rows
FROM clean_data.geolocation;

-- 9. Analytical outputs answering the three project questions.
SELECT *
FROM analytics.vw_category_sales
ORDER BY sales_revenue DESC
LIMIT 10;

SELECT *
FROM analytics.vw_monthly_sales
ORDER BY month_start;

SELECT *
FROM analytics.vw_state_sales
ORDER BY sales_revenue DESC;
