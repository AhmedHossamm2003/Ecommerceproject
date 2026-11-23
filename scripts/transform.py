#!/usr/bin/env python3
"""Execute the Phase 3 clean-layer and star-schema transformation."""

from __future__ import annotations

import logging
import sys

from ingestion.config import Settings
from ingestion.logging_config import configure_logging
from ingestion.transformation import TransformationDatabase


LOGGER = logging.getLogger("transform")


def main() -> int:
    try:
        settings = Settings.from_environment()
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    configure_logging(settings.log_level)
    database = TransformationDatabase(settings)
    LOGGER.info("Phase 3 transformation execution started")
    try:
        database.wait_until_ready()
        database.initialize_phase3_schema()
        result = database.transform()
    except Exception:
        LOGGER.exception("Phase 3 initialization failed")
        return 1

    log = LOGGER.info if result.status == "success" else LOGGER.error
    log(
        "Phase 3 transformation finished run_id=%s status=%s clean_records=%d "
        "fact_records=%d rejected_records=%d duration_seconds=%.3f error=%s",
        result.run_id,
        result.status,
        result.clean_records,
        result.fact_records,
        result.rejected_records,
        result.duration_seconds,
        result.error_message or "none",
    )
    return 0 if result.status == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
