-- Phase 4 configurable data-quality gate metadata and default rules.
-- This script is repeatable and never modifies raw, clean, or warehouse data.

CREATE SCHEMA IF NOT EXISTS quality;

CREATE TABLE IF NOT EXISTS quality.gate_rules (
    rule_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rule_key TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('blocking', 'warning')),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    check_sql TEXT NOT NULL,
    comparison TEXT NOT NULL CHECK (comparison IN ('eq', 'le', 'ge')),
    expected_value NUMERIC NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 100,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE IF NOT EXISTS quality.gate_runs (
    gate_run_id UUID PRIMARY KEY,
    transformation_run_id UUID REFERENCES clean_data.transformation_runs(transformation_run_id),
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('running', 'passed', 'failed', 'error')),
    rules_evaluated INTEGER NOT NULL DEFAULT 0 CHECK (rules_evaluated >= 0),
    blocking_failures INTEGER NOT NULL DEFAULT 0 CHECK (blocking_failures >= 0),
    warning_failures INTEGER NOT NULL DEFAULT 0 CHECK (warning_failures >= 0),
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS quality.gate_results (
    gate_run_id UUID NOT NULL REFERENCES quality.gate_runs(gate_run_id),
    rule_id BIGINT NOT NULL REFERENCES quality.gate_rules(rule_id),
    observed_value NUMERIC NOT NULL,
    expected_value NUMERIC NOT NULL,
    comparison TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    severity TEXT NOT NULL,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (gate_run_id, rule_id)
);

CREATE INDEX IF NOT EXISTS idx_gate_runs_started
    ON quality.gate_runs (started_at DESC);
CREATE INDEX IF NOT EXISTS idx_gate_results_failures
    ON quality.gate_results (gate_run_id, passed, severity);

INSERT INTO quality.gate_rules (
    rule_key, description, severity, check_sql, comparison, expected_value, sort_order
) VALUES
(
    'latest_transformation_success',
    'The most recent transformation completed successfully.',
    'blocking',
    $$SELECT COUNT(*)::NUMERIC FROM (SELECT 1 FROM clean_data.transformation_runs WHERE status = 'success' ORDER BY finished_at DESC LIMIT 1) AS latest$$,
    'eq', 1, 10
),
(
    'expected_raw_sources',
    'Exactly nine source files have a successful ingestion run.',
    'blocking',
    $$SELECT COUNT(DISTINCT source_file)::NUMERIC FROM raw_data.ingestion_runs WHERE status = 'success'$$,
    'eq', 9, 20
),
(
    'latest_rejected_rows',
    'The latest successful transformation has no rejected source rows.',
    'blocking',
    $$SELECT rejected_records::NUMERIC FROM clean_data.transformation_runs WHERE status = 'success' ORDER BY finished_at DESC LIMIT 1$$,
    'eq', 0, 30
),
(
    'fact_grain_unique',
    'The order-item fact contains no duplicate natural grain.',
    'blocking',
    $$SELECT (COUNT(*) - COUNT(DISTINCT (order_id, order_item_id)))::NUMERIC FROM warehouse.fact_order_items$$,
    'eq', 0, 40
),
(
    'fact_row_reconciliation',
    'Clean order-item rows exactly match fact rows.',
    'blocking',
    $$SELECT ABS((SELECT COUNT(*) FROM clean_data.order_items) - (SELECT COUNT(*) FROM warehouse.fact_order_items))::NUMERIC$$,
    'eq', 0, 50
),
(
    'fact_revenue_reconciliation',
    'Clean item-price revenue exactly matches fact revenue.',
    'blocking',
    $$SELECT ABS(COALESCE((SELECT SUM(price) FROM clean_data.order_items), 0) - COALESCE((SELECT SUM(item_price) FROM warehouse.fact_order_items), 0))::NUMERIC$$,
    'eq', 0, 60
),
(
    'fact_foreign_keys_resolved',
    'Every fact row resolves to non-Unknown dimensions.',
    'blocking',
    $$SELECT COUNT(*)::NUMERIC FROM warehouse.fact_order_items WHERE customer_key = 0 OR product_key = 0 OR seller_key = 0 OR purchase_date_key = 0$$,
    'eq', 0, 70
),
(
    'fact_nonnegative_measures',
    'Fact price and freight measures are nonnegative.',
    'blocking',
    $$SELECT COUNT(*)::NUMERIC FROM warehouse.fact_order_items WHERE item_price < 0 OR freight_value < 0$$,
    'eq', 0, 80
),
(
    'geolocation_occurrence_reconciliation',
    'Normalized geolocation occurrence counts represent every selected raw row.',
    'blocking',
    $$WITH latest AS (SELECT ingestion_run_id FROM raw_data.ingestion_runs WHERE source_file = 'olist_geolocation_dataset.csv' AND status = 'success' ORDER BY finished_at DESC, ingestion_run_id DESC LIMIT 1) SELECT ABS((SELECT COUNT(*) FROM raw_data.records WHERE ingestion_run_id = (SELECT ingestion_run_id FROM latest)) - (SELECT COALESCE(SUM(source_occurrence_count), 0) FROM clean_data.geolocation))::NUMERIC$$,
    'eq', 0, 90
),
(
    'analytical_views_populated',
    'All three reporting views return at least one row.',
    'blocking',
    $$SELECT LEAST((SELECT COUNT(*) FROM analytics.vw_category_sales), (SELECT COUNT(*) FROM analytics.vw_monthly_sales), (SELECT COUNT(*) FROM analytics.vw_state_sales))::NUMERIC$$,
    'ge', 1, 100
),
(
    'delivered_revenue_positive',
    'Delivered item revenue is positive.',
    'blocking',
    $$SELECT COALESCE(SUM(item_price), 0)::NUMERIC FROM warehouse.fact_order_items WHERE order_status = 'delivered'$$,
    'ge', 1, 110
),
(
    'product_translation_gaps',
    'Untranslated product categories stay within the documented baseline threshold.',
    'warning',
    $$SELECT COUNT(*)::NUMERIC FROM clean_data.products AS p LEFT JOIN clean_data.category_translation AS t ON t.product_category_name = p.product_category_name WHERE p.product_category_name IS NOT NULL AND t.product_category_name IS NULL$$,
    'le', 13, 120
)
ON CONFLICT (rule_key) DO NOTHING;
