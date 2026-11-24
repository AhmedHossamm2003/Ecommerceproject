from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Phase5OrchestrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.flow = (ROOT / "flows" / "olist_ecommerce_pipeline.yaml").read_text(
            encoding="utf-8"
        ).lower()
        cls.compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8").lower()

    def test_flow_orders_all_pipeline_stages(self) -> None:
        positions = [
            self.flow.index("id: ingest_raw_files"),
            self.flow.index("id: build_clean_warehouse"),
            self.flow.index("id: enforce_quality_gate"),
            self.flow.index("id: prepare_bi_views"),
        ]
        self.assertEqual(positions, sorted(positions))

    def test_flow_has_retries_schedule_and_network(self) -> None:
        self.assertGreaterEqual(self.flow.count("maxattempt: 2"), 4)
        self.assertIn('cron: "0 3 * * 1"', self.flow)
        self.assertGreaterEqual(self.flow.count("networkmode: ecommerce_network"), 4)

    def test_flow_does_not_store_database_password(self) -> None:
        self.assertIn("envs.pipeline_db_password", self.flow)
        self.assertNotIn("change_me", self.flow)
        self.assertNotIn("replace_with", self.flow)

    def test_kestra_uses_persistent_storage(self) -> None:
        self.assertIn("kestra_postgres_data", self.compose)
        self.assertIn("kestra_data", self.compose)
        self.assertIn("--flow-path=/app/flows", self.compose)


class Phase6PowerBITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sql = (ROOT / "sql" / "06_phase6_bi.sql").read_text(
            encoding="utf-8"
        ).lower()
        cls.power_query = (ROOT / "powerbi" / "OlistSales.PowerQuery.m").read_text(
            encoding="utf-8"
        ).lower()
        cls.spec = (ROOT / "powerbi" / "DASHBOARD_SPEC.md").read_text(
            encoding="utf-8"
        ).lower()

    def test_bi_views_are_declared(self) -> None:
        self.assertIn("analytics.vw_executive_kpis", self.sql)
        self.assertIn("analytics.vw_pipeline_health", self.sql)

    def test_power_query_uses_only_controlled_views(self) -> None:
        required = (
            "analytics.vw_executive_kpis",
            "analytics.vw_category_sales",
            "analytics.vw_monthly_sales",
            "analytics.vw_state_sales",
            "analytics.vw_pipeline_health",
        )
        for view in required:
            self.assertIn(view, self.power_query)
        self.assertNotIn("password", self.power_query)

    def test_dashboard_answers_all_business_questions(self) -> None:
        self.assertIn("category", self.spec)
        self.assertIn("monthly", self.spec)
        self.assertIn("state", self.spec)
        self.assertIn("pipeline health", self.spec)

    def test_bi_sql_does_not_modify_pipeline_data(self) -> None:
        for operation in ("truncate ", "delete from ", "update ", "insert into "):
            self.assertNotIn(operation, self.sql)


if __name__ == "__main__":
    unittest.main()
