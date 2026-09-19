from __future__ import annotations

import unittest
from pathlib import Path

from scripts import check_triality_transport


class TrialityTransportOutputTests(unittest.TestCase):
    def test_committed_output_is_self_consistent(self) -> None:
        repository_root = Path(__file__).resolve().parent.parent
        report = check_triality_transport.verify_output(
            repository_root / "artifacts" / "triality-transport",
            None,
            repository_root / "artifacts" / "exact" / "triality44.json",
            repository_root / "artifacts" / "exact" / "split-octonion.json",
        )
        self.assertEqual(
            len(report["checks"]),
            check_triality_transport.EXPECTED_CHECK_COUNT,
        )
        self.assertEqual(
            [name for name, passed in report["checks"].items() if not passed],
            [],
        )


if __name__ == "__main__":
    unittest.main()