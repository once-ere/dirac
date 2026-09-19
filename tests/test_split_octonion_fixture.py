from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIRECTORY = REPOSITORY_ROOT / "scripts"
if str(SCRIPTS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIRECTORY))

import check_split_octonion_fixture  # noqa: E402


class SplitOctonionFixtureTests(unittest.TestCase):
    def test_fixture_passes_independent_exact_checks(self) -> None:
        report = check_split_octonion_fixture.verify_fixture(
            REPOSITORY_ROOT / "artifacts" / "exact" / "split-octonion.json",
            REPOSITORY_ROOT / "wolfram" / "SplitOctonion.wl",
        )
        self.assertEqual(
            len(report["checks"]),
            check_split_octonion_fixture.EXPECTED_CHECK_COUNT,
        )
        self.assertEqual(
            [name for name, passed in report["checks"].items() if not passed],
            [],
        )


if __name__ == "__main__":
    unittest.main()