"""Database orchestration for the idempotent Phase 3 transformation."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from psycopg.types.json import Jsonb

from .config import EXPECTED_FILES, Settings
from .database import RawDatabase


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class TransformationResult:
    run_id: uuid.UUID
    status: str
    clean_records: int
    fact_records: int
    rejected_records: int
    duration_seconds: float
    error_message: str | None = None


class TransformationDatabase(RawDatabase):
    def initialize_phase3_schema(self) -> None:
        sql_path = self.settings.phase3_schema_sql_path
        if not sql_path.is_file():
            raise FileNotFoundError(f"Phase 3 schema SQL is missing: {sql_path}")
        with self.connect() as connection:
            connection.execute(sql_path.read_text(encoding="utf-8"))
        LOGGER.info("Phase 3 schemas initialized from %s", sql_path)

    def latest_successful_source_runs(self) -> dict[str, str]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT ON (source_file)
                    source_file,
                    ingestion_run_id::text
                FROM raw_data.ingestion_runs
                WHERE status = 'success'
                ORDER BY source_file, finished_at DESC, ingestion_run_id DESC
                """
            ).fetchall()
        source_runs = {str(row[0]): str(row[1]) for row in rows}
        missing = [filename for filename in EXPECTED_FILES if filename not in source_runs]
        if missing:
            raise RuntimeError(
                "Phase 3 requires a successful raw run for every source file; missing: "
                + ", ".join(missing)
            )
        return {filename: source_runs[filename] for filename in EXPECTED_FILES}

    def transform(self) -> TransformationResult:
        run_id = uuid.uuid4()
        started_at = datetime.now(timezone.utc)
        started_clock = time.monotonic()
        source_runs = self.latest_successful_source_runs()
        transform_path = self.settings.phase3_transform_sql_path
        if not transform_path.is_file():
            raise FileNotFoundError(f"Phase 3 transform SQL is missing: {transform_path}")

        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO clean_data.transformation_runs (
                    transformation_run_id,
                    started_at,
                    status,
                    source_ingestion_runs
                ) VALUES (%s, %s, 'running', %s)
                """,
                (run_id, started_at, Jsonb(source_runs)),
            )

        try:
            with self.connect() as connection:
                with connection.transaction():
                    connection.execute(
                        "SELECT pg_advisory_xact_lock(hashtext('olist_phase3_transform'))"
                    )
                    connection.execute(
                        "SELECT set_config('phase3.run_id', %s, true)",
                        (str(run_id),),
                    )
                    connection.execute(transform_path.read_text(encoding="utf-8"))
                    counts = connection.execute(
                        """
                        SELECT
                            (
                                (SELECT COUNT(*) FROM clean_data.customers)
                                + (SELECT COUNT(*) FROM clean_data.orders)
                                + (SELECT COUNT(*) FROM clean_data.order_items)
                                + (SELECT COUNT(*) FROM clean_data.products)
                                + (SELECT COUNT(*) FROM clean_data.order_payments)
                                + (SELECT COUNT(*) FROM clean_data.order_reviews)
                                + (SELECT COUNT(*) FROM clean_data.sellers)
                                + (SELECT COUNT(*) FROM clean_data.geolocation)
                                + (SELECT COUNT(*) FROM clean_data.category_translation)
                            )::BIGINT AS clean_records,
                            (SELECT COUNT(*) FROM warehouse.fact_order_items)::BIGINT,
                            (
                                SELECT COUNT(*)
                                FROM clean_data.rejected_records
                                WHERE transformation_run_id = %s
                            )::BIGINT
                        """,
                        (run_id,),
                    ).fetchone()
                    clean_records, fact_records, rejected_records = map(int, counts)
                    connection.execute(
                        """
                        UPDATE clean_data.transformation_runs
                        SET finished_at = clock_timestamp(),
                            status = 'success',
                            clean_records = %s,
                            fact_records = %s,
                            rejected_records = %s
                        WHERE transformation_run_id = %s
                        """,
                        (clean_records, fact_records, rejected_records, run_id),
                    )
            return TransformationResult(
                run_id=run_id,
                status="success",
                clean_records=clean_records,
                fact_records=fact_records,
                rejected_records=rejected_records,
                duration_seconds=time.monotonic() - started_clock,
            )
        except Exception as exc:
            error_message = f"{type(exc).__name__}: {exc}"[:4000]
            try:
                with self.connect() as connection:
                    connection.execute(
                        """
                        UPDATE clean_data.transformation_runs
                        SET finished_at = clock_timestamp(),
                            status = 'failed',
                            error_message = %s
                        WHERE transformation_run_id = %s
                        """,
                        (error_message, run_id),
                    )
            except Exception as metadata_exc:
                LOGGER.error(
                    "Could not update failed transformation metadata run_id=%s error=%s",
                    run_id,
                    metadata_exc,
                )
            return TransformationResult(
                run_id=run_id,
                status="failed",
                clean_records=0,
                fact_records=0,
                rejected_records=0,
                duration_seconds=time.monotonic() - started_clock,
                error_message=error_message,
            )
