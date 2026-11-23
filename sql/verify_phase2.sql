-- Read-only Phase 2 verification queries. Safe before and after container restarts.

-- 1. Prove that the raw_data schema exists.
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name = 'raw_data';

-- 2. Prove that the required landing tables exist.
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'raw_data'
ORDER BY table_name;

-- 3. Raw record counts by source file.
SELECT source_file, COUNT(*) AS total_records
FROM raw_data.records
GROUP BY source_file
ORDER BY source_file;

-- 4. Successful and skipped ingestion executions with hashes and counts.
SELECT
    ingestion_run_id,
    source_file,
    source_file_hash,
    status,
    records_read,
    records_inserted,
    started_at,
    finished_at
FROM raw_data.ingestion_runs
ORDER BY started_at, source_file;

-- 5. Reconcile each successful run's metadata with physically stored records.
SELECT
    runs.ingestion_run_id,
    runs.source_file,
    runs.records_inserted AS metadata_count,
    COUNT(records.raw_record_id) AS stored_count,
    runs.records_inserted = COUNT(records.raw_record_id) AS counts_match
FROM raw_data.ingestion_runs AS runs
LEFT JOIN raw_data.records AS records
    ON records.ingestion_run_id = runs.ingestion_run_id
WHERE runs.status = 'success'
GROUP BY
    runs.ingestion_run_id,
    runs.source_file,
    runs.records_inserted
ORDER BY runs.source_file, runs.started_at;

-- 6. Ingestion timestamp range demonstrates persisted landing times.
SELECT MIN(ingested_at) AS first_ingested_at, MAX(ingested_at) AS last_ingested_at
FROM raw_data.records;

-- 7. One JSONB payload example per source file (parsed strings, not CSV bytes).
-- The lateral lookup avoids sorting every JSONB payload in the raw table.
SELECT
    files.source_file,
    sample.source_row_number,
    sample.raw_payload,
    sample.ingested_at
FROM (
    SELECT DISTINCT source_file
    FROM raw_data.records
) AS files
CROSS JOIN LATERAL (
    SELECT source_row_number, raw_payload, ingested_at
    FROM raw_data.records
    WHERE source_file = files.source_file
    LIMIT 1
) AS sample
ORDER BY files.source_file;

-- 8. Confirm there are no orphan raw records.
SELECT COUNT(*) AS orphan_record_count
FROM raw_data.records AS records
LEFT JOIN raw_data.ingestion_runs AS runs
    ON runs.ingestion_run_id = records.ingestion_run_id
WHERE runs.ingestion_run_id IS NULL;
