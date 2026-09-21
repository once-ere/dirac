from __future__ import annotations

import unittest
from pathlib import Path

from scripts import check_einstein_spinor_model


class EinsteinSpinorModelTests(unittest.TestCase):
    def test_exact_action_and_einstein_reduction(self) -> None:
        repository_root = Path(__file__).resolve().parent.parent
        report = check_einstein_spinor_model.verify_model(
            repository_root
            / "artifacts"
            / "curved-spin-geometry"
            / "geometry.json",
            repository_root / "artifacts" / "exact" / "cl44-seed.json",
        )
        self.assertEqual(
            len(report["checks"]),
            check_einstein_spinor_model.EXPECTED_CHECK_COUNT,
        )
        self.assertEqual(
            [name for name, passed in report["checks"].items() if not passed],
            [],
        )


if __name__ == "__main__":
    unittest.main()
