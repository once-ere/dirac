from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts import check_einstein_spinor_44


class EinsteinSpinor44OutputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository_root = Path(__file__).resolve().parent.parent

    def test_committed_output_is_self_consistent(self) -> None:
        report = check_einstein_spinor_44.verify_output(
            self.repository_root / "artifacts" / "einstein-spinor-44",
            None,
            None,
            self.repository_root
            / "artifacts"
            / "curved-spin-geometry"
            / "geometry.json",
            self.repository_root
            / "artifacts"
            / "exact"
            / "cl44-seed.json",
        )
        self.assertEqual(
            len(report["checks"]),
            check_einstein_spinor_44.EXPECTED_CHECK_COUNT,
        )
        self.assertEqual(
            [name for name, passed in report["checks"].items() if not passed],
            [],
        )

    def test_refined_summary_requires_improvement_and_exact_stats(self) -> None:
        summary_path = (
            self.repository_root
            / "artifacts"
            / "einstein-spinor-44"
            / "summary.json"
        )
        canonical = json.loads(summary_path.read_text(encoding="utf-8"))
        canonical_errors = list(
            canonical["maximumRelativeError"].values()
        )
        refined_errors = [value / 2.0 for value in canonical_errors]
        refined = copy.deepcopy(canonical)
        refined.update(
            {
                "relativeTolerance": 1.0e-12,
                "absoluteTolerance": 1.0e-14,
                "maximumStep": 0.001,
                "solverSteps": 2294,
                "rhsEvaluations": 2422,
                "maximumRelativeError": dict(
                    zip(
                        ("condensate", "density", "friedmann"),
                        refined_errors,
                        strict=True,
                    )
                ),
            }
        )
        self.assertTrue(
            check_einstein_spinor_44.refined_summary_is_valid(
                refined,
                canonical,
                refined_errors,
                canonical_errors,
            )
        )
        self.assertFalse(
            check_einstein_spinor_44.refined_summary_is_valid(
                refined,
                canonical,
                canonical_errors,
                canonical_errors,
            )
        )
        refined["solverSteps"] -= 1
        self.assertFalse(
            check_einstein_spinor_44.refined_summary_is_valid(
                refined,
                canonical,
                refined_errors,
                canonical_errors,
            )
        )


if __name__ == "__main__":
    unittest.main()
