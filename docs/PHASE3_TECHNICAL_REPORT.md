# Phase 3 Technical Report

## Objective and scope

Phase 3 converts the immutable Phase 2 JSONB landing records into typed, source-aligned clean tables and an analytical star schema. It also exposes three PostgreSQL views that answer the business questions defined in Phase 1.

The scope stops at deterministic SQL transformation and analytical views. It does not add scheduled orchestration, a separate automated quality-gate framework, Kestra, Power BI, cloud services, Kafka, Spark, Airflow, or dbt.

## Implemented architecture

```text
raw_data.records + raw_data.ingestion_runs
                 |
                 | latest successful run per source file
                 v
clean_data typed tables
  + transformation_runs
  + rejected_records
  + quality_metrics
                 |
                 v
warehouse star schema
  dim_customers  dim_products  dim_sellers  dim_date
                         |
                         v
                 fact_order_items
                         |
                         v
analytics.vw_category_sales
analytics.vw_monthly_sales
analytics.vw_state_sales
```

The `transformation` Compose service uses the same Python/psycopg image and Docker network as ingestion. It is a manual one-shot profile and is not started by routine `docker compose up -d`.

## Raw-run selection and idempotency

For each expected filename, Phase 3 selects the most recently finished `success` row from `raw_data.ingestion_runs`. Skipped and failed ingestion attempts are never transformed. The selected run UUIDs are stored as JSONB in `clean_data.transformation_runs` for lineage.

Each execution creates a new transformation metadata row but atomically rebuilds the current derived clean and warehouse tables. A PostgreSQL advisory transaction lock prevents concurrent rebuilds. Raw records and earlier transformation metadata, reject evidence, and quality metrics are preserved.

## Cleaning rules

- Identifiers remain text and are trimmed, never converted to numbers.
- Postal prefixes are retained as five-character text with leading-zero padding.
- State codes are uppercased and validated as two letters.
- Numeric and timestamp values use safe conversion functions; invalid required rows go to `clean_data.rejected_records` with the raw payload and reason.
- Empty optional values become SQL `NULL`.
- Review title/message whitespace is trimmed.
- Product source spellings such as `product_name_lenght` are mapped to correctly named clean columns.
- Exact normalized geolocation rows are collapsed while `source_occurrence_count` preserves how many source rows each clean row represents.
- Missing and untranslated product categories remain in the product dimension and receive the analytical label `Unknown`.
- Payments and reviews are typed in the clean layer but are not joined into the order-item fact, preventing many-to-many revenue multiplication.

## Typed clean layer

The clean layer contains:

- `customers`
- `orders`
- `order_items`
- `products`
- `order_payments`
- `order_reviews`
- `sellers`
- `geolocation`
- `category_translation`

Every non-geolocation row retains `raw_record_id`, `source_row_number`, and `transformation_run_id`. Geolocation retains a representative raw row plus its total occurrence count.

## Warehouse design

`warehouse.fact_order_items` has one row per (`order_id`, `order_item_id`). It stores item price and freight separately, the order purchase timestamp/status, and foreign keys to customer, product, seller, and purchase date dimensions.

Each dimension includes an explicit key `0` Unknown member. The fact table never silently loses an otherwise valid order item because a descriptive dimension value is missing. The primary sales measure is `SUM(item_price)` for delivered orders; freight is reported separately.

## Analytical views

- `analytics.vw_category_sales`: delivered item revenue, freight, item/order counts, and revenue percentage by English category.
- `analytics.vw_monthly_sales`: complete purchase-month spine with delivered revenue, freight, item count, and distinct order count.
- `analytics.vw_state_sales`: delivered revenue, freight, item/order counts, and revenue percentage by customer state.

These views intentionally avoid direct joins to payments, reviews, or raw geolocation.

## Reconciliation and failure behavior

Before a transaction can commit, Phase 3 verifies:

1. Clean order-item rows equal warehouse fact rows.
2. Clean item-price revenue exactly equals fact revenue.
3. The sum of geolocation occurrence counts equals the selected raw geolocation count.
4. All three analytical views return rows.

Any violation rolls back the derived rebuild and marks the transformation run failed. These are technical transaction guards for Phase 3; Phase 4 subsequently added configurable blocking/warning policy and durable rule results.

## Commands

```powershell
docker compose up -d postgres pgadmin
docker compose --profile transformation build transformation
docker compose --profile transformation run --rm transformation
Get-Content -Raw sql\verify_phase3.sql | docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db
```

Rerunning the transformation is supported and produces the same derived counts for unchanged raw hashes.

## Verified execution results

The full official dataset transformation completed successfully on 23 November 2026. A final-image repeat run also succeeded with identical results, proving deterministic rebuild behavior for unchanged raw runs. It selected 1,550,922 raw rows and produced:

| Layer or table group | Rows |
|---|---:|
| Typed clean tables | 1,289,091 |
| `warehouse.fact_order_items` | 112,650 |
| Rejected rows | 0 |
| Unique normalized geolocation rows | 738,332 |
| Geolocation source rows represented | 1,000,163 |

Clean order-item count and fact count both equal 112,650. Clean and fact item revenue both equal 13,591,643.70, and no fact uses an Unknown dimension key. Dimension counts include their key-0 member: 99,442 customers, 32,952 products, 3,096 sellers, and 775 dates.

The baseline metrics found 610 products without a category, 13 products whose category did not match the translation table, 87,658 reviews without a title, 58,256 reviews without a message, and two zero-installment payments. These are retained and measured rather than silently removed.

The leading delivered-sales results were `health_beauty` at 1,233,131.72 and Sao Paulo (`SP`) at 5,067,633.16. Full reproducible output and repeat-run evidence are recorded in `docs/evidence/PHASE3_VERIFICATION.md`.

## Phase 4 continuation

Phase 4 builds explicit configurable pass/fail quality gates around these rejects, metrics, constraints, and reconciliation results. Phase 3 remains the typed-data and deterministic-modeling foundation; the implemented policy is in `sql/05_phase4_quality.sql` and `scripts/ingestion/quality.py`.
