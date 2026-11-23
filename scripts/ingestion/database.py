"""PostgreSQL access for schema initialization and atomic raw file loads."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import psycopg
from psycopg.types.json import Jsonb

from .config import Settings
from .csv_reader import SourceFile


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class LoadResult:
    run_id: uuid.UUID
    source_file: str
    status: str
    records_read: int
    records_inserted: int
    records_skipped: int
    duration_seconds: float
    error_message: str | None = None


class RawDatabase:
    def __init__(self, settings: Settings):
        self.settings = settings

    def connect(self) -> psycopg.Connection:
        return psycopg.connect(**self.settings.connection_kwargs, autocommit=True)

    def wait_until_ready(self) -> None:
        last_error: Exception | None = None
        for attempt in range(1, self.settings.db_retry_attempts + 1):
            try:
                with self.connect() as connection:
                    connection.execute("SELECT 1")
                LOGGER.info("PostgreSQL connection ready host=%s port=%s database=%s",
                            self.settings.db_host, self.settings.db_port, self.settings.db_name)
                return
            except psycopg.Error as exc:
                last_error = exc
                LOGGER.warning(
                    "PostgreSQL not ready attempt=%d/%d error=%s",
                    attempt,
                    self.settings.db_retry_attempts,
                    exc,
                )
                if attempt < self.settings.db_retry_attempts:
                    time.sleep(self.settings.db_retry_delay_seconds)
        raise ConnectionError(
            f"PostgreSQL was unavailable after {self.settings.db_retry_attempts} attempts"
        ) from last_error

    def initialize_schema(self) -> None:
        sql_path = self.settings.schema_sql_path
        if not sql_path.is_file():
            raise FileNotFoundError(f"Raw schema SQL is missing: {sql_path}")
        statement = sql_path.read_text(encoding="utf-8")
        with self.connect() as connection:
            connection.execute(statement)
        LOGGER.info("Raw storage schema initialized from %s", sql_path)

    def load_file(
        self,
        source: SourceFile,
        rows: Iterable[tuple[int, dict[str, str]]],
        force: bool = False,
    ) -> LoadResult:
        run_id = uuid.uuid4()
        started_at = datetime.now(timezone.utc)
        started_clock = time.monotonic()
        records_read = 0

        try:
            with self.connect() as connection:
                with connection.transaction():
                    # Serialize decisions for the same filename/content while keeping
                    # --force available for deliberate additional immutable runs.
                    connection.execute(
                        "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                        (f"{source.filename}:{source.sha256}",),
                    )
                    previous = connection.execute(
                        """
                        SELECT ingestion_run_id, records_inserted
                        FROM raw_data.ingestion_runs
                        WHERE source_file = %s
                          AND source_file_hash = %s
                          AND status = 'success'
                        ORDER BY finished_at DESC
                        LIMIT 1
                        """,
                        (source.filename, source.sha256),
                    ).fetchone()

                    if previous and not force:
                        skipped_count = int(previous[1])
                        connection.execute(
                            """
                            INSERT INTO raw_data.ingestion_runs (
                                ingestion_run_id, started_at, finished_at, status,
                                source_file, source_file_hash, source_file_size_bytes,
                                records_read, records_inserted, error_message
                            ) VALUES (%s, %s, clock_timestamp(), 'skipped', %s, %s, %s, 0, 0, %s)
                            """,
                            (
                                run_id,
                                started_at,
                                source.filename,
                                source.sha256,
                                source.size_bytes,
                                f"Identical content already ingested by run {previous[0]}",
                            ),
                        )
                        return LoadResult(
                            run_id=run_id,
                            source_file=source.filename,
                            status="skipped",
                            records_read=0,
                            records_inserted=0,
                            records_skipped=skipped_count,
                            duration_seconds=time.monotonic() - started_clock,
                        )

                    connection.execute(
                        """
                        INSERT INTO raw_data.ingestion_runs (
                            ingestion_run_id, started_at, status, source_file,
                            source_file_hash, source_file_size_bytes,
                            records_read, records_inserted
                        ) VALUES (%s, %s, 'running', %s, %s, %s, 0, 0)
                        """,
                        (run_id, started_at, source.filename, source.sha256, source.size_bytes),
                    )

                    with connection.cursor() as cursor:
                        with cursor.copy(
                            """
                            COPY raw_data.records (
                                ingestion_run_id, source_file, source_row_number, raw_payload
                            ) FROM STDIN
                            """
                        ) as copy:
                            for source_row_number, payload in rows:
                                records_read += 1
                                copy.write_row(
                                    (run_id, source.filename, source_row_number, Jsonb(payload))
                                )

                    connection.execute(
                        """
                        UPDATE raw_data.ingestion_runs
                        SET finished_at = clock_timestamp(),
                            status = 'success',
                            records_read = %s,
                            records_inserted = %s
                        WHERE ingestion_run_id = %s
                        """,
                        (records_read, records_read, run_id),
                    )

            return LoadResult(
                run_id=run_id,
                source_file=source.filename,
                status="success",
                records_read=records_read,
                records_inserted=records_read,
                records_skipped=0,
                duration_seconds=time.monotonic() - started_clock,
            )
        except Exception as exc:
            duration = time.monotonic() - started_clock
            error_message = f"{type(exc).__name__}: {exc}"[:4000]
            self._record_failure(
                run_id=run_id,
                started_at=started_at,
                source=source,
                records_read=records_read,
                error_message=error_message,
            )
            return LoadResult(
                run_id=run_id,
                source_file=source.filename,
                status="failed",
                records_read=records_read,
                records_inserted=0,
                records_skipped=0,
                duration_seconds=duration,
                error_message=error_message,
            )

    def _record_failure(
        self,
        run_id: uuid.UUID,
        started_at: datetime,
        source: SourceFile,
        records_read: int,
        error_message: str,
    ) -> None:
        try:
            with self.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO raw_data.ingestion_runs (
                        ingestion_run_id, started_at, finished_at, status,
                        source_file, source_file_hash, source_file_size_bytes,
                        records_read, records_inserted, error_message
                    ) VALUES (%s, %s, clock_timestamp(), 'failed', %s, %s, %s, %s, 0, %s)
                    ON CONFLICT (ingestion_run_id) DO UPDATE
                    SET finished_at = EXCLUDED.finished_at,
                        status = 'failed',
                        records_read = EXCLUDED.records_read,
                        records_inserted = 0,
                        error_message = EXCLUDED.error_message
                    """,
                    (
                        run_id,
                        started_at,
                        source.filename,
                        source.sha256,
                        source.size_bytes,
                        records_read,
                        error_message,
                    ),
                )
        except Exception as metadata_exc:
            LOGGER.error(
                "Could not persist failed-run metadata run_id=%s error=%s",
                run_id,
                metadata_exc,
            )
