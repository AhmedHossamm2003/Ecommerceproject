-- Phase 2 raw landing schema. Safe to run repeatedly; never drops existing data.

CREATE SCHEMA IF NOT EXISTS raw_data;

CREATE TABLE IF NOT EXISTS raw_data.ingestion_runs (
    ingestion_run_id UUID PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    source_file TEXT NOT NULL,
    source_file_hash CHAR(64) NOT NULL,
    source_file_size_bytes BIGINT NOT NULL,
    records_read BIGINT NOT NULL DEFAULT 0,
    records_inserted BIGINT NOT NULL DEFAULT 0,
    error_message TEXT,
    CONSTRAINT ingestion_runs_status_check
        CHECK (status IN ('running', 'success', 'failed', 'skipped')),
    CONSTRAINT ingestion_runs_hash_check
        CHECK (source_file_hash ~ '^[0-9a-f]{64}$'),
    CONSTRAINT ingestion_runs_size_check
        CHECK (source_file_size_bytes >= 0),
    CONSTRAINT ingestion_runs_counts_check
        CHECK (records_read >= 0 AND records_inserted >= 0),
    CONSTRAINT ingestion_runs_finished_check
        CHECK (
            (status = 'running' AND finished_at IS NULL)
            OR (status <> 'running' AND finished_at IS NOT NULL)
        )
);

CREATE TABLE IF NOT EXISTS raw_data.records (
    raw_record_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ingestion_run_id UUID NOT NULL
        REFERENCES raw_data.ingestion_runs (ingestion_run_id) ON DELETE RESTRICT,
    source_file TEXT NOT NULL,
    source_row_number BIGINT NOT NULL,
    raw_payload JSONB NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT records_source_row_check CHECK (source_row_number > 0),
    CONSTRAINT records_payload_object_check CHECK (jsonb_typeof(raw_payload) = 'object'),
    CONSTRAINT records_run_row_unique UNIQUE (ingestion_run_id, source_row_number)
);

CREATE INDEX IF NOT EXISTS idx_ingestion_runs_source_hash_status
    ON raw_data.ingestion_runs (source_file, source_file_hash, status);

CREATE INDEX IF NOT EXISTS idx_ingestion_runs_started_at
    ON raw_data.ingestion_runs (started_at DESC);

CREATE INDEX IF NOT EXISTS idx_records_source_file
    ON raw_data.records (source_file);

CREATE INDEX IF NOT EXISTS idx_records_ingested_at
    ON raw_data.records (ingested_at DESC);

COMMENT ON SCHEMA raw_data IS
    'Immutable Phase 2 landing area for parsed source CSV records and ingestion metadata.';

COMMENT ON COLUMN raw_data.records.raw_payload IS
    'JSON object retaining source column names and parsed string values. It is not a byte-for-byte CSV copy.';
