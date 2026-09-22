from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts import build_dissertation_tex
from scripts import check_developer_summary
from scripts import check_provenance_pdf


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = REPOSITORY_ROOT / "DEVELOPER_SUMMARY.md"
TEX_PATH = REPOSITORY_ROOT / "DEVELOPER_SUMMARY.tex"
PDF_PATH = REPOSITORY_ROOT / "DEVELOPER_SUMMARY.pdf"
EXPECTED_MARKDOWN_SHA256 = (
    "ad56d4a4ab86326c4923228e4e84a102b92aecc874969e3083cbd9f2e7db8010"
)
EXPECTED_TEX_SHA256 = (
    "ffa17fcf780cbe08e6104c23a840d6ce91e833272b884c01f6ee86a87360fe2b"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DeveloperSummaryTests(unittest.TestCase):
    def test_committed_artifacts_are_canonical(self) -> None:
        markdown = SUMMARY_PATH.read_text(encoding="utf-8")
        self.assertEqual(sha256_file(SUMMARY_PATH), EXPECTED_MARKDOWN_SHA256)
        self.assertEqual(sha256_file(TEX_PATH), EXPECTED_TEX_SHA256)
        self.assertEqual(
            build_dissertation_tex.convert(
                markdown,
                strip_heading_numbers=True,
                developer_layout=True,
            ).encode("utf-8"),
            TEX_PATH.read_bytes(),
        )
        specification = check_provenance_pdf.SPECIFICATIONS[
            "developer-summary"
        ]
        report = check_provenance_pdf.check_dissertation_pdf.verify_pdf(
            PDF_PATH,
            None,
            specification["pages"],
            612.0,
            792.0,
            specification["sha256"],
        )
        self.assertTrue(all(report["checks"].values()))

    def test_committed_summary_passes_every_semantic_check(self) -> None:
        report = check_developer_summary.verify_summary()
        self.assertEqual(
            [name for name, passed in report["checks"].items() if not passed],
            [],
        )
        self.assertGreaterEqual(report["measurements"]["lineCount"], 750)
        self.assertGreaterEqual(report["measurements"]["wordCount"], 5000)
        self.assertEqual(report["measurements"]["requiredPathCount"], 27)

    def test_checker_rejects_executive_summary_substitution(self) -> None:
        text = SUMMARY_PATH.read_text(encoding="utf-8")
        mutated = text.replace(
            "# Developer Summary:",
            "# Executive Summary:",
            1,
        )
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / SUMMARY_PATH.name
            path.write_text(mutated, encoding="utf-8")
            report = check_developer_summary.verify_summary(path)
        self.assertFalse(report["checks"]["developerTitle"])
        self.assertFalse(report["checks"]["notExecutiveHeading"])

    def test_checker_rejects_missing_phase(self) -> None:
        text = SUMMARY_PATH.read_text(encoding="utf-8")
        mutated = text.replace(
            "Phase 7: `{x0,...,x7}` component refinement",
            "Final coordinate work",
            1,
        )
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / SUMMARY_PATH.name
            path.write_text(mutated, encoding="utf-8")
            report = check_developer_summary.verify_summary(path)
        self.assertFalse(report["checks"]["phaseCoverage"])

    def test_checker_rejects_corrupted_canonical_hash(self) -> None:
        text = SUMMARY_PATH.read_text(encoding="utf-8")
        canonical = check_developer_summary.ARTIFACT_HASHES[
            "artifacts/exact/cl44-seed.json"
        ]
        mutated = text.replace(canonical, "0" * 64, 1)
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / SUMMARY_PATH.name
            path.write_text(mutated, encoding="utf-8")
            report = check_developer_summary.verify_summary(path)
        self.assertFalse(report["checks"]["artifactHashes"])


if __name__ == "__main__":
    unittest.main()
