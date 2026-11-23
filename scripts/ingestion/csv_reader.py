"""Strict, streaming CSV discovery and reading utilities."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


class CsvSourceError(ValueError):
    """Raised when a source CSV cannot be safely represented as row dictionaries."""


@dataclass(frozen=True)
class SourceFile:
    path: Path
    filename: str
    size_bytes: int
    sha256: str


def discover_source_files(
    data_dir: Path, expected_files: tuple[str, ...]
) -> tuple[list[Path], list[str]]:
    available: list[Path] = []
    missing: list[str] = []
    for filename in expected_files:
        path = data_dir / filename
        if path.is_file():
            available.append(path)
        else:
            missing.append(filename)
    return available, missing


def sha256_file(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Source CSV does not exist: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def describe_source(path: Path) -> SourceFile:
    if not path.is_file():
        raise FileNotFoundError(f"Source CSV does not exist: {path}")
    return SourceFile(
        path=path,
        filename=path.name,
        size_bytes=path.stat().st_size,
        sha256=sha256_file(path),
    )


def read_csv_rows(path: Path) -> Iterator[tuple[int, dict[str, str]]]:
    """Yield one-based source data row numbers and unmodified parsed string values.

    UTF-8 BOMs are removed from the first header. Empty fields remain empty strings.
    No trimming, null conversion, type conversion, filtering, or deduplication occurs.
    """

    if not path.is_file():
        raise FileNotFoundError(f"Source CSV does not exist: {path}")
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, strict=True)
            columns = reader.fieldnames
            if not columns:
                raise CsvSourceError(f"{path.name}: CSV header is missing")
            if any(column == "" for column in columns):
                raise CsvSourceError(f"{path.name}: CSV header contains an empty name")
            if len(set(columns)) != len(columns):
                raise CsvSourceError(f"{path.name}: CSV header contains duplicate names")

            for source_row_number, row in enumerate(reader, start=1):
                if None in row:
                    raise CsvSourceError(
                        f"{path.name}: row {source_row_number} has more fields than the header"
                    )
                missing_fields = [key for key, value in row.items() if value is None]
                if missing_fields:
                    raise CsvSourceError(
                        f"{path.name}: row {source_row_number} is missing fields: "
                        f"{', '.join(missing_fields)}"
                    )
                yield source_row_number, {column: row[column] for column in columns}
    except UnicodeDecodeError as exc:
        raise CsvSourceError(f"{path.name}: source is not valid UTF-8") from exc
    except csv.Error as exc:
        raise CsvSourceError(f"{path.name}: malformed CSV: {exc}") from exc
