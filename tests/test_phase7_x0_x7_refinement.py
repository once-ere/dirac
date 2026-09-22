from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts import check_phase7_x0_x7_reports


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent


class Phase7X0X7RefinementTests(unittest.TestCase):
    def test_every_semantic_claim_check_passes(self) -> None:
        report = check_phase7_x0_x7_reports.verify_reports()
        self.assertEqual(
            [name for name, passed in report["checks"].items() if not passed],
            [],
        )
        self.assertEqual(report["measurements"]["spinorEquationCount"], 16)
        self.assertEqual(report["measurements"]["diagonalEinsteinCount"], 8)
        self.assertEqual(
            report["measurements"]["offDiagonalEinsteinCount"], 28
        )

    def test_checker_rejects_reintroduced_matrix_sum(self) -> None:
        components_path = (
            REPOSITORY_ROOT
            / "provenance"
            / "EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.md"
        )
        with tempfile.TemporaryDirectory() as root:
            mutated_path = Path(root) / components_path.name
            mutated_path.write_text(
                components_path.read_text(encoding="utf-8")
                + "\n$\\sum_{B=1}^{16}X_B$\n",
                encoding="utf-8",
            )
            report = check_phase7_x0_x7_reports.verify_reports(
                components_path=mutated_path
            )
            self.assertFalse(report["checks"]["componentSumsEliminated"])

    def test_evidence_is_canonical_and_has_no_failed_checks(self) -> None:
        evidence_path = (
            REPOSITORY_ROOT
            / "refinement"
            / "phase7-x0-x7"
            / "evidence.json"
        )
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        rebuilt = (
            check_phase7_x0_x7_reports.load_evidence_builder().build_evidence()
        )
        self.assertEqual(evidence, rebuilt)
        for section in (
            "exactComponents",
            "exactModel",
            "solver",
            "numericalOutput",
        ):
            with self.subTest(section=section):
                self.assertTrue(all(evidence[section]["checks"].values()))

    def test_convergence_artifact_records_replay_and_refinement(self) -> None:
        convergence_path = (
            REPOSITORY_ROOT
            / "refinement"
            / "phase7-x0-x7"
            / "convergence.json"
        )
        convergence = json.loads(
            convergence_path.read_text(encoding="utf-8")
        )
        checks = convergence["independentVerification"]["checks"]
        measurements = convergence["independentVerification"]["measurements"]
        self.assertTrue(all(checks.values()))
        self.assertTrue(checks["repeatByteIdentity"])
        self.assertTrue(checks["refinedConvergence"])
        self.assertLess(
            measurements["maximumRefinedStateDifference"], 2.0e-9
        )
        self.assertEqual(convergence["refined"]["solverSteps"], 2294)
        self.assertEqual(convergence["refined"]["rhsEvaluations"], 2422)


if __name__ == "__main__":
    unittest.main()