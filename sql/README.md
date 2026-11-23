# SQL

- `02_raw_storage.sql` creates the repeatable, non-destructive Phase 2 `raw_data` schema, metadata table, JSONB landing table, constraints, and indexes.
- `verify_phase2.sql` contains read-only proof queries for schema existence, per-file counts, successful/skipped runs, metadata reconciliation, timestamps, sample JSONB payloads, hashes, and orphan detection.

No clean, fact, dimension, or analytical-view SQL is implemented in Phase 2.
