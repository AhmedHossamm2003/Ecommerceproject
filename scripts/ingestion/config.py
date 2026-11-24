"""Environment-driven configuration for the ingestion application."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


EXPECTED_FILES = (
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_products_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "product_category_name_translation.csv",
)


def _positive_int(name: str, default: int) -> int:
    raw_value = os.getenv(name, str(default))
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, received {raw_value!r}") from exc
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    profile_output_dir: Path
    schema_sql_path: Path
    phase3_schema_sql_path: Path
    phase3_transform_sql_path: Path
    phase4_quality_sql_path: Path
    phase6_bi_sql_path: Path
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    db_connect_timeout: int
    db_retry_attempts: int
    db_retry_delay_seconds: int
    log_level: str

    @classmethod
    def from_environment(cls) -> "Settings":
        root = Path(__file__).resolve().parents[2]
        settings = cls(
            data_dir=Path(os.getenv("DATA_DIR", str(root / "data" / "raw"))),
            profile_output_dir=Path(
                os.getenv("PROFILE_OUTPUT_DIR", str(root / "docs"))
            ),
            schema_sql_path=Path(
                os.getenv("SCHEMA_SQL_PATH", str(root / "sql" / "02_raw_storage.sql"))
            ),
            phase3_schema_sql_path=Path(
                os.getenv(
                    "PHASE3_SCHEMA_SQL_PATH",
                    str(root / "sql" / "03_phase3_schema.sql"),
                )
            ),
            phase3_transform_sql_path=Path(
                os.getenv(
                    "PHASE3_TRANSFORM_SQL_PATH",
                    str(root / "sql" / "04_phase3_transform.sql"),
                )
            ),
            phase4_quality_sql_path=Path(
                os.getenv(
                    "PHASE4_QUALITY_SQL_PATH",
                    str(root / "sql" / "05_phase4_quality.sql"),
                )
            ),
            phase6_bi_sql_path=Path(
                os.getenv(
                    "PHASE6_BI_SQL_PATH",
                    str(root / "sql" / "06_phase6_bi.sql"),
                )
            ),
            db_host=os.getenv("DB_HOST", "localhost"),
            db_port=_positive_int("DB_PORT", 5432),
            db_name=os.getenv("POSTGRES_DB", "ecommerce_db"),
            db_user=os.getenv("POSTGRES_USER", "ecommerce_user"),
            db_password=os.getenv("POSTGRES_PASSWORD", ""),
            db_connect_timeout=_positive_int("DB_CONNECT_TIMEOUT", 5),
            db_retry_attempts=_positive_int("DB_RETRY_ATTEMPTS", 12),
            db_retry_delay_seconds=_positive_int("DB_RETRY_DELAY_SECONDS", 5),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        required = {
            "DB_HOST": self.db_host,
            "POSTGRES_DB": self.db_name,
            "POSTGRES_USER": self.db_user,
            "POSTGRES_PASSWORD": self.db_password,
        }
        empty = [name for name, value in required.items() if not value]
        if empty:
            raise ValueError(f"Required environment values are empty: {', '.join(empty)}")

    @property
    def connection_kwargs(self) -> dict[str, object]:
        return {
            "host": self.db_host,
            "port": self.db_port,
            "dbname": self.db_name,
            "user": self.db_user,
            "password": self.db_password,
            "connect_timeout": self.db_connect_timeout,
            "application_name": "olist_phase2_ingestion",
        }
