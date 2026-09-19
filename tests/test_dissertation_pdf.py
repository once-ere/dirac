from __future__ import annotations

import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from scripts import check_dissertation_pdf


class DissertationPdfTests(unittest.TestCase):
    def test_committed_pdf_is_self_consistent(self) -> None:
        repository_root = Path(__file__).resolve().parent.parent
        report = check_dissertation_pdf.verify_pdf(
            repository_root / "dissertation" / "dirac-triality.pdf",
            None,
            13,
            612.0,
            792.0,
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