#!/usr/bin/env python3
"""Create a measured Markdown profile for the unmodified Olist CSV files.

Standard-library only. The script reads data/raw and writes docs/dataset_profile.md.
It never writes to or changes a source CSV.
"""

from __future__ import annotations

import csv
import hashlib
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUTPUT = ROOT / "docs" / "dataset_profile.md"

EXPECTED_FILES = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_products_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "product_category_name_translation.csv",
]

CANDIDATE_KEYS = {
    "olist_orders_dataset.csv": [("order_id",)],
    "olist_order_items_dataset.csv": [("order_id", "order_item_id")],
    "olist_customers_dataset.csv": [("customer_id",)],
    "olist_products_dataset.csv": [("product_id",)],
    "olist_order_payments_dataset.csv": [("order_id", "payment_sequential")],
    "olist_order_reviews_dataset.csv": [("review_id",), ("review_id", "order_id")],
    "olist_sellers_dataset.csv": [("seller_id",)],
    "olist_geolocation_dataset.csv": [],
    "product_category_name_translation.csv": [("product_category_name",)],
}

FOREIGN_KEYS = [
    ("olist_orders_dataset.csv", ("customer_id",), "olist_customers_dataset.csv", ("customer_id",)),
    ("olist_order_items_dataset.csv", ("order_id",), "olist_orders_dataset.csv", ("order_id",)),
    ("olist_order_items_dataset.csv", ("product_id",), "olist_products_dataset.csv", ("product_id",)),
    ("olist_order_items_dataset.csv", ("seller_id",), "olist_sellers_dataset.csv", ("seller_id",)),
    ("olist_order_payments_dataset.csv", ("order_id",), "olist_orders_dataset.csv", ("order_id",)),
    ("olist_order_reviews_dataset.csv", ("order_id",), "olist_orders_dataset.csv", ("order_id",)),
    ("olist_products_dataset.csv", ("product_category_name",), "product_category_name_translation.csv", ("product_category_name",)),
]

NULL_MARKERS = {"", "null", "none", "na", "n/a", "nan"}
INTEGER_RE = re.compile(r"^[+-]?\d+$")
DECIMAL_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\d*\.\d+)$")
TIMESTAMP_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d")


@dataclass
class FileProfile:
    filename: str
    size_bytes: int
    sha256: str
    row_count: int
    columns: list[str]
    inferred_types: dict[str, str]
    null_counts: dict[str, int]
    duplicate_rows: int
    key_results: list[str]
    distinct_samples: dict[str, list[str]]


def is_null(value: str | None) -> bool:
    return value is None or value.strip().lower() in NULL_MARKERS


def value_type(value: str) -> str:
    stripped = value.strip()
    if INTEGER_RE.fullmatch(stripped):
        return "INTEGER"
    if DECIMAL_RE.fullmatch(stripped):
        return "NUMERIC"
    for fmt in TIMESTAMP_FORMATS:
        try:
            datetime.strptime(stripped, fmt)
            return "TIMESTAMP" if " " in stripped else "DATE"
        except ValueError:
            pass
    return "TEXT"


def merge_types(types: set[str]) -> str:
    if not types:
        return "UNKNOWN (all values null)"
    if types <= {"INTEGER"}:
        return "INTEGER"
    if types <= {"INTEGER", "NUMERIC"}:
        return "NUMERIC"
    if types <= {"DATE"}:
        return "DATE"
    if types <= {"DATE", "TIMESTAMP"}:
        return "TIMESTAMP"
    return "TEXT"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def profile_file(path: Path) -> FileProfile:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames or []
        if not columns:
            raise ValueError(f"{path.name}: header row is missing")

        null_counts = Counter({column: 0 for column in columns})
        observed_types = {column: set() for column in columns}
        sample_values = {column: [] for column in columns}
        sample_seen = {column: set() for column in columns}
        duplicate_hashes: set[bytes] = set()
        duplicate_rows = 0
        row_count = 0

        key_specs = CANDIDATE_KEYS.get(path.name, [])
        key_seen = {key: set() for key in key_specs}
        key_nulls = Counter()
        key_duplicates = Counter()

        for row in reader:
            row_count += 1
            ordered = tuple(row.get(column, "") for column in columns)
            row_digest = hashlib.blake2b(
                "\x1f".join(ordered).encode("utf-8"), digest_size=16
            ).digest()
            if row_digest in duplicate_hashes:
                duplicate_rows += 1
            else:
                duplicate_hashes.add(row_digest)

            for column in columns:
                value = row.get(column, "")
                if is_null(value):
                    null_counts[column] += 1
                    continue
                observed_types[column].add(value_type(value))
                if len(sample_values[column]) < 5 and value not in sample_seen[column]:
                    sample_values[column].append(value)
                    sample_seen[column].add(value)

            for key in key_specs:
                values = tuple(row.get(column, "") for column in key)
                if any(is_null(value) for value in values):
                    key_nulls[key] += 1
                elif values in key_seen[key]:
                    key_duplicates[key] += 1
                else:
                    key_seen[key].add(values)

    key_results = []
    for key in key_specs:
        label = ", ".join(f"`{column}`" for column in key)
        status = "PASS" if key_nulls[key] == 0 and key_duplicates[key] == 0 else "FAIL"
        key_results.append(
            f"{status}: ({label}) - null-key rows: {key_nulls[key]:,}; "
            f"duplicate-key rows: {key_duplicates[key]:,}"
        )
    if not key_specs:
        key_results.append("No primary key assumed; uniqueness requires a separate design decision.")

    return FileProfile(
        filename=path.name,
        size_bytes=path.stat().st_size,
        sha256=sha256_file(path),
        row_count=row_count,
        columns=columns,
        inferred_types={column: merge_types(observed_types[column]) for column in columns},
        null_counts=dict(null_counts),
        duplicate_rows=duplicate_rows,
        key_results=key_results,
        distinct_samples=sample_values,
    )


def collect_key_values(path: Path, columns: tuple[str, ...]) -> set[tuple[str, ...]]:
    values: set[tuple[str, ...]] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        missing = [column for column in columns if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path.name}: missing columns for relationship test: {missing}")
        for row in reader:
            item = tuple(row[column] for column in columns)
            if not any(is_null(value) for value in item):
                values.add(item)
    return values


def foreign_key_results() -> list[str]:
    results = []
    cache: dict[tuple[str, tuple[str, ...]], set[tuple[str, ...]]] = {}
    for child_file, child_cols, parent_file, parent_cols in FOREIGN_KEYS:
        child_key = (child_file, child_cols)
        parent_key = (parent_file, parent_cols)
        cache.setdefault(child_key, collect_key_values(RAW_DIR / child_file, child_cols))
        cache.setdefault(parent_key, collect_key_values(RAW_DIR / parent_file, parent_cols))
        unmatched = cache[child_key] - cache[parent_key]
        status = "PASS" if not unmatched else "WARN"
        results.append(
            f"- **{status}** `{child_file}` ({', '.join(child_cols)}) -> "
            f"`{parent_file}` ({', '.join(parent_cols)}): "
            f"{len(unmatched):,} distinct unmatched non-null key(s)"
        )
    return results


def escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_report(profiles: list[FileProfile]) -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Dataset Profiling Report",
        "",
        "**Profile status:** VERIFIED AGAINST LOCAL CSV FILES",
        "",
        f"**Generated:** {generated}",
        "",
        "**Method:** `scripts/profile_dataset.py` streamed the unmodified files in `data/raw/`. "
        "Counts below are measured locally. SHA-256 values identify the exact inputs.",
        "",
        "Dataset source: [Brazilian E-Commerce Public Dataset by Olist]"
        "(https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)",
        "",
        "## File inventory",
        "",
        "| Filename | Rows | Columns | Exact duplicate rows | Size (bytes) | SHA-256 |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for profile in profiles:
        lines.append(
            f"| `{profile.filename}` | {profile.row_count:,} | {len(profile.columns):,} | "
            f"{profile.duplicate_rows:,} | {profile.size_bytes:,} | `{profile.sha256}` |"
        )

    lines.extend(["", "## Per-file columns, inferred types, and missing values", ""])
    for profile in profiles:
        lines.extend(
            [
                f"### `{profile.filename}`",
                "",
                "| Column | Inferred type | Missing values | Non-null sample values (up to 5) |",
                "|---|---|---:|---|",
            ]
        )
        for column in profile.columns:
            samples = ", ".join(escape(value) for value in profile.distinct_samples[column])
            lines.append(
                f"| `{column}` | {profile.inferred_types[column]} | "
                f"{profile.null_counts[column]:,} | {samples or '(none)'} |"
            )
        lines.extend(["", "Candidate-key tests:", ""])
        lines.extend(f"- {result}" for result in profile.key_results)
        lines.append("")

    lines.extend(["## Candidate foreign-key tests", ""])
    lines.extend(foreign_key_results())
    lines.extend(
        [
            "",
            "## Potential data-quality problems identified by the profile",
            "",
        ]
    )
    warnings = []
    for profile in profiles:
        if profile.duplicate_rows:
            warnings.append(
                f"- `{profile.filename}` contains {profile.duplicate_rows:,} repeated exact row(s)."
            )
        missing_columns = [
            (column, count) for column, count in profile.null_counts.items() if count
        ]
        if missing_columns:
            summary = ", ".join(
                f"`{column}`={count:,}" for column, count in missing_columns
            )
            warnings.append(f"- `{profile.filename}` has missing values: {summary}.")
        for key_result in profile.key_results:
            if key_result.startswith("FAIL"):
                warnings.append(f"- `{profile.filename}` candidate key issue: {key_result}")
    if warnings:
        lines.extend(warnings)
    else:
        lines.append("- No null, duplicate-row, or candidate-key warnings were detected by these checks.")
    lines.extend(
        [
            "- Interpret foreign-key warnings carefully for optional category translations; quantify and map unknown members rather than dropping facts.",
            "- This structural profile does not replace semantic validation of status/date order, monetary ranges, geographic consistency, or join reconciliation.",
            "",
            "## Reproducibility",
            "",
            "Run `python scripts/profile_dataset.py` again after any source-file change. Compare SHA-256 values before treating two profiles as equivalent.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    missing = [filename for filename in EXPECTED_FILES if not (RAW_DIR / filename).is_file()]
    if missing:
        print("Profiling stopped: expected source files are missing:", file=sys.stderr)
        for filename in missing:
            print(f"  - {filename}", file=sys.stderr)
        print(
            "Download the official Olist dataset and place the unmodified CSV files in data/raw/.",
            file=sys.stderr,
        )
        return 2

    profiles = [profile_file(RAW_DIR / filename) for filename in EXPECTED_FILES]
    report = build_report(profiles)
    OUTPUT.write_text(report, encoding="utf-8", newline="\n")
    print(f"Wrote verified profile: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
