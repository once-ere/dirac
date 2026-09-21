# Learn dissertation provenance

## Artifacts and authority

```text
dissertation/Learn_dirac-triality.md
dissertation/Learn_dirac-triality.tex
dissertation/Learn_dirac-triality.pdf
```

The Markdown file is the authoritative teaching edition. It assumes calculus
and basic matrix multiplication, then defines every specialized mathematical,
numerical, geometric, and cosmological idea before use. It includes 29 numbered
chapters, 20 worked examples, 20 misconception checks, 22 exercises, 22 complete
solutions, 53 glossary entries, a notation index, reference capsules, and a
claim-to-evidence map.

The Python builder converts the complete Markdown source to a standalone LaTeX
document. The Learn build uses `--strip-heading-numbers`: authored numbering
remains visible in standalone Markdown, while LaTeX supplies one clean set of
section numbers in the PDF. The default builder mode generates the primary
research edition.

The PDF suppresses volatile engine timestamps and trailer identifiers. Two
isolated builds from independently generated TeX must be byte-identical. Three
pdfTeX passes are required to converge the table of contents from a clean
build.

## Canonical measurements

```text
Markdown bytes=102388
Markdown lines=3438
Markdown words=15682
Markdown SHA-256=ab6c653f6d0f2355411d61c9357d3c709ced8b9ac70167861e893a9029052676
LaTeX bytes=118691
LaTeX lines=2934
LaTeX SHA-256=533eeaef0619d3b590d74fa03a4a81aaa76163fce289d659a1007d1b10b0e03e
PDF bytes=745001
PDF pages=74
PDF MediaBox=612 x 792 points
PDF SHA-256=7c683b51445a3b4964b244ea3e232bc0ba3f745b5427308b59a80d1532e19ff9
```

## Content verification

`scripts/check_learn_dissertation.py` runs 21 checks. It requires:

- UTF-8 source with LF line endings and the canonical title/subtitle;
- all 29 chapters in order and at least 10,000 words;
- all original algebraic, numerical, and scientific-scope claims;
- exactly 20 sequential worked examples and misconception checks;
- exactly 22 exercises with 22 matching complete solutions;
- at least 53 glossary entries and seven reference capsules;
- no TODO, FIXME, TBD, or instruction to obtain a prerequisite elsewhere;
- byte agreement between committed TeX and a fresh in-memory conversion;
- exact Clifford chirality indices and volume-element signs from the fixture;
- exact split-octonion products, associator, and cyclic para-product values;
- exact triality rank, dimension, representation, and `S3` measurements;
- exact canonical transport, cosmology, curved-geometry, Einstein-spinor, and
	Weitzenböck measurements.

The checker deliberately recomputes the small algebra examples from the
machine-readable tensors. It does not accept matching prose as proof of those
examples.

## Mathematical and scientific review

A separate pre-publication review checked Clifford signs and factors of two,
chirality coordinates, real representation scope, global group versus Lie
algebra language, split-octonion signs and nonassociativity, the reflection and
intertwiner conventions, transport generators, the cosmology rotation, and the
independence of numerical diagnostics.

Corrections incorporated before freezing the PDF include:

- parity-interleaved half-spin indices from the exact Clifford fixture;
- `Pin`, `Spin`, and identity-component covering distinctions;
- algebraically versus topologically simply connected terminology;
- the explicit cross product and triality reflection formulas;
- the canonical intertwiner equation `gamma_a K = K Gamma_a`;
- the zero-based matrix convention for each transport generator `E_ab`;
- identification of `J` as the fifth ordered, odd Clifford generator;
- labeling Friedmann consistency as derived from the density comparison;
- disclosure that dimensionless time has no independent quadrature check.

The final pdfTeX logs have no errors, LaTeX/package warnings, overfull boxes,
underfull boxes, or undefined controls. Text extraction found the title,
representative chapters, exercises, solutions, glossary, reference capsules,
and conclusion, with no placeholders. Rendered pages from the beginning,
quarter, midpoint, three-quarter point, and end were inspected for clipping,
overlap, broken glyphs, duplicate numbering, and malformed mathematics.

## Complete Windows verification

From PowerShell:

```powershell
Set-Location C:\Users\nsh\Developer\code\vscode\dirac
.\scripts\verify_learn_dissertation.ps1
```

The gate performs these operations in order:

```powershell
python scripts/backup_files.py dissertation/Learn_dirac-triality.tex dissertation/Learn_dirac-triality.pdf
python scripts/build_dissertation_tex.py --strip-heading-numbers --input dissertation/Learn_dirac-triality.md --output dissertation/Learn_dirac-triality.tex
python scripts/build_dissertation_tex.py --strip-heading-numbers --input dissertation/Learn_dirac-triality.md --output build/learn/Learn_dirac-triality-repeat.tex
python scripts/check_learn_dissertation.py
pdflatex -interaction=nonstopmode -halt-on-error -jobname=Learn_dirac-triality -output-directory=build/learn/verify-pdf-a dissertation/Learn_dirac-triality.tex
pdflatex -interaction=nonstopmode -halt-on-error -jobname=Learn_dirac-triality -output-directory=build/learn/verify-pdf-a dissertation/Learn_dirac-triality.tex
pdflatex -interaction=nonstopmode -halt-on-error -jobname=Learn_dirac-triality -output-directory=build/learn/verify-pdf-a dissertation/Learn_dirac-triality.tex
pdflatex -interaction=nonstopmode -halt-on-error -jobname=Learn_dirac-triality -output-directory=build/learn/verify-pdf-b build/learn/Learn_dirac-triality-repeat.tex
pdflatex -interaction=nonstopmode -halt-on-error -jobname=Learn_dirac-triality -output-directory=build/learn/verify-pdf-b build/learn/Learn_dirac-triality-repeat.tex
pdflatex -interaction=nonstopmode -halt-on-error -jobname=Learn_dirac-triality -output-directory=build/learn/verify-pdf-b build/learn/Learn_dirac-triality-repeat.tex
python scripts/check_dissertation_pdf.py --edition learn build/learn/verify-pdf-a/Learn_dirac-triality.pdf --repeat build/learn/verify-pdf-b/Learn_dirac-triality.pdf
python -m unittest discover -s tests -p test_dissertation_builder.py -v
python -m unittest discover -s tests -p test_learn_dissertation.py -v
python -m unittest discover -s tests -p test_dissertation_pdf.py -v
```

The script also checks the canonical SHA-256 values of all three primary
`dirac-triality.*` artifacts, compares both generated TeX files and both PDFs,
rejects any listed TeX warning, and copies the PDF only after every check
passes. Its final line must be:

```text
learn_dissertation_verification=OK
```

## Complete Git Bash or WSL verification

```bash
cd /c/Users/nsh/Developer/code/vscode/dirac
bash ./scripts/verify_learn_dissertation.sh
```

The Bash gate resolves the installed Windows Python and MiKTeX executables,
performs the same primary-hash guards, backups, dual builds, content checks,
focused tests, warning scan, byte comparisons, and canonical copy. Its final
line must also be:

```text
learn_dissertation_verification=OK
```

## Full publication verification

The Learn gate is part of both Phase 4 entry points:

```powershell
.\scripts\verify_phase4_publication.ps1
```

```bash
bash ./scripts/verify_phase4_publication.sh
```

A Phase 4 success therefore requires the standalone Wolfram report,
Mathematica notebook, Jupyter notebook, original dissertation, and Learn
dissertation to pass together.

## Primary-edition synchronization

The teaching edition is parallel to, not a replacement for, the primary
research edition. The focused gate requires these canonical hashes before
doing any work:

```text
dissertation/dirac-triality.md  44b76c2d872598ad1b038a8d4ad1293b18885ab228297c921579daa86eeb1381
dissertation/dirac-triality.tex 12df60627b5f11b09ccbbadd9ca38fd2ce7efcfccd769f69fd8280b78a6cec38
dissertation/dirac-triality.pdf 8531af531c91fbf366fbcb30759da63e3881dcc241931698a9f6ee3a6ae0b69e
```
