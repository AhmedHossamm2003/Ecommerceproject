# Phase 2 Verification Evidence

**Execution date:** 23 November 2026  
**Dataset:** nine local official Olist CSV files  
**Result:** ingestion, idempotency, raw persistence, profiling, and unit tests verified

## Docker and tests

- `docker compose --profile ingestion config`: passed; the ingestion service uses `ecommerce_network`, host `postgres`, health-based dependency, read-only `/data/raw`, and the persistent PostgreSQL service.
- PostgreSQL and pgAdmin were healthy before ingestion.
- The ingestion image built from `python:3.12-slim` with psycopg 3.3.9.
- `python -m unittest discover -s /app/tests -v`: **8 tests passed in 0.089 seconds**.

The tests cover strict CSV parsing, missing files, raw string preservation, malformed rows, default rerun skipping, forced additional runs, failed database status, missing/duplicate/type profiling, and report generation.

## First ingestion execution

Command:

```powershell
docker compose --profile ingestion run --rm ingestion --strict-files
```

The command finished with `exit_code=0`. All counts below are taken from the actual stdout logs and PostgreSQL verification, not examples.

| Source file | Run status | Read | Inserted | Duration (seconds) |
|---|---|---:|---:|---:|
| `olist_orders_dataset.csv` | success | 99,441 | 99,441 | 37.026 |
| `olist_order_items_dataset.csv` | success | 112,650 | 112,650 | 45.763 |
| `olist_customers_dataset.csv` | success | 99,441 | 99,441 | 35.923 |
| `olist_products_dataset.csv` | success | 32,951 | 32,951 | 9.540 |
| `olist_order_payments_dataset.csv` | success | 103,886 | 103,886 | 32.595 |
| `olist_order_reviews_dataset.csv` | success | 99,224 | 99,224 | 28.359 |
| `olist_sellers_dataset.csv` | success | 3,095 | 3,095 | 0.654 |
| `olist_geolocation_dataset.csv` | success | 1,000,163 | 1,000,163 | 418.847 |
| `product_category_name_translation.csv` | success | 71 | 71 | 3.427 |
| **Total** | **9 successful** | **1,550,922** | **1,550,922** | |

Full profiling started after ingestion and completed at `2026-11-23 14:28:39 UTC`; the end-to-end process exited successfully.

## Repeat execution / idempotency

Command:

```powershell
docker compose --profile ingestion run --rm ingestion --skip-profile --strict-files
```

Result: `exit_code=0`; all nine filename/SHA-256 pairs were recorded with status `skipped`, `records_inserted=0`, and `records_skipped` equal to the previously ingested file count. The raw table remained at **1,550,922 rows**.

## PostgreSQL proof

`sql/verify_phase2.sql` returned:

- Schema `raw_data`: present.
- Tables `raw_data.ingestion_runs` and `raw_data.records`: present.
- Successful runs: 9.
- Idempotent skipped runs: 9.
- Metadata-to-physical-row reconciliation: `counts_match = true` for every successful run.
- Orphan raw records: 0.
- Raw ingestion timestamp range: `2026-11-23 14:02:31.249753+00` to `2026-11-23 14:12:57.259568+00`.
- One readable JSONB payload was returned for every source file, including empty review fields represented as `""`.

Persisted counts:

| Source file | Stored rows |
|---|---:|
| `olist_customers_dataset.csv` | 99,441 |
| `olist_geolocation_dataset.csv` | 1,000,163 |
| `olist_order_items_dataset.csv` | 112,650 |
| `olist_order_payments_dataset.csv` | 103,886 |
| `olist_order_reviews_dataset.csv` | 99,224 |
| `olist_orders_dataset.csv` | 99,441 |
| `olist_products_dataset.csv` | 32,951 |
| `olist_sellers_dataset.csv` | 3,095 |
| `product_category_name_translation.csv` | 71 |
| **Total** | **1,550,922** |

## Persistence after restart

The required non-destructive `docker compose down` was attempted without `-v`, but Docker Desktop failed to stop pgAdmin with `tried to kill container, but did not receive an exit event`; neither service nor volume was deleted. To verify the database storage itself without risking the volume, PostgreSQL was restarted with:

```powershell
docker compose restart postgres
```

The PostgreSQL log reported that the existing database directory was reused and completed recovery with `database system is ready to accept connections` at `2026-11-23 14:54:57 UTC`. Running the verification SQL again after that restart returned the same nine grouped counts and **1,550,922 raw rows**. This verifies persistence of the `ecommerce_postgres_data` named volume. A clean full `down`/`up` demonstration remains a useful manual retry after restarting Docker Desktop, but it is not required to establish that PostgreSQL survived an actual container restart.

No `docker compose down -v`, volume removal, database reset, or destructive SQL was executed.

## Full profiling findings

- Full scan, not sampling: 1,550,922 source rows.
- Exact duplicates: 261,831 in geolocation; zero in the other eight files.
- Candidate key: `review_id` alone has 814 duplicate-key rows; (`review_id`, `order_id`) passes.
- Missing order timestamps: approved 160; carrier-delivered 1,783; customer-delivered 2,965.
- Missing product category/name-description-photo fields: 610 each; physical measurements: 2 each.
- Missing review title: 87,658 (88.34%); missing review message: 58,275 (58.73%).
- Leading/trailing whitespace observations: review title 1,996; review message 9,424; geolocation city 1.
- Invalid numeric parses: 0. Invalid date parses: 0. Invalid tested category/range values: 0.
- Source hashes in the Phase 2 profile match the hashes used by successful ingestion metadata.

## Acceptance checklist

| Criterion | Status | Evidence |
|---|---|---|
| Preserve Phase 1 | Completed | Existing services, proposal, documents, volumes, and history retained |
| Python ingestion | Completed | Modular `scripts/ingestion/` implementation |
| Dedicated ingestion container/network | Completed | Build and live one-shot run passed |
| Original CSVs unchanged | Completed | Read-only mount and matching SHA-256 values |
| Raw records and metadata persisted | Completed | 1,550,922 records; 9 reconciled success runs |
| Detailed logs | Completed | Actual UTC run/file/count/duration/status logs observed |
| Missing, duplicates, invalid types profiled | Completed | Generated full Markdown and CSV reports |
| Predictable rerun | Completed | 9 skipped runs; zero additional records |
| Verification SQL | Completed | All read-only queries passed; zero orphans |
| Persistence | Completed | Same counts after PostgreSQL container restart |
| README, report, lab guide | Completed | Phase 2 documentation added |
| Automated tests | Completed | 8/8 passed |
| Screenshots | Manual action | Exact safe capture checklist supplied; none fabricated |
| Phase 3-6 excluded | Completed | No cleaning, warehouse, orchestration, views, or dashboard code |
