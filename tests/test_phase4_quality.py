from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ingestion.quality_rules import compare_numeric  # noqa: E402


class Phase4QualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sql = (ROOT / "sql" / "05_phase4_quality.sql").read_text(
            encoding="utf-8"
        ).lower()

    def test_comparison_operators(self) -> None:
        self.assertTrue(compare_numeric(Decimal("1"), "eq", Decimal("1")))
        self.assertTrue(compare_numeric(Decimal("1"), "le", Decimal("2")))
        self.assertTrue(compare_numeric(Decimal("2"), "ge", Decimal("1")))
        self.assertFalse(compare_numeric(Decimal("2"), "eq", Decimal("1")))
        with self.assertRaises(ValueError):
            compare_numeric(Decimal("1"), "bad", Decimal("1"))

    def test_quality_sql_is_non_destructive_to_pipeline_layers(self) -> None:
        for schema in ("raw_data", "clean_data", "warehouse"):
            self.assertNotIn(f"truncate {schema}", self.sql)
            self.assertNotIn(f"delete from {schema}", self.sql)
            self.assertNotIn(f"update {schema}", self.sql)

    def test_default_rules_cover_required_reconciliations(self) -> None:
        required = (
            "fact_grain_unique",
            "fact_row_reconciliation",
            "fact_revenue_reconciliation",
            "fact_foreign_keys_resolved",
            "geolocation_occurrence_reconciliation",
            "analytical_views_populated",
        )
        for rule in required:
            self.assertIn(rule, self.sql)

    def test_rules_are_configurable_and_results_are_auditable(self) -> None:
        self.assertIn("enabled boolean", self.sql)
        self.assertIn("expected_value numeric", self.sql)
        self.assertIn("quality.gate_runs", self.sql)
        self.assertIn("quality.gate_results", self.sql)


if __name__ == "__main__":
    unittest.main()
