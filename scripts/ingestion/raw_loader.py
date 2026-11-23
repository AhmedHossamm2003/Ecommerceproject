"""File-level ingestion orchestration and required operational logging."""

from __future__ import annotations

import logging
from pathlib import Path

from .csv_reader import describe_source, read_csv_rows
from .database import LoadResult, RawDatabase


LOGGER = logging.getLogger(__name__)


class RawLoader:
    def __init__(self, database: RawDatabase):
        self.database = database

    def load(self, path: Path, force: bool = False) -> LoadResult:
        source = describe_source(path)
        LOGGER.info(
            "Ingestion started source=%s size_bytes=%d sha256=%s force=%s",
            source.filename,
            source.size_bytes,
            source.sha256,
            force,
        )
        result = self.database.load_file(source, read_csv_rows(path), force=force)
        log = LOGGER.error if result.status == "failed" else LOGGER.info
        log(
            "Ingestion finished run_id=%s source=%s status=%s records_read=%d "
            "records_inserted=%d records_skipped=%d duration_seconds=%.3f error=%s",
            result.run_id,
            result.source_file,
            result.status,
            result.records_read,
            result.records_inserted,
            result.records_skipped,
            result.duration_seconds,
            result.error_message or "none",
        )
        return result
