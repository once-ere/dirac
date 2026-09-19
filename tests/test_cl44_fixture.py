from __future__ import annotations

import unittest
from pathlib import Path

from scripts import check_cl44_fixture


class Cl44FixtureTests(unittest.TestCase):
    def test_fixture_passes_independent_exact_checks(self) -> None:
        repository_root = Path(__file__).resolve().parent.parent
        report = check_cl44_fixture.verify_fixture(
            repository_root / "artifacts" / "exact" / "cl44-seed.json",
            repository_root / "wolfram" / "Cl44.wl",
        )
        self.assertEqual(
            len(report["checks"]),
            check_cl44_fixture.EXPECTED_CHECK_COUNT,
        )
        self.assertEqual(
            [name for name, passed in report["checks"].items() if not passed],
            [],
        )


if __name__ == "__main__":
    unittest.main()