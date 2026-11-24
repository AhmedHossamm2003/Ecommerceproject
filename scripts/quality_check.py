#!/usr/bin/env python3
"""Execute the Phase 4 configurable quality gate."""

from __future__ import annotations

import logging
import sys

from ingestion.config import Settings
from ingestion.logging_config import configure_logging
from ingestion.quality import QualityDatabase


LOGGER = logging.getLogger("quality_check")


def main() -> int:
    try:
        settings = Settings.from_environment()
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    configure_logging(settings.log_level)
    database = QualityDatabase(settings)
    LOGGER.info("Phase 4 quality-gate execution started")
    try:
        database.wait_until_ready()
        database.initialize_quality_schema()
        result = database.run_gate()
    except Exception:
        LOGGER.exception("Phase 4 quality-gate initialization failed")
        return 1

    log = LOGGER.info if result.status == "passed" else LOGGER.error
    log(
        "Phase 4 quality gate finished run_id=%s status=%s rules=%d "
        "blocking_failures=%d warning_failures=%d duration_seconds=%.3f error=%s",
        result.run_id,
        result.status,
        result.rules_evaluated,
        result.blocking_failures,
        result.warning_failures,
        result.duration_seconds,
        result.error_message or "none",
    )
    return 0 if result.status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
