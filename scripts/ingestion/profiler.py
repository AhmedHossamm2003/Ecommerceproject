"""Full, streaming initial profile of the unmodified Olist CSV sources."""

from __future__ import annotations

import csv
import hashlib
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .csv_reader import SourceFile, describe_source, read_csv_rows


NULL_MARKERS = {"", "null", "none", "na", "n/a", "nan"}
INTEGER_RE = re.compile(r"^[+-]?\d+$")
DECIMAL_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$")
STATE_RE = re.compile(r"^[A-Z]{2}$")
DATE_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d")

CANDIDATE_KEYS: dict[str, tuple[tuple[str, ...], ...]] = {
    "olist_orders_dataset.csv": (("order_id",),),
    "olist_order_items_dataset.csv": (("order_id", "order_item_id"),),
    "olist_customers_dataset.csv": (("customer_id",),),
    "olist_products_dataset.csv": (("product_id",),),
    "olist_order_payments_dataset.csv": (("order_id", "payment_sequential"),),
    "olist_order_reviews_dataset.csv": (("review_id",), ("review_id", "order_id")),
    "olist_sellers_dataset.csv": (("seller_id",),),
    "olist_geolocation_dataset.csv": (),
    "product_category_name_translation.csv": (("product_category_name",),),
}

NUMERIC_COLUMNS = {
    "order_item_id",
    "price",
    "freight_value",
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
    "payment_sequential",
    "payment_installments",
    "payment_value",
    "review_score",
    "geolocation_lat",
    "geolocation_lng",
}

DATE_COLUMNS = {
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
    "shipping_limit_date",
    "review_creation_date",
    "review_answer_timestamp",
}

IDENTIFIER_COLUMNS = {
    "order_id",
    "customer_id",
    "customer_unique_id",
    "product_id",
    "seller_id",
    "review_id",
    "product_category_name",
}

STATE_COLUMNS = {"customer_state", "seller_state", "geolocation_state"}
ORDER_STATUSES = {
    "approved",
    "canceled",
    "created",
    "delivered",
    "invoiced",
    "processing",
    "shipped",
    "unavailable",
}


@dataclass
class ColumnProfile:
    name: str
    missing_count: int = 0
    observed_types: set[str] = field(default_factory=set)
    invalid_numeric_count: int = 0
    invalid_date_count: int = 0
    empty_identifier_count: int = 0
    whitespace_count: int = 0
    invalid_category_count: int = 0
    samples: list[str] = field(default_factory=list)
    _sample_seen: set[str] = field(default_factory=set, repr=False)

    @property
    def inferred_type(self) -> str:
        if not self.observed_types:
            return "UNKNOWN (all values missing)"
        if self.observed_types <= {"INTEGER"}:
            return "INTEGER"
        if self.observed_types <= {"INTEGER", "NUMERIC"}:
            return "NUMERIC"
        if self.observed_types <= {"DATE"}:
            return "DATE"
        if self.observed_types <= {"DATE", "TIMESTAMP"}:
            return "TIMESTAMP"
        return "TEXT"

    @property
    def issue_count(self) -> int:
        return (
            self.invalid_numeric_count
            + self.invalid_date_count
            + self.empty_identifier_count
            + self.whitespace_count
            + self.invalid_category_count
        )

    def add_sample(self, value: str) -> None:
        if len(self.samples) < 3 and value not in self._sample_seen:
            self.samples.append(value)
            self._sample_seen.add(value)


@dataclass
class FileProfile:
    source: SourceFile
    row_count: int
    columns: list[ColumnProfile]
    duplicate_rows: int
    candidate_key_results: list[str]


def is_missing(value: str) -> bool:
    return value.strip().lower() in NULL_MARKERS


def infer_value_type(value: str) -> str:
    stripped = value.strip()
    if INTEGER_RE.fullmatch(stripped):
        return "INTEGER"
    if DECIMAL_RE.fullmatch(stripped):
        return "NUMERIC"
    # Avoid millions of expensive parser exceptions for identifiers and free text.
    looks_like_date = (
        len(stripped) in {10, 19}
        and stripped[4:5] == "-"
        and stripped[7:8] == "-"
        and (len(stripped) == 10 or stripped[10:11] == " ")
    )
    if looks_like_date:
        for date_format in DATE_FORMATS:
            try:
                datetime.strptime(stripped, date_format)
                return "TIMESTAMP" if " " in stripped else "DATE"
            except ValueError:
                continue
    return "TEXT"


def _is_valid_decimal(value: str) -> bool:
    try:
        number = Decimal(value)
    except InvalidOperation:
        return False
    return number.is_finite()


def _is_valid_date(value: str) -> bool:
    return any(_matches_date(value, date_format) for date_format in DATE_FORMATS)


def _matches_date(value: str, date_format: str) -> bool:
    try:
        datetime.strptime(value, date_format)
        return True
    except ValueError:
        return False


def _invalid_category(column: str, value: str) -> bool:
    if column in STATE_COLUMNS:
        return STATE_RE.fullmatch(value) is None
    if column == "order_status":
        return value not in ORDER_STATUSES
    if column == "review_score" and _is_valid_decimal(value):
        return not (Decimal("1") <= Decimal(value) <= Decimal("5"))
    if column == "geolocation_lat" and _is_valid_decimal(value):
        return not (Decimal("-90") <= Decimal(value) <= Decimal("90"))
    if column == "geolocation_lng" and _is_valid_decimal(value):
        return not (Decimal("-180") <= Decimal(value) <= Decimal("180"))
    return False


def profile_file(path: Path) -> FileProfile:
    source = describe_source(path)
    row_hashes: set[bytes] = set()
    duplicate_rows = 0
    row_count = 0
    columns: list[str] | None = None
    column_profiles: dict[str, ColumnProfile] = {}
    key_specs = CANDIDATE_KEYS.get(path.name, ())
    key_seen = {key: set() for key in key_specs}
    key_nulls: Counter[tuple[str, ...]] = Counter()
    key_duplicates: Counter[tuple[str, ...]] = Counter()

    for source_row_number, row in read_csv_rows(path):
        del source_row_number
        if columns is None:
            columns = list(row)
            column_profiles = {column: ColumnProfile(column) for column in columns}
        row_count += 1
        ordered_values = tuple(row[column] for column in columns)
        digest = hashlib.blake2b(
            "\x1f".join(ordered_values).encode("utf-8"), digest_size=16
        ).digest()
        if digest in row_hashes:
            duplicate_rows += 1
        else:
            row_hashes.add(digest)

        for column, value in row.items():
            profile = column_profiles[column]
            stripped = value.strip()
            if is_missing(value):
                profile.missing_count += 1
                if column in IDENTIFIER_COLUMNS:
                    profile.empty_identifier_count += 1
                continue
            profile.observed_types.add(infer_value_type(value))
            profile.add_sample(value)
            if value != stripped:
                profile.whitespace_count += 1
            if column in NUMERIC_COLUMNS and not _is_valid_decimal(stripped):
                profile.invalid_numeric_count += 1
            if column in DATE_COLUMNS and not _is_valid_date(stripped):
                profile.invalid_date_count += 1
            if _invalid_category(column, stripped):
                profile.invalid_category_count += 1

        for key in key_specs:
            values = tuple(row[column] for column in key)
            if any(is_missing(value) for value in values):
                key_nulls[key] += 1
            elif values in key_seen[key]:
                key_duplicates[key] += 1
            else:
                key_seen[key].add(values)

    if columns is None:
        # Force header validation and support valid header-only test fixtures.
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            columns = next(csv.reader(stream), [])
        column_profiles = {column: ColumnProfile(column) for column in columns}

    key_results = []
    for key in key_specs:
        label = ", ".join(key)
        status = "PASS" if not key_nulls[key] and not key_duplicates[key] else "WARN"
        key_results.append(
            f"{status}: ({label}); missing-key rows={key_nulls[key]:,}; "
            f"duplicate-key rows={key_duplicates[key]:,}"
        )
    if not key_specs:
        key_results.append("NOT TESTED: no candidate business key is assumed")

    return FileProfile(
        source=source,
        row_count=row_count,
        columns=[column_profiles[column] for column in columns],
        duplicate_rows=duplicate_rows,
        candidate_key_results=key_results,
    )


def profile_files(paths: list[Path]) -> list[FileProfile]:
    return [profile_file(path) for path in paths]


def _escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_profile_reports(profiles: list[FileProfile], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / "phase2_data_profile.md"
    csv_path = output_dir / "phase2_data_profile.csv"
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# Phase 2 Initial Data Profile",
        "",
        "**Status:** VERIFIED AGAINST THE LOCAL UNMODIFIED CSV FILES",
        "",
        f"**Generated:** {generated_at}",
        "",
        "This is a full streaming profile, not a sample. Empty strings and the case-insensitive "
        "markers `null`, `none`, `na`, `n/a`, and `nan` are counted as missing for profiling "
        "only. Raw ingestion preserves the original parsed strings, including empty strings.",
        "",
        "## File summary",
        "",
        "| Source file | Rows | Columns | Exact duplicate rows | Size (bytes) | SHA-256 |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for profile in profiles:
        lines.append(
            f"| `{profile.source.filename}` | {profile.row_count:,} | {len(profile.columns):,} | "
            f"{profile.duplicate_rows:,} | {profile.source.size_bytes:,} | "
            f"`{profile.source.sha256}` |"
        )

    for profile in profiles:
        lines.extend(
            [
                "",
                f"## `{profile.source.filename}`",
                "",
                "| Column | Inferred type | Missing | Missing % | Invalid numeric | Invalid date | "
                "Empty identifier | Whitespace | Invalid category/range | Samples |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for column in profile.columns:
            missing_percentage = (
                (column.missing_count / profile.row_count * 100) if profile.row_count else 0
            )
            lines.append(
                f"| `{column.name}` | {column.inferred_type} | {column.missing_count:,} | "
                f"{missing_percentage:.2f}% | {column.invalid_numeric_count:,} | "
                f"{column.invalid_date_count:,} | {column.empty_identifier_count:,} | "
                f"{column.whitespace_count:,} | {column.invalid_category_count:,} | "
                f"{_escape(', '.join(column.samples) or '(none)')} |"
            )
        lines.extend(["", "Candidate business-key checks:", ""])
        lines.extend(f"- {result}" for result in profile.candidate_key_results)

    lines.extend(
        [
            "",
            "## Interpretation and limitations",
            "",
            "- Exact duplicates and candidate-key duplicates are reported, never removed.",
            "- Numeric/date checks validate parseability only; semantic cleaning belongs to Phase 3.",
            "- Category/range checks cover state-code formatting, known order statuses, review scores, "
            "and coordinate bounds. They do not assert that every semantically valid domain is complete.",
            "- A 128-bit row digest is retained during each file scan to calculate full duplicate counts "
            "without retaining every full row in memory. Hash collision risk is negligible but non-zero.",
            "- JSONB storage preserves parsed column names and string values, not exact CSV bytes, quoting, "
            "line endings, or column order. The unchanged CSV files remain the byte-level source of record.",
            "",
        ]
    )
    markdown_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")

    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "source_file",
                "row_count",
                "column_count",
                "exact_duplicate_rows",
                "source_file_size_bytes",
                "source_file_sha256",
                "column_name",
                "inferred_type",
                "missing_count",
                "missing_percentage",
                "invalid_numeric_count",
                "invalid_date_count",
                "empty_identifier_count",
                "whitespace_count",
                "invalid_category_or_range_count",
            ]
        )
        for profile in profiles:
            for column in profile.columns:
                percentage = (
                    column.missing_count / profile.row_count * 100
                    if profile.row_count
                    else 0
                )
                writer.writerow(
                    [
                        profile.source.filename,
                        profile.row_count,
                        len(profile.columns),
                        profile.duplicate_rows,
                        profile.source.size_bytes,
                        profile.source.sha256,
                        column.name,
                        column.inferred_type,
                        column.missing_count,
                        f"{percentage:.6f}",
                        column.invalid_numeric_count,
                        column.invalid_date_count,
                        column.empty_identifier_count,
                        column.whitespace_count,
                        column.invalid_category_count,
                    ]
                )
    return markdown_path, csv_path
