-- Idempotent Phase 3 rebuild from the latest successful Phase 2 run per file.
-- The caller must set transaction-local setting phase3.run_id to a UUID.

TRUNCATE TABLE
    warehouse.fact_order_items,
    warehouse.dim_customers,
    warehouse.dim_products,
    warehouse.dim_sellers,
    warehouse.dim_date,
    clean_data.order_items,
    clean_data.order_payments,
    clean_data.order_reviews,
    clean_data.orders,
    clean_data.customers,
    clean_data.products,
    clean_data.sellers,
    clean_data.geolocation,
    clean_data.category_translation
RESTART IDENTITY;

CREATE TEMP TABLE selected_raw_records ON COMMIT DROP AS
WITH latest_runs AS (
    SELECT DISTINCT ON (source_file)
        source_file,
        ingestion_run_id
    FROM raw_data.ingestion_runs
    WHERE status = 'success'
    ORDER BY source_file, finished_at DESC, ingestion_run_id DESC
)
SELECT
    records.raw_record_id,
    records.ingestion_run_id,
    records.source_file,
    records.source_row_number,
    records.raw_payload
FROM raw_data.records AS records
JOIN latest_runs
    ON latest_runs.ingestion_run_id = records.ingestion_run_id;

CREATE INDEX ON selected_raw_records (source_file, raw_record_id);

-- Required-field, domain, and type rejects. Optional missing values remain valid.
WITH candidates AS (
    SELECT
        raw_record_id,
        source_file,
        source_row_number,
        raw_payload,
        'invalid_customer'::TEXT AS reason_code,
        'Required customer identifier, postcode, city, or state is invalid.'::TEXT AS reason_detail
    FROM selected_raw_records
    WHERE source_file = 'olist_customers_dataset.csv'
      AND (
          NULLIF(BTRIM(raw_payload ->> 'customer_id'), '') IS NULL
          OR NULLIF(BTRIM(raw_payload ->> 'customer_unique_id'), '') IS NULL
          OR BTRIM(raw_payload ->> 'customer_zip_code_prefix') !~ '^\d{1,5}$'
          OR NULLIF(BTRIM(raw_payload ->> 'customer_city'), '') IS NULL
          OR UPPER(BTRIM(raw_payload ->> 'customer_state')) !~ '^[A-Z]{2}$'
      )

    UNION ALL
    SELECT raw_record_id, source_file, source_row_number, raw_payload,
           'invalid_order',
           'Required order identifier, status, purchase date, or estimated date is invalid.'
    FROM selected_raw_records
    WHERE source_file = 'olist_orders_dataset.csv'
      AND (
          NULLIF(BTRIM(raw_payload ->> 'order_id'), '') IS NULL
          OR NULLIF(BTRIM(raw_payload ->> 'customer_id'), '') IS NULL
          OR BTRIM(raw_payload ->> 'order_status') NOT IN (
              'approved', 'canceled', 'created', 'delivered',
              'invoiced', 'processing', 'shipped', 'unavailable'
          )
          OR clean_data.try_timestamp(raw_payload ->> 'order_purchase_timestamp') IS NULL
          OR clean_data.try_timestamp(raw_payload ->> 'order_estimated_delivery_date') IS NULL
          OR (
              NULLIF(BTRIM(raw_payload ->> 'order_approved_at'), '') IS NOT NULL
              AND clean_data.try_timestamp(raw_payload ->> 'order_approved_at') IS NULL
          )
          OR (
              NULLIF(BTRIM(raw_payload ->> 'order_delivered_carrier_date'), '') IS NOT NULL
              AND clean_data.try_timestamp(raw_payload ->> 'order_delivered_carrier_date') IS NULL
          )
          OR (
              NULLIF(BTRIM(raw_payload ->> 'order_delivered_customer_date'), '') IS NOT NULL
              AND clean_data.try_timestamp(raw_payload ->> 'order_delivered_customer_date') IS NULL
          )
      )

    UNION ALL
    SELECT raw_record_id, source_file, source_row_number, raw_payload,
           'invalid_order_item',
           'Required item identifiers, date, price, or freight value is invalid.'
    FROM selected_raw_records
    WHERE source_file = 'olist_order_items_dataset.csv'
      AND (
          NULLIF(BTRIM(raw_payload ->> 'order_id'), '') IS NULL
          OR COALESCE(clean_data.try_integer(raw_payload ->> 'order_item_id'), 0) <= 0
          OR NULLIF(BTRIM(raw_payload ->> 'product_id'), '') IS NULL
          OR NULLIF(BTRIM(raw_payload ->> 'seller_id'), '') IS NULL
          OR clean_data.try_timestamp(raw_payload ->> 'shipping_limit_date') IS NULL
          OR COALESCE(clean_data.try_numeric(raw_payload ->> 'price'), -1) < 0
          OR COALESCE(clean_data.try_numeric(raw_payload ->> 'freight_value'), -1) < 0
      )

    UNION ALL
    SELECT raw_record_id, source_file, source_row_number, raw_payload,
           'invalid_product',
           'Product identifier or an optional numeric product attribute is invalid.'
    FROM selected_raw_records
    WHERE source_file = 'olist_products_dataset.csv'
      AND (
          NULLIF(BTRIM(raw_payload ->> 'product_id'), '') IS NULL
          OR (
              NULLIF(BTRIM(raw_payload ->> 'product_name_lenght'), '') IS NOT NULL
              AND COALESCE(clean_data.try_integer(raw_payload ->> 'product_name_lenght'), -1) < 0
          )
          OR (
              NULLIF(BTRIM(raw_payload ->> 'product_description_lenght'), '') IS NOT NULL
              AND COALESCE(clean_data.try_integer(raw_payload ->> 'product_description_lenght'), -1) < 0
          )
          OR (
              NULLIF(BTRIM(raw_payload ->> 'product_photos_qty'), '') IS NOT NULL
              AND COALESCE(clean_data.try_integer(raw_payload ->> 'product_photos_qty'), -1) < 0
          )
          OR (
              NULLIF(BTRIM(raw_payload ->> 'product_weight_g'), '') IS NOT NULL
              AND COALESCE(clean_data.try_numeric(raw_payload ->> 'product_weight_g'), -1) < 0
          )
          OR (
              NULLIF(BTRIM(raw_payload ->> 'product_length_cm'), '') IS NOT NULL
              AND COALESCE(clean_data.try_numeric(raw_payload ->> 'product_length_cm'), -1) < 0
          )
          OR (
              NULLIF(BTRIM(raw_payload ->> 'product_height_cm'), '') IS NOT NULL
              AND COALESCE(clean_data.try_numeric(raw_payload ->> 'product_height_cm'), -1) < 0
          )
          OR (
              NULLIF(BTRIM(raw_payload ->> 'product_width_cm'), '') IS NOT NULL
              AND COALESCE(clean_data.try_numeric(raw_payload ->> 'product_width_cm'), -1) < 0
          )
      )

    UNION ALL
    SELECT raw_record_id, source_file, source_row_number, raw_payload,
           'invalid_seller',
           'Required seller identifier, postcode, city, or state is invalid.'
    FROM selected_raw_records
    WHERE source_file = 'olist_sellers_dataset.csv'
      AND (
          NULLIF(BTRIM(raw_payload ->> 'seller_id'), '') IS NULL
          OR BTRIM(raw_payload ->> 'seller_zip_code_prefix') !~ '^\d{1,5}$'
          OR NULLIF(BTRIM(raw_payload ->> 'seller_city'), '') IS NULL
          OR UPPER(BTRIM(raw_payload ->> 'seller_state')) !~ '^[A-Z]{2}$'
      )

    UNION ALL
    SELECT raw_record_id, source_file, source_row_number, raw_payload,
           'invalid_payment',
           'Required payment identifier, sequence, installments, or value is invalid.'
    FROM selected_raw_records
    WHERE source_file = 'olist_order_payments_dataset.csv'
      AND (
          NULLIF(BTRIM(raw_payload ->> 'order_id'), '') IS NULL
          OR COALESCE(clean_data.try_integer(raw_payload ->> 'payment_sequential'), 0) <= 0
          OR NULLIF(BTRIM(raw_payload ->> 'payment_type'), '') IS NULL
          OR COALESCE(clean_data.try_integer(raw_payload ->> 'payment_installments'), -1) < 0
          OR COALESCE(clean_data.try_numeric(raw_payload ->> 'payment_value'), -1) < 0
      )

    UNION ALL
    SELECT raw_record_id, source_file, source_row_number, raw_payload,
           'invalid_review',
           'Required review identifiers, score, or timestamps are invalid.'
    FROM selected_raw_records
    WHERE source_file = 'olist_order_reviews_dataset.csv'
      AND (
          NULLIF(BTRIM(raw_payload ->> 'review_id'), '') IS NULL
          OR NULLIF(BTRIM(raw_payload ->> 'order_id'), '') IS NULL
          OR COALESCE(clean_data.try_integer(raw_payload ->> 'review_score'), 0) NOT BETWEEN 1 AND 5
          OR clean_data.try_timestamp(raw_payload ->> 'review_creation_date') IS NULL
          OR clean_data.try_timestamp(raw_payload ->> 'review_answer_timestamp') IS NULL
      )

    UNION ALL
    SELECT raw_record_id, source_file, source_row_number, raw_payload,
           'invalid_category_translation',
           'Category translation requires both source and English names.'
    FROM selected_raw_records
    WHERE source_file = 'product_category_name_translation.csv'
      AND (
          NULLIF(BTRIM(raw_payload ->> 'product_category_name'), '') IS NULL
          OR NULLIF(BTRIM(raw_payload ->> 'product_category_name_english'), '') IS NULL
      )

    UNION ALL
    SELECT raw_record_id, source_file, source_row_number, raw_payload,
           'invalid_geolocation',
           'Required geolocation postcode, coordinates, city, or state is invalid.'
    FROM selected_raw_records
    WHERE source_file = 'olist_geolocation_dataset.csv'
      AND (
          BTRIM(raw_payload ->> 'geolocation_zip_code_prefix') !~ '^\d{1,5}$'
          OR COALESCE(clean_data.try_double(raw_payload ->> 'geolocation_lat'), 999) NOT BETWEEN -90 AND 90
          OR COALESCE(clean_data.try_double(raw_payload ->> 'geolocation_lng'), 999) NOT BETWEEN -180 AND 180
          OR NULLIF(BTRIM(raw_payload ->> 'geolocation_city'), '') IS NULL
          OR UPPER(BTRIM(raw_payload ->> 'geolocation_state')) !~ '^[A-Z]{2}$'
      )
)
INSERT INTO clean_data.rejected_records (
    transformation_run_id,
    raw_record_id,
    source_file,
    source_row_number,
    reason_code,
    reason_detail,
    raw_payload
)
SELECT
    current_setting('phase3.run_id')::UUID,
    raw_record_id,
    source_file,
    source_row_number,
    reason_code,
    reason_detail,
    raw_payload
FROM candidates;

INSERT INTO clean_data.customers (
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    raw_record_id,
    source_row_number,
    transformation_run_id
)
SELECT
    BTRIM(raw_payload ->> 'customer_id'),
    BTRIM(raw_payload ->> 'customer_unique_id'),
    LPAD(BTRIM(raw_payload ->> 'customer_zip_code_prefix'), 5, '0'),
    BTRIM(raw_payload ->> 'customer_city'),
    UPPER(BTRIM(raw_payload ->> 'customer_state')),
    raw_record_id,
    source_row_number,
    current_setting('phase3.run_id')::UUID
FROM selected_raw_records AS records
WHERE source_file = 'olist_customers_dataset.csv'
  AND NOT EXISTS (
      SELECT 1 FROM clean_data.rejected_records AS rejected
      WHERE rejected.transformation_run_id = current_setting('phase3.run_id')::UUID
        AND rejected.raw_record_id = records.raw_record_id
  )
ORDER BY source_row_number;

INSERT INTO clean_data.products (
    product_id,
    product_category_name,
    product_name_length,
    product_description_length,
    product_photos_quantity,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,
    raw_record_id,
    source_row_number,
    transformation_run_id
)
SELECT
    BTRIM(raw_payload ->> 'product_id'),
    NULLIF(BTRIM(raw_payload ->> 'product_category_name'), ''),
    clean_data.try_integer(raw_payload ->> 'product_name_lenght'),
    clean_data.try_integer(raw_payload ->> 'product_description_lenght'),
    clean_data.try_integer(raw_payload ->> 'product_photos_qty'),
    clean_data.try_numeric(raw_payload ->> 'product_weight_g'),
    clean_data.try_numeric(raw_payload ->> 'product_length_cm'),
    clean_data.try_numeric(raw_payload ->> 'product_height_cm'),
    clean_data.try_numeric(raw_payload ->> 'product_width_cm'),
    raw_record_id,
    source_row_number,
    current_setting('phase3.run_id')::UUID
FROM selected_raw_records AS records
WHERE source_file = 'olist_products_dataset.csv'
  AND NOT EXISTS (
      SELECT 1 FROM clean_data.rejected_records AS rejected
      WHERE rejected.transformation_run_id = current_setting('phase3.run_id')::UUID
        AND rejected.raw_record_id = records.raw_record_id
  )
ORDER BY source_row_number;

INSERT INTO clean_data.sellers (
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state,
    raw_record_id,
    source_row_number,
    transformation_run_id
)
SELECT
    BTRIM(raw_payload ->> 'seller_id'),
    LPAD(BTRIM(raw_payload ->> 'seller_zip_code_prefix'), 5, '0'),
    BTRIM(raw_payload ->> 'seller_city'),
    UPPER(BTRIM(raw_payload ->> 'seller_state')),
    raw_record_id,
    source_row_number,
    current_setting('phase3.run_id')::UUID
FROM selected_raw_records AS records
WHERE source_file = 'olist_sellers_dataset.csv'
  AND NOT EXISTS (
      SELECT 1 FROM clean_data.rejected_records AS rejected
      WHERE rejected.transformation_run_id = current_setting('phase3.run_id')::UUID
        AND rejected.raw_record_id = records.raw_record_id
  )
ORDER BY source_row_number;

INSERT INTO clean_data.category_translation (
    product_category_name,
    product_category_name_english,
    raw_record_id,
    source_row_number,
    transformation_run_id
)
SELECT
    BTRIM(raw_payload ->> 'product_category_name'),
    BTRIM(raw_payload ->> 'product_category_name_english'),
    raw_record_id,
    source_row_number,
    current_setting('phase3.run_id')::UUID
FROM selected_raw_records AS records
WHERE source_file = 'product_category_name_translation.csv'
  AND NOT EXISTS (
      SELECT 1 FROM clean_data.rejected_records AS rejected
      WHERE rejected.transformation_run_id = current_setting('phase3.run_id')::UUID
        AND rejected.raw_record_id = records.raw_record_id
  )
ORDER BY source_row_number;

-- Referential rejects are identified after valid parent rows are available.
INSERT INTO clean_data.rejected_records (
    transformation_run_id, raw_record_id, source_file, source_row_number,
    reason_code, reason_detail, raw_payload
)
SELECT
    current_setting('phase3.run_id')::UUID,
    records.raw_record_id,
    records.source_file,
    records.source_row_number,
    'unmatched_customer',
    'The order customer_id does not match a valid clean customer.',
    records.raw_payload
FROM selected_raw_records AS records
WHERE records.source_file = 'olist_orders_dataset.csv'
  AND NOT EXISTS (
      SELECT 1 FROM clean_data.rejected_records AS rejected
      WHERE rejected.transformation_run_id = current_setting('phase3.run_id')::UUID
        AND rejected.raw_record_id = records.raw_record_id
  )
  AND NOT EXISTS (
      SELECT 1 FROM clean_data.customers AS customers
      WHERE customers.customer_id = BTRIM(records.raw_payload ->> 'customer_id')
  );

INSERT INTO clean_data.orders (
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    raw_record_id,
    source_row_number,
    transformation_run_id
)
SELECT
    BTRIM(raw_payload ->> 'order_id'),
    BTRIM(raw_payload ->> 'customer_id'),
    BTRIM(raw_payload ->> 'order_status'),
    clean_data.try_timestamp(raw_payload ->> 'order_purchase_timestamp'),
    clean_data.try_timestamp(raw_payload ->> 'order_approved_at'),
    clean_data.try_timestamp(raw_payload ->> 'order_delivered_carrier_date'),
    clean_data.try_timestamp(raw_payload ->> 'order_delivered_customer_date'),
    clean_data.try_timestamp(raw_payload ->> 'order_estimated_delivery_date'),
    raw_record_id,
    source_row_number,
    current_setting('phase3.run_id')::UUID
FROM selected_raw_records AS records
WHERE source_file = 'olist_orders_dataset.csv'
  AND NOT EXISTS (
      SELECT 1 FROM clean_data.rejected_records AS rejected
      WHERE rejected.transformation_run_id = current_setting('phase3.run_id')::UUID
        AND rejected.raw_record_id = records.raw_record_id
  )
ORDER BY source_row_number;

WITH child_candidates AS (
    SELECT
        records.*,
        CASE
            WHEN records.source_file = 'olist_order_items_dataset.csv'
                 AND NOT EXISTS (
                     SELECT 1 FROM clean_data.orders
                     WHERE order_id = BTRIM(records.raw_payload ->> 'order_id')
                 ) THEN 'unmatched_order'
            WHEN records.source_file = 'olist_order_items_dataset.csv'
                 AND NOT EXISTS (
                     SELECT 1 FROM clean_data.products
                     WHERE product_id = BTRIM(records.raw_payload ->> 'product_id')
                 ) THEN 'unmatched_product'
            WHEN records.source_file = 'olist_order_items_dataset.csv'
                 AND NOT EXISTS (
                     SELECT 1 FROM clean_data.sellers
                     WHERE seller_id = BTRIM(records.raw_payload ->> 'seller_id')
                 ) THEN 'unmatched_seller'
            WHEN records.source_file IN (
                    'olist_order_payments_dataset.csv',
                    'olist_order_reviews_dataset.csv'
                 )
                 AND NOT EXISTS (
                     SELECT 1 FROM clean_data.orders
                     WHERE order_id = BTRIM(records.raw_payload ->> 'order_id')
                 ) THEN 'unmatched_order'
        END AS reason_code
    FROM selected_raw_records AS records
    WHERE records.source_file IN (
        'olist_order_items_dataset.csv',
        'olist_order_payments_dataset.csv',
        'olist_order_reviews_dataset.csv'
    )
      AND NOT EXISTS (
          SELECT 1 FROM clean_data.rejected_records AS rejected
          WHERE rejected.transformation_run_id = current_setting('phase3.run_id')::UUID
            AND rejected.raw_record_id = records.raw_record_id
      )
)
INSERT INTO clean_data.rejected_records (
    transformation_run_id, raw_record_id, source_file, source_row_number,
    reason_code, reason_detail, raw_payload
)
SELECT
    current_setting('phase3.run_id')::UUID,
    raw_record_id,
    source_file,
    source_row_number,
    reason_code,
    'A required parent key does not exist in the clean layer.',
    raw_payload
FROM child_candidates
WHERE reason_code IS NOT NULL;

INSERT INTO clean_data.order_items (
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value,
    raw_record_id,
    source_row_number,
    transformation_run_id
)
SELECT
    BTRIM(raw_payload ->> 'order_id'),
    clean_data.try_integer(raw_payload ->> 'order_item_id'),
    BTRIM(raw_payload ->> 'product_id'),
    BTRIM(raw_payload ->> 'seller_id'),
    clean_data.try_timestamp(raw_payload ->> 'shipping_limit_date'),
    clean_data.try_numeric(raw_payload ->> 'price'),
    clean_data.try_numeric(raw_payload ->> 'freight_value'),
    raw_record_id,
    source_row_number,
    current_setting('phase3.run_id')::UUID
FROM selected_raw_records AS records
WHERE source_file = 'olist_order_items_dataset.csv'
  AND NOT EXISTS (
      SELECT 1 FROM clean_data.rejected_records AS rejected
      WHERE rejected.transformation_run_id = current_setting('phase3.run_id')::UUID
        AND rejected.raw_record_id = records.raw_record_id
  )
ORDER BY source_row_number;

INSERT INTO clean_data.order_payments (
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value,
    raw_record_id,
    source_row_number,
    transformation_run_id
)
SELECT
    BTRIM(raw_payload ->> 'order_id'),
    clean_data.try_integer(raw_payload ->> 'payment_sequential'),
    BTRIM(raw_payload ->> 'payment_type'),
    clean_data.try_integer(raw_payload ->> 'payment_installments'),
    clean_data.try_numeric(raw_payload ->> 'payment_value'),
    raw_record_id,
    source_row_number,
    current_setting('phase3.run_id')::UUID
FROM selected_raw_records AS records
WHERE source_file = 'olist_order_payments_dataset.csv'
  AND NOT EXISTS (
      SELECT 1 FROM clean_data.rejected_records AS rejected
      WHERE rejected.transformation_run_id = current_setting('phase3.run_id')::UUID
        AND rejected.raw_record_id = records.raw_record_id
  )
ORDER BY source_row_number;

INSERT INTO clean_data.order_reviews (
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date,
    review_answer_timestamp,
    raw_record_id,
    source_row_number,
    transformation_run_id
)
SELECT
    BTRIM(raw_payload ->> 'review_id'),
    BTRIM(raw_payload ->> 'order_id'),
    clean_data.try_integer(raw_payload ->> 'review_score')::SMALLINT,
    NULLIF(BTRIM(raw_payload ->> 'review_comment_title'), ''),
    NULLIF(BTRIM(raw_payload ->> 'review_comment_message'), ''),
    clean_data.try_timestamp(raw_payload ->> 'review_creation_date'),
    clean_data.try_timestamp(raw_payload ->> 'review_answer_timestamp'),
    raw_record_id,
    source_row_number,
    current_setting('phase3.run_id')::UUID
FROM selected_raw_records AS records
WHERE source_file = 'olist_order_reviews_dataset.csv'
  AND NOT EXISTS (
      SELECT 1 FROM clean_data.rejected_records AS rejected
      WHERE rejected.transformation_run_id = current_setting('phase3.run_id')::UUID
        AND rejected.raw_record_id = records.raw_record_id
  )
ORDER BY source_row_number;

WITH normalized AS (
    SELECT
        LPAD(BTRIM(raw_payload ->> 'geolocation_zip_code_prefix'), 5, '0') AS zip_code,
        clean_data.try_double(raw_payload ->> 'geolocation_lat') AS latitude,
        clean_data.try_double(raw_payload ->> 'geolocation_lng') AS longitude,
        BTRIM(raw_payload ->> 'geolocation_city') AS city,
        UPPER(BTRIM(raw_payload ->> 'geolocation_state')) AS state,
        raw_record_id,
        source_row_number
    FROM selected_raw_records AS records
    WHERE source_file = 'olist_geolocation_dataset.csv'
      AND NOT EXISTS (
          SELECT 1 FROM clean_data.rejected_records AS rejected
          WHERE rejected.transformation_run_id = current_setting('phase3.run_id')::UUID
            AND rejected.raw_record_id = records.raw_record_id
      )
)
INSERT INTO clean_data.geolocation (
    geolocation_zip_code_prefix,
    geolocation_lat,
    geolocation_lng,
    geolocation_city,
    geolocation_state,
    source_occurrence_count,
    representative_raw_record_id,
    representative_source_row_number,
    transformation_run_id
)
SELECT
    zip_code,
    latitude,
    longitude,
    city,
    state,
    COUNT(*)::INTEGER,
    MIN(raw_record_id),
    MIN(source_row_number),
    current_setting('phase3.run_id')::UUID
FROM normalized
GROUP BY zip_code, latitude, longitude, city, state
ORDER BY zip_code, latitude, longitude, city, state;

-- Build the warehouse with deterministic keys and explicit unknown members.
INSERT INTO warehouse.dim_customers (
    customer_key, customer_id, customer_unique_id, customer_city,
    customer_state, transformation_run_id
)
VALUES (
    0, 'Unknown', 'Unknown', 'Unknown', 'UN',
    current_setting('phase3.run_id')::UUID
);

INSERT INTO warehouse.dim_customers (
    customer_id, customer_unique_id, customer_city,
    customer_state, transformation_run_id
)
SELECT
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state,
    current_setting('phase3.run_id')::UUID
FROM clean_data.customers
ORDER BY customer_id;

INSERT INTO warehouse.dim_products (
    product_key, product_id, product_category_name,
    product_category_name_english, transformation_run_id
)
VALUES (
    0, 'Unknown', 'Unknown', 'Unknown',
    current_setting('phase3.run_id')::UUID
);

INSERT INTO warehouse.dim_products (
    product_id, product_category_name,
    product_category_name_english, transformation_run_id
)
SELECT
    products.product_id,
    COALESCE(products.product_category_name, 'Unknown'),
    COALESCE(translations.product_category_name_english, 'Unknown'),
    current_setting('phase3.run_id')::UUID
FROM clean_data.products AS products
LEFT JOIN clean_data.category_translation AS translations
    ON translations.product_category_name = products.product_category_name
ORDER BY products.product_id;

INSERT INTO warehouse.dim_sellers (
    seller_key, seller_id, seller_city, seller_state, transformation_run_id
)
VALUES (
    0, 'Unknown', 'Unknown', 'UN',
    current_setting('phase3.run_id')::UUID
);

INSERT INTO warehouse.dim_sellers (
    seller_id, seller_city, seller_state, transformation_run_id
)
SELECT
    seller_id,
    seller_city,
    seller_state,
    current_setting('phase3.run_id')::UUID
FROM clean_data.sellers
ORDER BY seller_id;

INSERT INTO warehouse.dim_date (
    date_key, full_date, day, month, month_name, quarter, year,
    transformation_run_id
)
VALUES (
    0, DATE '1900-01-01', 1, 1, 'Unknown', 1, 1900,
    current_setting('phase3.run_id')::UUID
);

INSERT INTO warehouse.dim_date (
    date_key, full_date, day, month, month_name, quarter, year,
    transformation_run_id
)
SELECT
    TO_CHAR(calendar_date, 'YYYYMMDD')::INTEGER,
    calendar_date,
    EXTRACT(DAY FROM calendar_date)::SMALLINT,
    EXTRACT(MONTH FROM calendar_date)::SMALLINT,
    TO_CHAR(calendar_date, 'FMMonth'),
    EXTRACT(QUARTER FROM calendar_date)::SMALLINT,
    EXTRACT(YEAR FROM calendar_date)::SMALLINT,
    current_setting('phase3.run_id')::UUID
FROM GENERATE_SERIES(
    (SELECT MIN(order_purchase_timestamp)::DATE FROM clean_data.orders),
    (SELECT MAX(order_purchase_timestamp)::DATE FROM clean_data.orders),
    INTERVAL '1 day'
) AS dates(calendar_date)
ORDER BY calendar_date;

INSERT INTO warehouse.fact_order_items (
    order_id,
    order_item_id,
    customer_key,
    product_key,
    seller_key,
    purchase_date_key,
    order_status,
    order_purchase_timestamp,
    item_price,
    freight_value,
    transformation_run_id
)
SELECT
    items.order_id,
    items.order_item_id,
    COALESCE(customers.customer_key, 0),
    COALESCE(products.product_key, 0),
    COALESCE(sellers.seller_key, 0),
    COALESCE(dates.date_key, 0),
    orders.order_status,
    orders.order_purchase_timestamp,
    items.price,
    items.freight_value,
    current_setting('phase3.run_id')::UUID
FROM clean_data.order_items AS items
JOIN clean_data.orders AS orders USING (order_id)
LEFT JOIN warehouse.dim_customers AS customers
    ON customers.customer_id = orders.customer_id
LEFT JOIN warehouse.dim_products AS products
    ON products.product_id = items.product_id
LEFT JOIN warehouse.dim_sellers AS sellers
    ON sellers.seller_id = items.seller_id
LEFT JOIN warehouse.dim_date AS dates
    ON dates.full_date = orders.order_purchase_timestamp::DATE
ORDER BY items.order_id, items.order_item_id;

INSERT INTO clean_data.quality_metrics (
    transformation_run_id, metric_name, metric_value, details
)
VALUES
    (
        current_setting('phase3.run_id')::UUID,
        'raw_selected_rows',
        (SELECT COUNT(*) FROM selected_raw_records),
        '{}'::JSONB
    ),
    (
        current_setting('phase3.run_id')::UUID,
        'rejected_rows',
        (
            SELECT COUNT(*) FROM clean_data.rejected_records
            WHERE transformation_run_id = current_setting('phase3.run_id')::UUID
        ),
        '{}'::JSONB
    ),
    (
        current_setting('phase3.run_id')::UUID,
        'geolocation_rows_collapsed',
        (
            SELECT COUNT(*) FROM selected_raw_records
            WHERE source_file = 'olist_geolocation_dataset.csv'
        ) - (SELECT COUNT(*) FROM clean_data.geolocation),
        '{"rule":"trim fields then collapse identical normalized rows"}'::JSONB
    ),
    (
        current_setting('phase3.run_id')::UUID,
        'products_missing_category',
        (SELECT COUNT(*) FROM clean_data.products WHERE product_category_name IS NULL),
        '{}'::JSONB
    ),
    (
        current_setting('phase3.run_id')::UUID,
        'products_unmatched_translation',
        (
            SELECT COUNT(*)
            FROM clean_data.products AS products
            LEFT JOIN clean_data.category_translation AS translations
                ON translations.product_category_name = products.product_category_name
            WHERE products.product_category_name IS NOT NULL
              AND translations.product_category_name IS NULL
        ),
        '{}'::JSONB
    ),
    (
        current_setting('phase3.run_id')::UUID,
        'reviews_missing_title',
        (SELECT COUNT(*) FROM clean_data.order_reviews WHERE review_comment_title IS NULL),
        '{}'::JSONB
    ),
    (
        current_setting('phase3.run_id')::UUID,
        'reviews_missing_message',
        (SELECT COUNT(*) FROM clean_data.order_reviews WHERE review_comment_message IS NULL),
        '{}'::JSONB
    ),
    (
        current_setting('phase3.run_id')::UUID,
        'zero_installment_payments',
        (SELECT COUNT(*) FROM clean_data.order_payments WHERE payment_installments = 0),
        '{}'::JSONB
    ),
    (
        current_setting('phase3.run_id')::UUID,
        'fact_order_item_rows',
        (SELECT COUNT(*) FROM warehouse.fact_order_items),
        '{}'::JSONB
    ),
    (
        current_setting('phase3.run_id')::UUID,
        'fact_unknown_dimension_keys',
        (
            SELECT COUNT(*)
            FROM warehouse.fact_order_items
            WHERE customer_key = 0 OR product_key = 0 OR seller_key = 0 OR purchase_date_key = 0
        ),
        '{}'::JSONB
    );

-- Transaction-failing reconciliation guards prevent a false successful run.
DO $$
DECLARE
    clean_item_count BIGINT;
    fact_item_count BIGINT;
    clean_revenue NUMERIC;
    fact_revenue NUMERIC;
    geolocation_source_count BIGINT;
    geolocation_occurrence_count BIGINT;
BEGIN
    SELECT COUNT(*), COALESCE(SUM(price), 0)
    INTO clean_item_count, clean_revenue
    FROM clean_data.order_items;

    SELECT COUNT(*), COALESCE(SUM(item_price), 0)
    INTO fact_item_count, fact_revenue
    FROM warehouse.fact_order_items;

    IF clean_item_count <> fact_item_count THEN
        RAISE EXCEPTION 'Fact row reconciliation failed: clean %, fact %',
            clean_item_count, fact_item_count;
    END IF;

    IF clean_revenue <> fact_revenue THEN
        RAISE EXCEPTION 'Fact revenue reconciliation failed: clean %, fact %',
            clean_revenue, fact_revenue;
    END IF;

    SELECT COUNT(*) INTO geolocation_source_count
    FROM selected_raw_records
    WHERE source_file = 'olist_geolocation_dataset.csv';

    SELECT COALESCE(SUM(source_occurrence_count), 0)
    INTO geolocation_occurrence_count
    FROM clean_data.geolocation;

    IF geolocation_source_count <> geolocation_occurrence_count THEN
        RAISE EXCEPTION 'Geolocation occurrence reconciliation failed: raw %, clean occurrences %',
            geolocation_source_count, geolocation_occurrence_count;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM analytics.vw_category_sales) THEN
        RAISE EXCEPTION 'Category sales analytical view is empty';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM analytics.vw_monthly_sales) THEN
        RAISE EXCEPTION 'Monthly sales analytical view is empty';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM analytics.vw_state_sales) THEN
        RAISE EXCEPTION 'State sales analytical view is empty';
    END IF;
END;
$$;
