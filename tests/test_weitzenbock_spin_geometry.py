from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts import check_weitzenbock_spin_geometry


class WeitzenbockSpinGeometryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository_root = Path(__file__).resolve().parent.parent
        self.fixture = (
            self.repository_root
            / "artifacts"
            / "weitzenbock-spin-geometry"
            / "geometry.json"
        )
        self.curved = (
            self.repository_root
            / "artifacts"
            / "curved-spin-geometry"
            / "geometry.json"
        )
        self.clifford = (
            self.repository_root
            / "artifacts"
            / "exact"
            / "cl44-seed.json"
        )

    def test_fixture_passes_independent_checks(self) -> None:
        report = check_weitzenbock_spin_geometry.verify_fixture(
            self.fixture,
            self.curved,
            self.clifford,
        )
        self.assertEqual(
            len(report["checks"]),
            check_weitzenbock_spin_geometry.EXPECTED_CHECK_COUNT,
        )
        self.assertEqual(
            [name for name, passed in report["checks"].items() if not passed],
            [],
        )

    def test_checker_rejects_mutated_torsion(self) -> None:
        document = json.loads(self.fixture.read_text(encoding="utf-8"))
        document["torsionNonzero"][0]["coefficient"] = "2 H"
        with tempfile.TemporaryDirectory() as temporary_directory:
            mutated = Path(temporary_directory) / "geometry.json"
            mutated.write_text(
                json.dumps(document, indent=2) + "\n",
                encoding="utf-8",
            )
            report = check_weitzenbock_spin_geometry.verify_fixture(
                mutated,
                self.curved,
                self.clifford,
                require_canonical_hash=False,
            )
        self.assertFalse(report["checks"]["torsionComponents"])


if __name__ == "__main__":
    unittest.main()
