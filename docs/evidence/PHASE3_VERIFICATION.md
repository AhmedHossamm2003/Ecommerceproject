# Phase 3 Verification Evidence

## Scope

This record contains actual Phase 3 execution evidence against the nine official Olist CSV files already landed by Phase 2. Commands were executed on 23 November 2026 with the repository's Docker Compose environment.

## Automated tests

Command:

```powershell
docker compose --profile ingestion run --rm --no-deps --entrypoint python ingestion -m unittest discover -s /app/tests -v
```

Result: all 12 tests passed. The suite includes the eight Phase 2 ingestion/profile tests and four Phase 3 SQL safety/contract tests. The Phase 3 tests verify that transformation SQL does not truncate or delete raw storage, selects latest successful ingestion runs, declares the star schema/views, and contains count/revenue/geolocation reconciliation guards.

## Full transformation

Command:

```powershell
docker compose --profile transformation run --rm transformation
```

First verified run:

| Field | Value |
|---|---|
| Transformation run ID | `15983188-e361-4a17-99b4-832325cc87a6` |
| Status | `success` |
| Clean records | 1,289,091 |
| Fact records | 112,650 |
| Rejected records | 0 |
| Duration | 734.749 seconds |

## Typed clean counts

| Table | Rows |
|---|---:|
| `category_translation` | 71 |
| `customers` | 99,441 |
| `geolocation` | 738,332 |
| `order_items` | 112,650 |
| `order_payments` | 103,886 |
| `order_reviews` | 99,224 |
| `orders` | 99,441 |
| `products` | 32,951 |
| `sellers` | 3,095 |
| **Total** | **1,289,091** |

## Warehouse and reconciliation

| Check | Verified value |
|---|---:|
| `dim_customers` rows, including Unknown | 99,442 |
| `dim_products` rows, including Unknown | 32,952 |
| `dim_sellers` rows, including Unknown | 3,096 |
| `dim_date` rows, including Unknown | 775 |
| Clean order-item rows | 112,650 |
| Fact order-item rows | 112,650 |
| Clean item revenue | 13,591,643.70 |
| Fact item revenue | 13,591,643.70 |
| Fact rows with any Unknown key | 0 |
| Geolocation source rows represented | 1,000,163 |
| Collapsed geolocation duplicates | 261,831 |

All transaction guards passed. The selected raw total remained 1,550,922 and no Phase 3 statement deletes, updates, or truncates `raw_data`.

## Recorded baseline metrics

| Metric | Value |
|---|---:|
| Products missing category | 610 |
| Products with unmatched translation | 13 |
| Reviews missing title | 87,658 |
| Reviews missing message | 58,256 |
| Zero-installment payments | 2 |
| Rejected rows | 0 |

Zero rejects means every official source row required by a typed table passed the structural/type rules. It does not mean optional missing values are absent; those are retained as `NULL` and measured above.

## Analytical smoke tests

- Highest delivered-sales category: `health_beauty`, 9,465 items, 8,647 orders, revenue 1,233,131.72 (9.33%).
- Highest delivered-sales customer state: `SP`, 46,448 items, 40,501 orders, revenue 5,067,633.16 (38.33%).
- Monthly view returned a complete 26-month spine from September 2016 through October 2018, including zero-activity months.

## Repeatability

The final rebuilt image was executed a second time against the same raw runs:

| Field | Repeat value |
|---|---|
| Transformation run ID | `c2bb258a-d22c-46ae-a6d9-f652d60c268a` |
| Status | `success` |
| Clean records | 1,289,091 |
| Fact records | 112,650 |
| Rejected records | 0 |
| Duration | 572.003 seconds |

`sql/verify_phase3.sql` was rerun after completion. Both successful transformation rows reference the same nine ingestion run UUIDs, and every clean, fact, reject, metric, reconciliation, and analytical result remained unchanged. This verifies deterministic, non-duplicating rerun behavior for unchanged raw inputs.

## Manual screenshot checklist

Screenshots are a team presentation action, not fabricated evidence. Suggested captures:

1. `docker compose ps` with PostgreSQL and pgAdmin healthy.
2. Latest successful rows from `clean_data.transformation_runs`.
3. Clean and warehouse counts from `sql/verify_phase3.sql`.
4. Exact row/revenue/geolocation reconciliation output.
5. Top category and state analytical view results in pgAdmin.
