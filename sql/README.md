# SQL

- `02_raw_storage.sql` creates the repeatable, non-destructive Phase 2 `raw_data` schema, metadata table, JSONB landing table, constraints, and indexes.
- `verify_phase2.sql` contains read-only proof queries for schema existence, per-file counts, successful/skipped runs, metadata reconciliation, timestamps, sample JSONB payloads, hashes, and orphan detection.
- `03_phase3_schema.sql` creates typed clean tables, lineage/reject metadata, the warehouse star schema, and analytical views.
- `04_phase3_transform.sql` performs the atomic, idempotent rebuild from the latest successful raw runs and executes reconciliation guards.
- `verify_phase3.sql` proves clean counts, rejects, measured quality results, warehouse reconciliation, geolocation deduplication, and analytical outputs.
- `05_phase4_quality.sql` creates configurable rules plus durable quality-gate runs and results.
- `verify_phase4.sql` shows the latest gate and every observed rule value.
- `06_phase6_bi.sql` creates the executive KPI and pipeline-health views used by the reporting kit.

Phase 2 SQL remains raw-only; Phase 3 adds the derived clean and analytical layers without changing raw records.
