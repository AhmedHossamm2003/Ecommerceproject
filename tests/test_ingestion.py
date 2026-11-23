from __future__ import annotations

import sys
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ingestion.database import LoadResult  # noqa: E402
from ingestion.raw_loader import RawLoader  # noqa: E402


class MemoryDatabase:
    def __init__(self) -> None:
        self.successful_hashes: dict[tuple[str, str], int] = {}
        self.metadata: list[dict[str, object]] = []
        self.payloads: list[dict[str, str]] = []

    def load_file(self, source, rows, force=False):
        key = (source.filename, source.sha256)
        run_id = uuid.uuid4()
        if key in self.successful_hashes and not force:
            count = self.successful_hashes[key]
            self.metadata.append({"run_id": run_id, "status": "skipped", "inserted": 0})
            return LoadResult(run_id, source.filename, "skipped", 0, 0, count, 0.0)
        loaded = [payload for _, payload in rows]
        self.payloads.extend(loaded)
        self.successful_hashes[key] = len(loaded)
        self.metadata.append(
            {"run_id": run_id, "status": "success", "inserted": len(loaded)}
        )
        return LoadResult(
            run_id, source.filename, "success", len(loaded), len(loaded), 0, 0.0
        )


class FailingDatabase:
    def load_file(self, source, rows, force=False):
        next(iter(rows))
        return LoadResult(
            uuid.uuid4(),
            source.filename,
            "failed",
            1,
            0,
            0,
            0.0,
            "simulated database failure",
        )


class RawLoaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = ROOT / "tests" / "fixtures" / "synthetic_orders.csv"

    def test_repeated_execution_skips_identical_file_by_default(self) -> None:
        database = MemoryDatabase()
        loader = RawLoader(database)

        first = loader.load(self.fixture)
        second = loader.load(self.fixture)

        self.assertEqual(first.status, "success")
        self.assertEqual(second.status, "skipped")
        self.assertEqual(len(database.payloads), 3)
        self.assertEqual([item["status"] for item in database.metadata], ["success", "skipped"])

    def test_force_preserves_prior_run_and_adds_another(self) -> None:
        database = MemoryDatabase()
        loader = RawLoader(database)
        loader.load(self.fixture)
        forced = loader.load(self.fixture, force=True)
        self.assertEqual(forced.status, "success")
        self.assertEqual(len(database.payloads), 6)

    def test_database_failure_is_not_reported_as_success(self) -> None:
        result = RawLoader(FailingDatabase()).load(self.fixture)
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.records_inserted, 0)
        self.assertIn("database failure", result.error_message)


if __name__ == "__main__":
    unittest.main()
