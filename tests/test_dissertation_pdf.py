from __future__ import annotations

import unittest
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


if __name__ == "__main__":
    unittest.main()