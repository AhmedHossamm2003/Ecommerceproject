# Olist Source Data Dictionary

## Verification status

The CSV files were not present locally on 2026-11-16 and Kaggle credentials were not configured. The column lists below describe the **expected public Olist schema** and are suitable for planning, but their headers and inferred types must be verified by running `scripts/profile_dataset.py` after download. They are not presented as measured local results.

Logical types are proposed PostgreSQL-friendly interpretations. Identifier strings must remain text; they are not numeric measures.

## `olist_orders_dataset.csv`

Candidate primary key: `order_id`. Candidate foreign key: `customer_id` -> customers.

| Column | Expected logical type | Nullable expectation | Meaning |
|---|---|---|---|
| `order_id` | TEXT | No | Order identifier |
| `customer_id` | TEXT | No | Order-specific customer identifier |
| `order_status` | TEXT | No | Lifecycle status such as delivered or canceled |
| `order_purchase_timestamp` | TIMESTAMP | No | Customer purchase time; date basis for monthly analysis |
| `order_approved_at` | TIMESTAMP | Yes | Payment/order approval time |
| `order_delivered_carrier_date` | TIMESTAMP | Yes | Time handed to carrier |
| `order_delivered_customer_date` | TIMESTAMP | Yes | Actual customer delivery time |
| `order_estimated_delivery_date` | TIMESTAMP | No/verify | Estimated delivery time |

## `olist_order_items_dataset.csv`

Candidate primary key: (`order_id`, `order_item_id`). Candidate foreign keys: `order_id` -> orders, `product_id` -> products, `seller_id` -> sellers.

| Column | Expected logical type | Nullable expectation | Meaning |
|---|---|---|---|
| `order_id` | TEXT | No | Parent order |
| `order_item_id` | INTEGER | No | Sequence of item within order |
| `product_id` | TEXT | No | Product identifier |
| `seller_id` | TEXT | No | Seller identifier |
| `shipping_limit_date` | TIMESTAMP | No/verify | Seller shipping deadline |
| `price` | NUMERIC(12,2) | No | Item sale price; primary revenue field |
| `freight_value` | NUMERIC(12,2) | No | Freight charged for the item; excluded from primary revenue |

## `olist_customers_dataset.csv`

Candidate primary key: `customer_id`. `customer_unique_id` is a person-level business identifier and may repeat across order-specific customer records.

| Column | Expected logical type | Nullable expectation | Meaning |
|---|---|---|---|
| `customer_id` | TEXT | No | Order-specific customer identifier |
| `customer_unique_id` | TEXT | No | Identifier linking repeat customers |
| `customer_zip_code_prefix` | TEXT | No/verify | Five-digit postal prefix; keep leading zeros |
| `customer_city` | TEXT | No/verify | Customer city |
| `customer_state` | CHAR(2) | No/verify | Brazilian state code used for geographic analysis |

## `olist_products_dataset.csv`

Candidate primary key: `product_id`. Candidate foreign key: `product_category_name` -> translation table, although missing categories and unmatched translations are possible.

| Column | Expected logical type | Nullable expectation | Meaning |
|---|---|---|---|
| `product_id` | TEXT | No | Product identifier |
| `product_category_name` | TEXT | Yes | Portuguese category name |
| `product_name_lenght` | INTEGER | Yes | Product-name character count; source spelling is retained |
| `product_description_lenght` | INTEGER | Yes | Description character count; source spelling is retained |
| `product_photos_qty` | INTEGER | Yes | Number of product photos |
| `product_weight_g` | NUMERIC | Yes | Weight in grams |
| `product_length_cm` | NUMERIC | Yes | Length in centimeters |
| `product_height_cm` | NUMERIC | Yes | Height in centimeters |
| `product_width_cm` | NUMERIC | Yes | Width in centimeters |

## `olist_order_payments_dataset.csv`

Candidate primary key: (`order_id`, `payment_sequential`). Candidate foreign key: `order_id` -> orders.

| Column | Expected logical type | Nullable expectation | Meaning |
|---|---|---|---|
| `order_id` | TEXT | No | Parent order |
| `payment_sequential` | INTEGER | No | Sequence for split/multiple payment records |
| `payment_type` | TEXT | No/verify | Payment method |
| `payment_installments` | INTEGER | No/verify | Number of installments |
| `payment_value` | NUMERIC(12,2) | No/verify | Value of the payment record |

Payment rows must first be aggregated to order grain before comparison with order-level or item-level totals. They are not used to calculate product sales revenue.

## `olist_order_reviews_dataset.csv`

Candidate key requires profiling. `review_id` may not be sufficient without further validation. Candidate foreign key: `order_id` -> orders.

| Column | Expected logical type | Nullable expectation | Meaning |
|---|---|---|---|
| `review_id` | TEXT | No | Review identifier |
| `order_id` | TEXT | No | Reviewed order |
| `review_score` | INTEGER | No/verify | Satisfaction score |
| `review_comment_title` | TEXT | Yes | Optional review title |
| `review_comment_message` | TEXT | Yes | Optional review body |
| `review_creation_date` | TIMESTAMP | No/verify | Survey/review creation time |
| `review_answer_timestamp` | TIMESTAMP | No/verify | Review response time |

## `olist_sellers_dataset.csv`

Candidate primary key: `seller_id`.

| Column | Expected logical type | Nullable expectation | Meaning |
|---|---|---|---|
| `seller_id` | TEXT | No | Seller identifier |
| `seller_zip_code_prefix` | TEXT | No/verify | Five-digit postal prefix; keep leading zeros |
| `seller_city` | TEXT | No/verify | Seller city |
| `seller_state` | CHAR(2) | No/verify | Seller state code |

## `olist_geolocation_dataset.csv`

No primary key is assumed. A postal prefix can have multiple coordinate rows, so direct joins can multiply facts.

| Column | Expected logical type | Nullable expectation | Meaning |
|---|---|---|---|
| `geolocation_zip_code_prefix` | TEXT | No/verify | Five-digit postal prefix; keep leading zeros |
| `geolocation_lat` | DOUBLE PRECISION | No/verify | Latitude |
| `geolocation_lng` | DOUBLE PRECISION | No/verify | Longitude |
| `geolocation_city` | TEXT | No/verify | City label |
| `geolocation_state` | CHAR(2) | No/verify | State code |

## `product_category_name_translation.csv`

Candidate primary key: `product_category_name`.

| Column | Expected logical type | Nullable expectation | Meaning |
|---|---|---|---|
| `product_category_name` | TEXT | No | Portuguese category key |
| `product_category_name_english` | TEXT | No/verify | English category label |

## Cross-file quality checks planned after download

- Confirm headers exactly match this expected dictionary.
- Count nulls and exact duplicate rows in every file.
- Validate candidate keys for uniqueness and non-nullness.
- Test all proposed foreign keys and report unmatched values.
- Parse all timestamps with explicit error counts.
- Check `price`, `freight_value`, and `payment_value` for negative or implausible values.
- Compare observed `order_status`, state, and payment-type domains with documented expectations.
- Quantify missing product categories and missing translation matches.
- Reconcile item-level price totals to order-level aggregates without joining one-to-many tables directly.
