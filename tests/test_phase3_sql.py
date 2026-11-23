from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Phase3SqlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema_sql = (ROOT / "sql" / "03_phase3_schema.sql").read_text(
            encoding="utf-8"
        ).lower()
        cls.transform_sql = (ROOT / "sql" / "04_phase3_transform.sql").read_text(
            encoding="utf-8"
        ).lower()

    def test_raw_schema_is_not_destructively_modified(self) -> None:
        prohibited = (
            "truncate raw_data",
            "drop schema raw_data",
            "drop table raw_data",
            "delete from raw_data",
            "update raw_data.records",
        )
        for statement in prohibited:
            self.assertNotIn(statement, self.transform_sql)

    def test_latest_successful_raw_runs_are_selected(self) -> None:
        self.assertIn("where status = 'success'", self.transform_sql)
        self.assertIn("distinct on (source_file)", self.transform_sql)

    def test_star_schema_and_analytical_views_are_declared(self) -> None:
        required = (
            "warehouse.dim_customers",
            "warehouse.dim_products",
            "warehouse.dim_sellers",
            "warehouse.dim_date",
            "warehouse.fact_order_items",
            "analytics.vw_category_sales",
            "analytics.vw_monthly_sales",
            "analytics.vw_state_sales",
        )
        for object_name in required:
            self.assertIn(object_name, self.schema_sql)

    def test_reconciliation_guards_are_present(self) -> None:
        self.assertIn("fact row reconciliation failed", self.transform_sql)
        self.assertIn("fact revenue reconciliation failed", self.transform_sql)
        self.assertIn("geolocation occurrence reconciliation failed", self.transform_sql)


if __name__ == "__main__":
    unittest.main()
