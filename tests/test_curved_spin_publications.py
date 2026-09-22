from __future__ import annotations

import hashlib
import re
import tempfile
import unittest
from pathlib import Path

from scripts import build_dissertation_tex
from scripts import check_provenance_pdf


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS = {
    "curved-spin-bundle": {
        "stem": "CURVED_SPIN_BUNDLE",
        "markdown_sha256": (
            "83bb78934b9b4986d8ae755319d9fb654e1c68dfc5f05ab6217839689e4184f7"
        ),
        "tex_sha256": (
            "55b94966a83b007c37543a6875210a83594165efad024f3e52571d7d4370469c"
        ),
        "required": [
            "spinor bundle",
            "g_{\\mu\\nu}=e_\\mu{}^a\\eta_{ab}e_\\nu{}^b",
            "vielbein postulate",
            "\\frac18\\omega_{\\mu ab}[\\gamma^a,\\gamma^b]",
            "\\frac72H",
            "Complete Windows commands",
            "Complete Git Bash or WSL commands",
        ],
    },
    "einstein-spinor-44": {
        "stem": "EINSTEIN_SPINOR_44",
        "markdown_sha256": (
            "0a38c49921735b27dc82e72acb8fa69ecb7f5e79c08d195a690dd00049c6fc5e"
        ),
        "tex_sha256": (
            "58d55a27362add0a73b35e5561b0500c0a2fbfe20cd17a5891c789aee5877c6c"
        ),
        "required": [
            "commuting classical real spinor",
            "No cosmological constant and no scalar field occur",
            "T_{\\mu\\nu} =-\\frac14",
            "positive-condensate cone",
            "G_{tt}=21H^2",
            "V(S)=\\frac1{20}S+\\frac{19}{20}S^{1/5}",
            "dust-like",
            "negative-pressure",
            "five-point finite differences",
            "tighter convergence run",
            "contains four tests",
            "Complete Windows commands",
            "Complete Git Bash or WSL commands",
        ],
    },
    "weitzenbock-spinor-44": {
        "stem": "WEITZENBOCK_SPINOR_44",
        "markdown_sha256": (
            "cdffe26dd1d3bc67a656769d7defb2eb991da6cc34231bfad4d55876e98ee7fc"
        ),
        "tex_sha256": (
            "735576ec52eb30477a6d1dc15ed5e0109ee47bafd389871075256554237046d0"
        ),
        "required": [
            "Dirac-Weitzenböck inertial spin connection",
            "omega^a{}_{W\\,\\mu b}=0",
            "R_{LC}=-\\mathbb T+B",
            "Hermitian Weitzenböck-Dirac equation",
            "There is no scalar field and no cosmological constant",
            "dust-like",
            "dark-energy-like",
            "not counted as an additional dark component",
            "Complete reproduction and verification commands",
            "all possible connections",
            "does not call the Phase 5 Einstein-spinor application",
        ],
    },
    "einstein-spinor-44-components-x0-x7": {
        "stem": "EINSTEIN_SPINOR_44_COMPONENTS_X0_X7",
        "markdown_sha256": (
            "aba76aabc2fce453aa1214b4b580555aa04045649279df2c9f796a27d3994502"
        ),
        "tex_sha256": (
            "4249ed227b8b4ed1c6ad7b8ec9f4b122fc296f7f17e729c274f49b7914d802ee"
        ),
        "required": [
            "coordinates = {x0, x1, x2, x3, x4, x5, x6, x7}",
            "Only the coordinate names and ordering are adopted",
            "These are the unrestricted PDEs",
            "constant-`x4` slice has signature `(4,3)`",
            "one commuting real 16-component spinor field",
            "There are no hidden matrix sums",
            "full 36-component symmetric Einstein system",
            "positive-condensate cone `S>0`",
            "backward from `x4=0` to `-0.2`",
            "Reduced autonomous ODE system solved by the study",
            "verify_phase7_x0_x7_reports.ps1",
            "verify_phase7_x0_x7_reports.sh",
        ],
    },
    "einstein-spinor-44-numerics-x0-x7": {
        "stem": "EINSTEIN_SPINOR_44_NUMERICS_X0_X7",
        "markdown_sha256": (
            "1ea9958088af5044f8ceea67e44c1b3b634e581e0902c26c1f364f9efa9e8f49"
        ),
        "tex_sha256": (
            "8465df163fb255c8b091365d543c604e6692d8b114921241e6cac5b39eb3a054"
        ),
        "required": [
            "coordinates = {x0, x1, x2, x3, x4, x5, x6, x7}",
            "variable-step, variable-order BDF",
            "CVODE",
            "No comparison study establishes BDF as globally optimal",
            "default Newton nonlinear solver",
            "internal dense difference-quotient Jacobian",
            "171",
            "1372",
            "1486",
            "Five-point finite-difference residual checks on all 18 ODE components",
            "4.705850657056059",
            "dark-energy analog",
            "dark-matter analog",
            "Exact reduction and approximate analytic solution",
            "verify_phase7_x0_x7_reports.ps1",
            "verify_phase7_x0_x7_reports.sh",
        ],
    },
}


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class CurvedSpinPublicationTests(unittest.TestCase):
    def test_documents_and_pdfs_are_canonical(self) -> None:
        for edition, document in DOCUMENTS.items():
            with self.subTest(edition=edition):
                stem = document["stem"]
                markdown_path = REPOSITORY_ROOT / "provenance" / f"{stem}.md"
                tex_path = REPOSITORY_ROOT / "provenance" / f"{stem}.tex"
                markdown_bytes = markdown_path.read_bytes()
                tex_bytes = tex_path.read_bytes()
                text = markdown_bytes.decode("utf-8")
                self.assertEqual(
                    sha256(markdown_bytes), document["markdown_sha256"]
                )
                self.assertEqual(sha256(tex_bytes), document["tex_sha256"])
                self.assertEqual(
                    build_dissertation_tex.convert(
                        text, strip_heading_numbers=True
                    ).encode("utf-8"),
                    tex_bytes,
                )
                normalized = re.sub(r"\s+", " ", text)
                self.assertTrue(
                    all(
                        phrase in normalized
                        for phrase in document["required"]
                    )
                )
                self.assertNotIn("TODO", text)
                self.assertNotIn("FIXME", text)
                markdown_references = {
                    match.replace("\\", "/")
                    for match in re.findall(
                        r"provenance[\\/][A-Za-z0-9_-]+\.md", text
                    )
                }
                if markdown_references:
                    self.assertEqual(
                        markdown_references,
                        {f"provenance/{stem}.md"},
                    )
                pdf_specification = (
                    check_provenance_pdf.SPECIFICATIONS[edition]
                )
                verify_pdf = (
                    check_provenance_pdf.check_dissertation_pdf.verify_pdf
                )
                report = verify_pdf(
                    REPOSITORY_ROOT / pdf_specification["path"],
                    None,
                    pdf_specification["pages"],
                    612.0,
                    792.0,
                    pdf_specification["sha256"],
                )
                self.assertEqual(
                    [
                        name
                        for name, passed in report["checks"].items()
                        if not passed
                    ],
                    [],
                )

    def test_pdf_checker_rejects_mutated_bytes(self) -> None:
        specifications = check_provenance_pdf.SPECIFICATIONS.items()
        for edition, specification in specifications:
            with (
                self.subTest(edition=edition),
                tempfile.TemporaryDirectory() as root,
            ):
                canonical_path = REPOSITORY_ROOT / specification["path"]
                mutated_path = Path(root) / canonical_path.name
                mutated_path.write_bytes(
                    canonical_path.read_bytes() + b"\n% mutation\n%%EOF\n"
                )
                verify_pdf = (
                    check_provenance_pdf.check_dissertation_pdf.verify_pdf
                )
                report = verify_pdf(
                    mutated_path,
                    None,
                    specification["pages"],
                    612.0,
                    792.0,
                    specification["sha256"],
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
