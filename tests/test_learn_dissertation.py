from __future__ import annotations

import unittest
from pathlib import Path

from scripts import check_learn_dissertation


class LearnDissertationTests(unittest.TestCase):
    def test_committed_learn_dissertation_passes_all_checks(self) -> None:
        repository_root = Path(__file__).resolve().parent.parent
        report = check_learn_dissertation.verify_document(
            repository_root / "dissertation" / "Learn_dirac-triality.md",
            repository_root / "dissertation" / "Learn_dirac-triality.tex",
            repository_root,
        )

        self.assertEqual(
            len(report["checks"]),
            check_learn_dissertation.EXPECTED_CHECK_COUNT,
        )
        self.assertEqual(
            [name for name, passed in report["checks"].items() if not passed],
            [],
        )
        self.assertEqual(report["measurements"]["exerciseCount"], 18)
        self.assertEqual(report["measurements"]["solutionCount"], 18)


if __name__ == "__main__":
    unittest.main()
