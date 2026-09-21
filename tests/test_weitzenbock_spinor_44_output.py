from __future__ import annotations

import csv
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts import check_weitzenbock_spinor_44


class WeitzenbockSpinor44OutputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository_root = Path(__file__).resolve().parent.parent
        self.output = (
            self.repository_root
            / "artifacts"
            / "weitzenbock-spinor-44"
        )
        self.weitzenbock = (
            self.repository_root
            / "artifacts"
            / "weitzenbock-spin-geometry"
            / "geometry.json"
        )
        self.curved = (
            self.repository_root
            / "artifacts"
            / "curved-spin-geometry"
            / "geometry.json"
        )
        self.clifford = (
            self.repository_root
            / "artifacts"
            / "exact"
            / "cl44-seed.json"
        )
        self.baseline = (
            self.repository_root / "artifacts" / "einstein-spinor-44"
        )

    def verify(
        self,
        output: Path,
        *,
        require_canonical_hash: bool = True,
    ) -> dict[str, object]:
        return check_weitzenbock_spinor_44.verify_output(
            output,
            None,
            None,
            self.weitzenbock,
            self.curved,
            self.clifford,
            self.baseline,
            require_canonical_hash=require_canonical_hash,
        )

    def test_committed_output_is_self_consistent(self) -> None:
        report = self.verify(self.output)
        self.assertEqual(
            len(report["checks"]),
            check_weitzenbock_spinor_44.EXPECTED_CHECK_COUNT,
        )
        self.assertEqual(
            [name for name, passed in report["checks"].items() if not passed],
            [],
        )

    def test_checker_rejects_mutated_torsion_scalar(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            mutated = Path(temporary_directory) / "output"
            shutil.copytree(self.output, mutated)
            history = mutated / "history.csv"
            with history.open("r", encoding="utf-8", newline="") as source:
                reader = csv.DictReader(source)
                rows = list(reader)
                fieldnames = reader.fieldnames
            rows[0]["torsion_scalar"] = "0.0"
            with history.open("w", encoding="utf-8", newline="") as target:
                writer = csv.DictWriter(target, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            report = self.verify(
                mutated,
                require_canonical_hash=False,
            )
        self.assertFalse(
            report["checks"]["recordedTeleparallelValues"]
        )


if __name__ == "__main__":
    unittest.main()
