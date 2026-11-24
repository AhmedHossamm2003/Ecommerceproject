"""Configurable Phase 4 quality-gate execution and result persistence."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from .config import Settings
from .database import RawDatabase
from .quality_rules import compare_numeric


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class QualityGateResult:
    run_id: uuid.UUID
    status: str
    rules_evaluated: int
    blocking_failures: int
    warning_failures: int
    duration_seconds: float
    error_message: str | None = None


class QualityDatabase(RawDatabase):
    def initialize_quality_schema(self) -> None:
        sql_path = self.settings.phase4_quality_sql_path
        if not sql_path.is_file():
            raise FileNotFoundError(f"Phase 4 quality SQL is missing: {sql_path}")
        with self.connect() as connection:
            connection.execute(sql_path.read_text(encoding="utf-8"))
        LOGGER.info("Phase 4 quality schema initialized from %s", sql_path)

    def run_gate(self) -> QualityGateResult:
        run_id = uuid.uuid4()
        started_at = datetime.now(timezone.utc)
        started_clock = time.monotonic()

        with self.connect() as connection:
            transformation = connection.execute(
                """
                SELECT transformation_run_id
                FROM clean_data.transformation_runs
                WHERE status = 'success'
                ORDER BY finished_at DESC, transformation_run_id DESC
                LIMIT 1
                """
            ).fetchone()
            transformation_run_id = transformation[0] if transformation else None
            connection.execute(
                """
                INSERT INTO quality.gate_runs (
                    gate_run_id, transformation_run_id, started_at, status
                ) VALUES (%s, %s, %s, 'running')
                """,
                (run_id, transformation_run_id, started_at),
            )

        try:
            with self.connect() as connection:
                with connection.transaction():
                    connection.execute(
                        "SELECT pg_advisory_xact_lock(hashtext('olist_phase4_quality_gate'))"
                    )
                    rules = connection.execute(
                        """
                        SELECT rule_id, rule_key, severity, check_sql,
                               comparison, expected_value
                        FROM quality.gate_rules
                        WHERE enabled
                        ORDER BY sort_order, rule_id
                        """
                    ).fetchall()
                    if not rules:
                        raise RuntimeError("No enabled quality-gate rules are configured")

                    blocking_failures = 0
                    warning_failures = 0
                    for rule_id, rule_key, severity, check_sql, comparison, expected in rules:
                        row = connection.execute(check_sql).fetchone()
                        if row is None or len(row) != 1 or row[0] is None:
                            raise RuntimeError(
                                f"Quality rule {rule_key!r} did not return one numeric value"
                            )
                        observed = Decimal(str(row[0]))
                        expected_value = Decimal(str(expected))
                        passed = compare_numeric(observed, comparison, expected_value)
                        if not passed and severity == "blocking":
                            blocking_failures += 1
                        elif not passed:
                            warning_failures += 1
                        connection.execute(
                            """
                            INSERT INTO quality.gate_results (
                                gate_run_id, rule_id, observed_value, expected_value,
                                comparison, passed, severity
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                run_id,
                                rule_id,
                                observed,
                                expected_value,
                                comparison,
                                passed,
                                severity,
                            ),
                        )
                        LOGGER.info(
                            "Quality rule rule=%s severity=%s observed=%s comparison=%s "
                            "expected=%s passed=%s",
                            rule_key,
                            severity,
                            observed,
                            comparison,
                            expected_value,
                            passed,
                        )

                    status = "passed" if blocking_failures == 0 else "failed"
                    connection.execute(
                        """
                        UPDATE quality.gate_runs
                        SET finished_at = clock_timestamp(), status = %s,
                            rules_evaluated = %s, blocking_failures = %s,
                            warning_failures = %s
                        WHERE gate_run_id = %s
                        """,
                        (
                            status,
                            len(rules),
                            blocking_failures,
                            warning_failures,
                            run_id,
                        ),
                    )
            return QualityGateResult(
                run_id=run_id,
                status=status,
                rules_evaluated=len(rules),
                blocking_failures=blocking_failures,
                warning_failures=warning_failures,
                duration_seconds=time.monotonic() - started_clock,
            )
        except Exception as exc:
            error_message = f"{type(exc).__name__}: {exc}"[:4000]
            with self.connect() as connection:
                connection.execute(
                    """
                    UPDATE quality.gate_runs
                    SET finished_at = clock_timestamp(), status = 'error', error_message = %s
                    WHERE gate_run_id = %s
                    """,
                    (error_message, run_id),
                )
            return QualityGateResult(
                run_id=run_id,
                status="error",
                rules_evaluated=0,
                blocking_failures=0,
                warning_failures=0,
                duration_seconds=time.monotonic() - started_clock,
                error_message=error_message,
            )
