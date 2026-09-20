from __future__ import annotations

import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from scripts import check_dissertation_pdf


class DissertationPdfTests(unittest.TestCase):
    def test_committed_pdfs_are_self_consistent(self) -> None:
        repository_root = Path(__file__).resolve().parent.parent
        for edition, specification in check_dissertation_pdf.PDF_SPECIFICATIONS.items():
            with self.subTest(edition=edition):
                report = check_dissertation_pdf.verify_pdf(
                    repository_root / specification["path"],
                    None,
                    specification["pages"],
                    612.0,
                    792.0,
                    specification["sha256"],
                )
                self.assertEqual(
                    [name for name, passed in report["checks"].items() if not passed],
                    [],
                )

    def test_changed_pdf_bytes_fail_the_canonical_hash(self) -> None:
        repository_root = Path(__file__).resolve().parent.parent
        committed_pdf = repository_root / "dissertation" / "dirac-triality.pdf"
        with TemporaryDirectory() as temporary_directory:
            changed_pdf = Path(temporary_directory) / "changed.pdf"
            changed_pdf.write_bytes(committed_pdf.read_bytes() + b"\n")
            report = check_dissertation_pdf.verify_pdf(
                changed_pdf,
                None,
                13,
                612.0,
                792.0,
                check_dissertation_pdf.ORIGINAL_PDF_SHA256,
            )
        self.assertFalse(report["checks"]["canonicalHash"])
        self.assertTrue(
            all(
                passed
                for name, passed in report["checks"].items()
                if name != "canonicalHash"
            )
        )


if __name__ == "__main__":
    unittest.main()
