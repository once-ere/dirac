from __future__ import annotations

import unittest
from pathlib import Path

from scripts import check_spinor_cosmology


class SpinorCosmologyOutputTests(unittest.TestCase):
    def test_committed_output_is_self_consistent(self) -> None:
        repository_root = Path(__file__).resolve().parent.parent
        report = check_spinor_cosmology.verify_output(
            repository_root / "artifacts" / "spinor-cosmology",
            None,
            repository_root / "artifacts" / "exact" / "cl44-seed.json",
        )
        self.assertEqual(
            len(report["checks"]),
            check_spinor_cosmology.EXPECTED_CHECK_COUNT,
        )
        self.assertEqual(
            [name for name, passed in report["checks"].items() if not passed],
            [],
        )


if __name__ == "__main__":
    unittest.main()