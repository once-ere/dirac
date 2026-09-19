from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIRECTORY = REPOSITORY_ROOT / "scripts"
if str(SCRIPTS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIRECTORY))

import check_triality44_fixture  # noqa: E402


class Triality44FixtureTests(unittest.TestCase):
    def test_fixture_passes_independent_exact_checks(self) -> None:
        report = check_triality44_fixture.verify_fixture(
            REPOSITORY_ROOT / "artifacts" / "exact" / "triality44.json",
            REPOSITORY_ROOT / "artifacts" / "exact" / "cl44-seed.json",
            REPOSITORY_ROOT / "artifacts" / "exact" / "split-octonion.json",
            {
                "cl44": REPOSITORY_ROOT / "wolfram" / "Cl44.wl",
                "splitOctonion": REPOSITORY_ROOT / "wolfram" / "SplitOctonion.wl",
                "triality44": REPOSITORY_ROOT / "wolfram" / "Triality44.wl",
            },
        )
        self.assertEqual(
            len(report["checks"]),
            check_triality44_fixture.EXPECTED_CHECK_COUNT,
        )
        self.assertEqual(
            [name for name, passed in report["checks"].items() if not passed],
            [],
        )


if __name__ == "__main__":
    unittest.main()