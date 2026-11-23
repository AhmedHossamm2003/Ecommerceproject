-- Phase 3 typed clean layer, warehouse model, and analytical views.
-- Safe to run repeatedly. Raw Phase 2 data is never dropped or modified.

CREATE SCHEMA IF NOT EXISTS clean_data;
CREATE SCHEMA IF NOT EXISTS warehouse;
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE FUNCTION clean_data.try_integer(value TEXT)
RETURNS INTEGER
LANGUAGE plpgsql
IMMUTABLE
PARALLEL SAFE
AS $$
BEGIN
    RETURN NULLIF(BTRIM(value), '')::INTEGER;
EXCEPTION WHEN invalid_text_representation OR numeric_value_out_of_range THEN
    RETURN NULL;
END;
$$;

CREATE OR REPLACE FUNCTION clean_data.try_numeric(value TEXT)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
PARALLEL SAFE
AS $$
BEGIN
    RETURN NULLIF(BTRIM(value), '')::NUMERIC;
EXCEPTION WHEN invalid_text_representation OR numeric_value_out_of_range THEN
    RETURN NULL;
END;
$$;

CREATE OR REPLACE FUNCTION clean_data.try_double(value TEXT)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
PARALLEL SAFE
AS $$
BEGIN
    RETURN NULLIF(BTRIM(value), '')::DOUBLE PRECISION;
EXCEPTION WHEN invalid_text_representation OR numeric_value_out_of_range THEN
    RETURN NULL;
END;
$$;

CREATE OR REPLACE FUNCTION clean_data.try_timestamp(value TEXT)
RETURNS TIMESTAMP WITHOUT TIME ZONE
LANGUAGE plpgsql
IMMUTABLE
PARALLEL SAFE
AS $$
BEGIN
    RETURN NULLIF(BTRIM(value), '')::TIMESTAMP WITHOUT TIME ZONE;
EXCEPTION WHEN invalid_datetime_format OR datetime_field_overflow THEN
    RETURN NULL;
END;
$$;

CREATE TABLE IF NOT EXISTS clean_data.transformation_runs (
    transformation_run_id UUID PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('running', 'success', 'failed')),
    source_ingestion_runs JSONB NOT NULL CHECK (jsonb_typeof(source_ingestion_runs) = 'object'),
    clean_records BIGINT NOT NULL DEFAULT 0 CHECK (clean_records >= 0),
    fact_records BIGINT NOT NULL DEFAULT 0 CHECK (fact_records >= 0),
    rejected_records BIGINT NOT NULL DEFAULT 0 CHECK (rejected_records >= 0),
    error_message TEXT,
    CHECK (
        (status = 'running' AND finished_at IS NULL)
        OR (status <> 'running' AND finished_at IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS clean_data.rejected_records (
    rejected_record_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id),
    raw_record_id BIGINT NOT NULL,
    source_file TEXT NOT NULL,
    source_row_number BIGINT NOT NULL,
    reason_code TEXT NOT NULL,
    reason_detail TEXT NOT NULL,
    raw_payload JSONB NOT NULL,
    rejected_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (transformation_run_id, raw_record_id)
);

CREATE TABLE IF NOT EXISTS clean_data.quality_metrics (
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id),
    metric_name TEXT NOT NULL,
    metric_value NUMERIC NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::JSONB,
    measured_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (transformation_run_id, metric_name)
);

CREATE TABLE IF NOT EXISTS clean_data.customers (
    customer_id TEXT PRIMARY KEY,
    customer_unique_id TEXT NOT NULL,
    customer_zip_code_prefix CHAR(5) NOT NULL,
    customer_city TEXT NOT NULL,
    customer_state CHAR(2) NOT NULL CHECK (customer_state ~ '^[A-Z]{2}$'),
    raw_record_id BIGINT NOT NULL UNIQUE,
    source_row_number BIGINT NOT NULL,
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id),
    cleaned_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE IF NOT EXISTS clean_data.orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES clean_data.customers (customer_id),
    order_status TEXT NOT NULL CHECK (
        order_status IN (
            'approved', 'canceled', 'created', 'delivered',
            'invoiced', 'processing', 'shipped', 'unavailable'
        )
    ),
    order_purchase_timestamp TIMESTAMP NOT NULL,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP NOT NULL,
    raw_record_id BIGINT NOT NULL UNIQUE,
    source_row_number BIGINT NOT NULL,
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id),
    cleaned_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE IF NOT EXISTS clean_data.products (
    product_id TEXT PRIMARY KEY,
    product_category_name TEXT,
    product_name_length INTEGER CHECK (product_name_length >= 0),
    product_description_length INTEGER CHECK (product_description_length >= 0),
    product_photos_quantity INTEGER CHECK (product_photos_quantity >= 0),
    product_weight_g NUMERIC CHECK (product_weight_g >= 0),
    product_length_cm NUMERIC CHECK (product_length_cm >= 0),
    product_height_cm NUMERIC CHECK (product_height_cm >= 0),
    product_width_cm NUMERIC CHECK (product_width_cm >= 0),
    raw_record_id BIGINT NOT NULL UNIQUE,
    source_row_number BIGINT NOT NULL,
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id),
    cleaned_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE IF NOT EXISTS clean_data.sellers (
    seller_id TEXT PRIMARY KEY,
    seller_zip_code_prefix CHAR(5) NOT NULL,
    seller_city TEXT NOT NULL,
    seller_state CHAR(2) NOT NULL CHECK (seller_state ~ '^[A-Z]{2}$'),
    raw_record_id BIGINT NOT NULL UNIQUE,
    source_row_number BIGINT NOT NULL,
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id),
    cleaned_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE IF NOT EXISTS clean_data.order_items (
    order_id TEXT NOT NULL REFERENCES clean_data.orders (order_id),
    order_item_id INTEGER NOT NULL CHECK (order_item_id > 0),
    product_id TEXT NOT NULL REFERENCES clean_data.products (product_id),
    seller_id TEXT NOT NULL REFERENCES clean_data.sellers (seller_id),
    shipping_limit_date TIMESTAMP NOT NULL,
    price NUMERIC(14, 2) NOT NULL CHECK (price >= 0),
    freight_value NUMERIC(14, 2) NOT NULL CHECK (freight_value >= 0),
    raw_record_id BIGINT NOT NULL UNIQUE,
    source_row_number BIGINT NOT NULL,
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id),
    cleaned_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (order_id, order_item_id)
);

CREATE TABLE IF NOT EXISTS clean_data.order_payments (
    order_id TEXT NOT NULL REFERENCES clean_data.orders (order_id),
    payment_sequential INTEGER NOT NULL CHECK (payment_sequential > 0),
    payment_type TEXT NOT NULL,
    payment_installments INTEGER NOT NULL CHECK (payment_installments >= 0),
    payment_value NUMERIC(14, 2) NOT NULL CHECK (payment_value >= 0),
    raw_record_id BIGINT NOT NULL UNIQUE,
    source_row_number BIGINT NOT NULL,
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id),
    cleaned_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (order_id, payment_sequential)
);

CREATE TABLE IF NOT EXISTS clean_data.order_reviews (
    review_id TEXT NOT NULL,
    order_id TEXT NOT NULL REFERENCES clean_data.orders (order_id),
    review_score SMALLINT NOT NULL CHECK (review_score BETWEEN 1 AND 5),
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP NOT NULL,
    review_answer_timestamp TIMESTAMP NOT NULL,
    raw_record_id BIGINT NOT NULL UNIQUE,
    source_row_number BIGINT NOT NULL,
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id),
    cleaned_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (review_id, order_id)
);

CREATE TABLE IF NOT EXISTS clean_data.category_translation (
    product_category_name TEXT PRIMARY KEY,
    product_category_name_english TEXT NOT NULL,
    raw_record_id BIGINT NOT NULL UNIQUE,
    source_row_number BIGINT NOT NULL,
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id),
    cleaned_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE IF NOT EXISTS clean_data.geolocation (
    geolocation_key BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    geolocation_zip_code_prefix CHAR(5) NOT NULL,
    geolocation_lat DOUBLE PRECISION NOT NULL CHECK (geolocation_lat BETWEEN -90 AND 90),
    geolocation_lng DOUBLE PRECISION NOT NULL CHECK (geolocation_lng BETWEEN -180 AND 180),
    geolocation_city TEXT NOT NULL,
    geolocation_state CHAR(2) NOT NULL CHECK (geolocation_state ~ '^[A-Z]{2}$'),
    source_occurrence_count INTEGER NOT NULL CHECK (source_occurrence_count > 0),
    representative_raw_record_id BIGINT NOT NULL,
    representative_source_row_number BIGINT NOT NULL,
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id),
    cleaned_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (
        geolocation_zip_code_prefix,
        geolocation_lat,
        geolocation_lng,
        geolocation_city,
        geolocation_state
    )
);

CREATE INDEX IF NOT EXISTS idx_clean_orders_customer
    ON clean_data.orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_clean_orders_purchase
    ON clean_data.orders (order_purchase_timestamp);
CREATE INDEX IF NOT EXISTS idx_clean_items_product
    ON clean_data.order_items (product_id);
CREATE INDEX IF NOT EXISTS idx_clean_items_seller
    ON clean_data.order_items (seller_id);
CREATE INDEX IF NOT EXISTS idx_clean_geolocation_zip
    ON clean_data.geolocation (geolocation_zip_code_prefix);
CREATE INDEX IF NOT EXISTS idx_rejected_records_run
    ON clean_data.rejected_records (transformation_run_id, source_file);

CREATE TABLE IF NOT EXISTS warehouse.dim_customers (
    customer_key BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE,
    customer_unique_id TEXT NOT NULL,
    customer_city TEXT NOT NULL,
    customer_state CHAR(2) NOT NULL,
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id)
);

CREATE TABLE IF NOT EXISTS warehouse.dim_products (
    product_key BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    product_id TEXT NOT NULL UNIQUE,
    product_category_name TEXT NOT NULL,
    product_category_name_english TEXT NOT NULL,
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id)
);

CREATE TABLE IF NOT EXISTS warehouse.dim_sellers (
    seller_key BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    seller_id TEXT NOT NULL UNIQUE,
    seller_city TEXT NOT NULL,
    seller_state CHAR(2) NOT NULL,
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id)
);

CREATE TABLE IF NOT EXISTS warehouse.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day SMALLINT NOT NULL,
    month SMALLINT NOT NULL,
    month_name TEXT NOT NULL,
    quarter SMALLINT NOT NULL,
    year SMALLINT NOT NULL,
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id)
);

CREATE TABLE IF NOT EXISTS warehouse.fact_order_items (
    order_item_key BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    order_id TEXT NOT NULL,
    order_item_id INTEGER NOT NULL,
    customer_key BIGINT NOT NULL REFERENCES warehouse.dim_customers (customer_key),
    product_key BIGINT NOT NULL REFERENCES warehouse.dim_products (product_key),
    seller_key BIGINT NOT NULL REFERENCES warehouse.dim_sellers (seller_key),
    purchase_date_key INTEGER NOT NULL REFERENCES warehouse.dim_date (date_key),
    order_status TEXT NOT NULL,
    order_purchase_timestamp TIMESTAMP NOT NULL,
    item_price NUMERIC(14, 2) NOT NULL CHECK (item_price >= 0),
    freight_value NUMERIC(14, 2) NOT NULL CHECK (freight_value >= 0),
    gross_item_value NUMERIC(14, 2)
        GENERATED ALWAYS AS (item_price + freight_value) STORED,
    transformation_run_id UUID NOT NULL
        REFERENCES clean_data.transformation_runs (transformation_run_id),
    UNIQUE (order_id, order_item_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_purchase_date
    ON warehouse.fact_order_items (purchase_date_key);
CREATE INDEX IF NOT EXISTS idx_fact_customer
    ON warehouse.fact_order_items (customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_product
    ON warehouse.fact_order_items (product_key);
CREATE INDEX IF NOT EXISTS idx_fact_seller
    ON warehouse.fact_order_items (seller_key);
CREATE INDEX IF NOT EXISTS idx_fact_status
    ON warehouse.fact_order_items (order_status);

CREATE OR REPLACE VIEW analytics.vw_category_sales AS
WITH category_totals AS (
    SELECT
        products.product_category_name_english AS product_category,
        COUNT(*) AS item_count,
        COUNT(DISTINCT facts.order_id) AS order_count,
        SUM(facts.item_price)::NUMERIC(16, 2) AS sales_revenue,
        SUM(facts.freight_value)::NUMERIC(16, 2) AS freight_value
    FROM warehouse.fact_order_items AS facts
    JOIN warehouse.dim_products AS products
        ON products.product_key = facts.product_key
    WHERE facts.order_status = 'delivered'
    GROUP BY products.product_category_name_english
)
SELECT
    product_category,
    item_count,
    order_count,
    sales_revenue,
    freight_value,
    ROUND(
        100 * sales_revenue / NULLIF(SUM(sales_revenue) OVER (), 0),
        2
    ) AS revenue_percentage
FROM category_totals;

CREATE OR REPLACE VIEW analytics.vw_monthly_sales AS
WITH month_spine AS (
    SELECT DISTINCT DATE_TRUNC('month', full_date)::DATE AS month_start
    FROM warehouse.dim_date
    WHERE date_key <> 0
),
monthly_facts AS (
    SELECT
        DATE_TRUNC('month', order_purchase_timestamp)::DATE AS month_start,
        COUNT(*) AS item_count,
        COUNT(DISTINCT order_id) AS order_count,
        SUM(item_price)::NUMERIC(16, 2) AS sales_revenue,
        SUM(freight_value)::NUMERIC(16, 2) AS freight_value
    FROM warehouse.fact_order_items
    WHERE order_status = 'delivered'
    GROUP BY DATE_TRUNC('month', order_purchase_timestamp)::DATE
)
SELECT
    spine.month_start,
    COALESCE(facts.item_count, 0) AS item_count,
    COALESCE(facts.order_count, 0) AS order_count,
    COALESCE(facts.sales_revenue, 0)::NUMERIC(16, 2) AS sales_revenue,
    COALESCE(facts.freight_value, 0)::NUMERIC(16, 2) AS freight_value
FROM month_spine AS spine
LEFT JOIN monthly_facts AS facts USING (month_start);

CREATE OR REPLACE VIEW analytics.vw_state_sales AS
WITH state_totals AS (
    SELECT
        customers.customer_state,
        COUNT(*) AS item_count,
        COUNT(DISTINCT facts.order_id) AS order_count,
        SUM(facts.item_price)::NUMERIC(16, 2) AS sales_revenue,
        SUM(facts.freight_value)::NUMERIC(16, 2) AS freight_value
    FROM warehouse.fact_order_items AS facts
    JOIN warehouse.dim_customers AS customers
        ON customers.customer_key = facts.customer_key
    WHERE facts.order_status = 'delivered'
    GROUP BY customers.customer_state
)
SELECT
    customer_state,
    item_count,
    order_count,
    sales_revenue,
    freight_value,
    ROUND(
        100 * sales_revenue / NULLIF(SUM(sales_revenue) OVER (), 0),
        2
    ) AS revenue_percentage
FROM state_totals;

COMMENT ON SCHEMA clean_data IS
    'Phase 3 typed source-aligned tables, reject lineage, and measured quality results.';
COMMENT ON SCHEMA warehouse IS
    'Phase 3 star schema at one order-item line per fact row.';
COMMENT ON SCHEMA analytics IS
    'Phase 3 views for category, monthly, and state sales questions.';
