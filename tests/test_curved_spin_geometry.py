from __future__ import annotations

import unittest
from pathlib import Path

from scripts import check_curved_spin_geometry


class CurvedSpinGeometryTests(unittest.TestCase):
    def test_fixture_passes_independent_checks(self) -> None:
        repository_root = Path(__file__).resolve().parent.parent
        report = check_curved_spin_geometry.verify_fixture(
            repository_root
            / "artifacts"
            / "curved-spin-geometry"
            / "geometry.json",
            repository_root / "artifacts" / "exact" / "cl44-seed.json",
            repository_root
            / "artifacts"
            / "curved-spin-geometry"
            / "wolfram-report.json",
            repository_root / "wolfram" / "Cl44.wl",
            repository_root / "wolfram" / "CurvedSpinGeometry.wl",
        )
        self.assertEqual(
            len(report["checks"]),
            check_curved_spin_geometry.EXPECTED_CHECK_COUNT,
        )
        self.assertEqual(
            [name for name, passed in report["checks"].items() if not passed],
            [],
        )


if __name__ == "__main__":
    unittest.main()
