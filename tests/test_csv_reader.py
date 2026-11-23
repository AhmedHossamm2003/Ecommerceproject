from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ingestion.csv_reader import CsvSourceError, read_csv_rows  # noqa: E402


class CsvReaderTests(unittest.TestCase):
    def test_parses_rows_and_preserves_source_strings(self) -> None:
        fixture = ROOT / "tests" / "fixtures" / "synthetic_orders.csv"
        original_bytes = fixture.read_bytes()

        rows = list(read_csv_rows(fixture))

        self.assertEqual(rows[0][0], 1)
        self.assertEqual(rows[0][1]["order_id"], "0001")
        self.assertEqual(rows[0][1]["empty_value"], "")
        self.assertEqual(rows[1][1]["empty_value"], "NA")
        self.assertEqual(fixture.read_bytes(), original_bytes)

    def test_missing_file_has_clear_error(self) -> None:
        missing = ROOT / "tests" / "fixtures" / "does_not_exist.csv"
        with self.assertRaisesRegex(FileNotFoundError, "does not exist"):
            list(read_csv_rows(missing))

    def test_malformed_row_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            path = Path(temporary_dir) / "malformed.csv"
            path.write_text("a,b\n1,2,3\n", encoding="utf-8")
            with self.assertRaisesRegex(CsvSourceError, "more fields"):
                list(read_csv_rows(path))


if __name__ == "__main__":
    unittest.main()
