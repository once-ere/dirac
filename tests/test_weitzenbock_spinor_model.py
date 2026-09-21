from __future__ import annotations

import unittest
from pathlib import Path

from scripts import check_weitzenbock_spinor_model


class WeitzenbockSpinorModelTests(unittest.TestCase):
    def test_exact_reduced_field_equations(self) -> None:
        repository_root = Path(__file__).resolve().parent.parent
        report = check_weitzenbock_spinor_model.verify_model(
            repository_root
            / "artifacts"
            / "weitzenbock-spin-geometry"
            / "geometry.json"
        )
        self.assertEqual(
            len(report["checks"]),
            check_weitzenbock_spinor_model.EXPECTED_CHECK_COUNT,
        )
        self.assertEqual(
            [name for name, passed in report["checks"].items() if not passed],
            [],
        )


if __name__ == "__main__":
    unittest.main()
