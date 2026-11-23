# SQL

- `02_raw_storage.sql` creates the repeatable, non-destructive Phase 2 `raw_data` schema, metadata table, JSONB landing table, constraints, and indexes.
- `verify_phase2.sql` contains read-only proof queries for schema existence, per-file counts, successful/skipped runs, metadata reconciliation, timestamps, sample JSONB payloads, hashes, and orphan detection.
- `03_phase3_schema.sql` creates typed clean tables, lineage/reject metadata, the warehouse star schema, and analytical views.
- `04_phase3_transform.sql` performs the atomic, idempotent rebuild from the latest successful raw runs and executes reconciliation guards.
- `verify_phase3.sql` proves clean counts, rejects, measured quality results, warehouse reconciliation, geolocation deduplication, and analytical outputs.

Phase 2 SQL remains raw-only; Phase 3 adds the derived clean and analytical layers without changing raw records.
