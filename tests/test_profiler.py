from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ingestion.profiler import profile_file, write_profile_reports  # noqa: E402


class ProfilerTests(unittest.TestCase):
    def test_full_missing_duplicate_and_invalid_calculations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            path = Path(temporary_dir) / "olist_orders_dataset.csv"
            path.write_text(
                "order_id,customer_id,order_status,order_purchase_timestamp\n"
                "a,c1,delivered,2017-01-01 10:00:00\n"
                "b,c2,unexpected,not-a-date\n"
                "b,c2,unexpected,not-a-date\n"
                ",c3,shipped,2017-01-03 12:00:00\n",
                encoding="utf-8",
            )

            profile = profile_file(path)
            columns = {column.name: column for column in profile.columns}

            self.assertEqual(profile.row_count, 4)
            self.assertEqual(profile.duplicate_rows, 1)
            self.assertEqual(columns["order_id"].missing_count, 1)
            self.assertEqual(columns["order_id"].empty_identifier_count, 1)
            self.assertEqual(columns["order_purchase_timestamp"].invalid_date_count, 2)
            self.assertEqual(columns["order_status"].invalid_category_count, 2)
            self.assertIn("duplicate-key rows=1", profile.candidate_key_results[0])

    def test_writes_markdown_and_csv_reports(self) -> None:
        fixture = ROOT / "tests" / "fixtures" / "synthetic_orders.csv"
        with tempfile.TemporaryDirectory() as temporary_dir:
            markdown_path, csv_path = write_profile_reports(
                [profile_file(fixture)], Path(temporary_dir)
            )
            self.assertTrue(markdown_path.is_file())
            self.assertTrue(csv_path.is_file())
            self.assertIn("VERIFIED", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
