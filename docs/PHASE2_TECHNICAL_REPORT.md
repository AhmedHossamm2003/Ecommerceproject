# Phase 2 Technical Report

## A. Objective and scope

Phase 2 implements source ingestion, persistent raw storage, containerization, operational logging, and initial profiling for the Olist dataset. Ingestion moves source records into a controlled landing area; raw storage keeps those values before business cleaning; containerization makes the runtime repeatable across team machines.

This phase deliberately does not clean or deduplicate records, build facts/dimensions or analytical views, add automated quality gates, orchestrate schedules, or create dashboards.

## B. Dataset source

The input is the [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce): nine UTF-8 CSV files covering orders, order items, customers, products, payments, reviews, sellers, geolocation, and category translation. The official files are stored unchanged under `data/raw/` and excluded from Git.

## C. Implemented architecture

```text
Olist CSV files (read-only bind mount)
              |
              v
Python 3.12 one-shot ingestion container
  - strict streaming csv reader
  - SHA-256 idempotency check
  - UTC stdout logging
  - full streaming profiler
              |
              v
PostgreSQL persistent named volume
  raw_data.ingestion_runs
  raw_data.records (JSONB payload)
```

The ingestion service joins the existing `ecommerce_network` and addresses PostgreSQL as `postgres`. The existing PostgreSQL and pgAdmin services and named volumes are preserved. The service is behind the `ingestion` Compose profile, so ordinary `docker compose up -d` keeps the Phase 1 workflow and does not repeatedly ingest data.

## D. Source schema and verified volume

| Source file | Rows | Columns | Main subject |
|---|---:|---:|---|
| `olist_orders_dataset.csv` | 99,441 | 8 | Order lifecycle and timestamps |
| `olist_order_items_dataset.csv` | 112,650 | 7 | Items, products, sellers, prices, freight |
| `olist_customers_dataset.csv` | 99,441 | 5 | Order-level and unique customers |
| `olist_products_dataset.csv` | 32,951 | 9 | Categories and physical attributes |
| `olist_order_payments_dataset.csv` | 103,886 | 5 | Payment sequence, method, installments, value |
| `olist_order_reviews_dataset.csv` | 99,224 | 7 | Scores, optional comments, review timestamps |
| `olist_sellers_dataset.csv` | 3,095 | 4 | Seller and location |
| `olist_geolocation_dataset.csv` | 1,000,163 | 5 | Postal-prefix coordinates and location labels |
| `product_category_name_translation.csv` | 71 | 2 | Portuguese-to-English category mapping |

Column names, inferred types, missing percentages, exact duplicates, candidate-key results, samples, and source hashes are recorded in `phase2_data_profile.md` and `phase2_data_profile.csv`.

## E. Ingestion process

1. `ingest.py` checks the nine configured filenames under `DATA_DIR`; available supported files are processed and missing files are logged. `--strict-files` makes any missing expected file fatal.
2. Each file is hashed with SHA-256 and its byte size is measured before database work.
3. The application connects with environment-provided credentials and retry logic. Compose also waits for the PostgreSQL health check.
4. `02_raw_storage.sql` runs safely with `IF NOT EXISTS` statements.
5. A PostgreSQL transaction takes a file/hash advisory lock, checks prior successful metadata, inserts a run row, and streams rows through PostgreSQL `COPY`.
6. Every payload is a JSONB object whose keys are the original headers and whose values are the parsed strings. Empty strings remain empty strings. There is no trimming, type conversion, filtering, or deduplication.
7. Success metadata and raw rows commit together. On any CSV or database exception, the transaction rolls back and a separate failed-run metadata row is attempted.
8. The profiler performs complete streaming scans and writes Markdown and CSV outputs.

CSV ingestion has no HTTP request, so HTTP status codes are not applicable and are not fabricated.

## F. Raw storage design

`raw_data.ingestion_runs` stores the UUID, UTC start/end timestamps, status (`running`, `success`, `failed`, or `skipped`), filename, SHA-256, file size, read/insert counts, and any error. `raw_data.records` stores a generated identifier, run UUID, filename, one-based source data-row number, JSONB payload, and ingestion timestamp.

The named `ecommerce_postgres_data` Docker volume persists both tables when containers are stopped or recreated. The CSV directory is a host bind mount and is read-only inside ingestion.

JSONB preserves parsed field names and string values, but not exact file bytes, original quoting, line endings, or column order. The unchanged CSV plus SHA-256 hash is the byte-level source of record.

For default reruns, an identical filename/hash with a prior successful run is logged as `skipped`, and no new raw records are created. `--force` deliberately creates a separate immutable run and leaves earlier runs untouched. A transaction-level advisory lock serializes the check and load for identical content.

## G. Profiling results

The full profile interprets empty strings and case-insensitive `null`, `none`, `na`, `n/a`, and `nan` as missing for reporting only. It measures every row, not a sample. Exact duplicates and candidate business-key duplicates are reported without removal.

Notable verified observations include 610 missing product category values, extensive optional review-title/message missingness, lifecycle timestamp missingness where orders have not reached later stages, 261,831 repeated exact geolocation rows, and 814 duplicate occurrences when `review_id` alone is tested. The composite (`review_id`, `order_id`) remains the useful candidate key. Detailed counts and all type/range checks are in the generated profile.

The invalid-value checks cover numeric/date parseability, leading/trailing whitespace, empty identifiers, state-code formatting, known order statuses, review-score bounds, and coordinate bounds. These are observations only; fixes belong to Phase 3.

## H. Testing and execution evidence

Commands used on 23 November 2026:

```bash
docker compose --profile ingestion config
docker compose up -d postgres pgadmin
docker compose --profile ingestion build ingestion
docker run --rm --entrypoint python ecommerce-sales-pipeline-ingestion:latest -m unittest discover -s /app/tests -v
docker compose --profile ingestion run --rm ingestion --strict-files
docker compose --profile ingestion run --rm ingestion --skip-profile
Get-Content -Raw sql\verify_phase2.sql | docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db
docker compose restart postgres
```

Unit result: 8 tests passed. Database counts, repeat-run skips, and persistence after a PostgreSQL container restart passed. A full `docker compose down` attempt was blocked by a Docker Desktop pgAdmin stop error, so the safer database-only restart was used without removing the named volume. Exact results are recorded in `docs/evidence/PHASE2_VERIFICATION.md`.

## I. Known limitations

- Raw JSONB is a parsed representation, not a byte-for-byte database copy of CSV files.
- Full duplicate profiling retains compact 128-bit row digests in memory; this is bounded well below retaining full source rows but is not constant memory.
- Screenshots require a human-selected desktop/browser view; exact capture instructions are in `docs/evidence/README.md` and no screenshots are fabricated.
- Phase 2 identifies suspicious values but intentionally does not correct them.

## J. Phase 3 handoff

Phase 3 can read immutable payloads from successful ingestion runs, use source row numbers for traceability, compare source hashes, and choose explicit clean relational types and rules. Both legitimate source duplicates and missing values remain available. No Phase 3 table or transformation is created here.
