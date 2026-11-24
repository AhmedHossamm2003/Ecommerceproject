#!/usr/bin/env python3
"""Create the Phase 6 Power BI-facing analytical views."""

from __future__ import annotations

import logging
import sys

from ingestion.config import Settings
from ingestion.database import RawDatabase
from ingestion.logging_config import configure_logging


LOGGER = logging.getLogger("prepare_bi")


def main() -> int:
    try:
        settings = Settings.from_environment()
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    configure_logging(settings.log_level)
    sql_path = settings.phase6_bi_sql_path
    if not sql_path.is_file():
        LOGGER.error("Phase 6 BI SQL is missing: %s", sql_path)
        return 1

    database = RawDatabase(settings)
    try:
        database.wait_until_ready()
        with database.connect() as connection:
            connection.execute(sql_path.read_text(encoding="utf-8"))
            row = connection.execute(
                "SELECT delivered_sales_revenue, delivered_orders FROM analytics.vw_executive_kpis"
            ).fetchone()
    except Exception:
        LOGGER.exception("Phase 6 BI view preparation failed")
        return 1

    LOGGER.info(
        "Phase 6 BI views ready delivered_sales_revenue=%s delivered_orders=%s",
        row[0],
        row[1],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
