from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

from scripts import build_dissertation_tex


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
ORIGINAL_MARKDOWN_SHA256 = (
    "47d280353a02c37778775720cf2459b9866510bc89ddb1bbb83c6da2d3504b97"
)
ORIGINAL_TEX_SHA256 = (
    "414b966295ae8f5092553c1af5f339683a67bf8ed77844eb118751713795bfd0"
)


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class DissertationBuilderTests(unittest.TestCase):
    def test_original_source_and_generated_tex_remain_frozen(self) -> None:
        markdown_path = REPOSITORY_ROOT / "dissertation" / "dirac-triality.md"
        tex_path = REPOSITORY_ROOT / "dissertation" / "dirac-triality.tex"
        markdown_bytes = markdown_path.read_bytes()
        tex_bytes = tex_path.read_bytes()

        self.assertEqual(sha256(markdown_bytes), ORIGINAL_MARKDOWN_SHA256)
        self.assertEqual(sha256(tex_bytes), ORIGINAL_TEX_SHA256)
        generated_bytes = build_dissertation_tex.convert(
            markdown_bytes.decode("utf-8")
        ).encode("utf-8")
        self.assertEqual(
            generated_bytes,
            tex_bytes,
        )

    def test_document_metadata_controls_the_generated_title(self) -> None:
        latex = build_dissertation_tex.convert(
            "# Student Title\n\n"
            "## A guided subtitle\n\n"
            "### Abstract\n\n"
            "A short abstract.\n"
        )

        self.assertIn(
            r"\title{Student Title\\[0.5em]\large A guided subtitle}",
            latex,
        )
        self.assertNotIn(r"\section{A guided subtitle}", latex)

    def test_missing_title_or_subtitle_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "H1 title"):
            build_dissertation_tex.convert("## Subtitle only\n")
        with self.assertRaisesRegex(ValueError, "H2 subtitle"):
            build_dissertation_tex.convert("# Title only\n")

    def test_heading_numbers_can_be_left_to_latex(self) -> None:
        latex = build_dissertation_tex.convert(
            "# Student Title\n\n"
            "## Subtitle\n\n"
            "## 1. First part\n\n"
            "### 1.1 First topic\n",
            strip_heading_numbers=True,
        )

        self.assertIn(r"\section{First part}", latex)
        self.assertIn(r"\subsection{First topic}", latex)
        self.assertNotIn(r"\section{1. First part}", latex)


if __name__ == "__main__":
    unittest.main()
