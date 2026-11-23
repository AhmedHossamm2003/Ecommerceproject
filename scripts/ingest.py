#!/usr/bin/env python3
"""CLI entry point for Phase 2 raw ingestion and initial source profiling."""

from __future__ import annotations

import argparse
import logging
import sys

from ingestion.config import EXPECTED_FILES, Settings
from ingestion.csv_reader import discover_source_files
from ingestion.database import RawDatabase
from ingestion.logging_config import configure_logging
from ingestion.profiler import profile_files, write_profile_reports
from ingestion.raw_loader import RawLoader


LOGGER = logging.getLogger("ingest")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingest unmodified Olist CSV rows into PostgreSQL raw_data JSONB storage."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Create an additional immutable run even when identical file content succeeded before.",
    )
    parser.add_argument(
        "--profile-only",
        action="store_true",
        help="Generate profiling reports without connecting to PostgreSQL.",
    )
    parser.add_argument(
        "--skip-profile",
        action="store_true",
        help="Ingest only; do not regenerate the Phase 2 profiling reports.",
    )
    parser.add_argument(
        "--strict-files",
        action="store_true",
        help="Fail when any of the nine expected source files is missing.",
    )
    return parser


def run(args: argparse.Namespace, settings: Settings) -> int:
    paths, missing = discover_source_files(settings.data_dir, EXPECTED_FILES)
    for filename in missing:
        LOGGER.warning("Expected source file missing source=%s", filename)
    if not paths:
        LOGGER.error("No supported CSV source files found in %s", settings.data_dir)
        return 2
    if missing and args.strict_files:
        LOGGER.error("Strict file validation failed missing_count=%d", len(missing))
        return 2

    failures = 0
    if not args.profile_only:
        database = RawDatabase(settings)
        try:
            database.wait_until_ready()
            database.initialize_schema()
        except Exception:
            LOGGER.exception("Database initialization failed")
            return 1
        loader = RawLoader(database)
        for path in paths:
            try:
                result = loader.load(path, force=args.force)
                failures += result.status == "failed"
            except Exception:
                # Covers permission/hash failures that happen before a database run
                # can be created. Database/COPY failures are returned as failed results.
                LOGGER.exception("Source ingestion failed source=%s", path.name)
                failures += 1

    if not args.skip_profile:
        LOGGER.info("Full source profiling started file_count=%d", len(paths))
        try:
            profiles = profile_files(paths)
            markdown_path, csv_path = write_profile_reports(
                profiles, settings.profile_output_dir
            )
            LOGGER.info(
                "Full source profiling completed markdown=%s csv=%s",
                markdown_path,
                csv_path,
            )
        except Exception:
            LOGGER.exception("Source profiling failed")
            failures += 1

    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        settings = Settings.from_environment()
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    configure_logging(settings.log_level)
    LOGGER.info("Phase 2 ingestion execution started")
    exit_code = run(args, settings)
    LOGGER.info("Phase 2 ingestion execution finished exit_code=%d", exit_code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
