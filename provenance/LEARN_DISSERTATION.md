# Learn dissertation provenance

## Artifacts and authority

```text
dissertation/Learn_dirac-triality.md
dissertation/Learn_dirac-triality.tex
dissertation/Learn_dirac-triality.pdf
```

The Markdown file is the authoritative teaching edition. It assumes calculus
and basic matrix multiplication, then defines every specialized mathematical,
numerical, and cosmological idea before use. It includes 25 numbered chapters,
16 worked examples, 16 misconception checks, 18 exercises, 18 complete
solutions, 47 glossary entries, a notation index, reference capsules, and a
claim-to-evidence map.

The Python builder converts the complete Markdown source to a standalone LaTeX
document. The Learn build uses `--strip-heading-numbers`: authored numbering
remains visible in standalone Markdown, while LaTeX supplies one clean set of
section numbers in the PDF. The default builder mode remains byte-compatible
with the original research edition.

The PDF suppresses volatile engine timestamps and trailer identifiers. Two
isolated builds from independently generated TeX must be byte-identical. Three
pdfTeX passes are required to converge the table of contents from a clean
build.

## Canonical measurements

```text
Markdown bytes=85702
Markdown lines=2826
Markdown words=13146
Markdown SHA-256=a8cf09e1ea1860bdbef3125ef01dbf3bc0c5f5a3e9a7adc4fe6c92f534abce58
LaTeX bytes=99832
LaTeX lines=2395
LaTeX SHA-256=ee325930f4f45540957c9bc6dd166e4c610aa479291273e8636d87382464405f
PDF bytes=669155
PDF pages=62
PDF MediaBox=612 x 792 points
PDF SHA-256=134bd5dba9751e7972463c17a6074a3ac440d031c1a4a9ae44212a8d8fbcf521
```

## Content verification

`scripts/check_learn_dissertation.py` runs 18 checks. It requires:

- UTF-8 source with LF line endings and the canonical title/subtitle;
- all 25 chapters in order and at least 10,000 words;
- all original algebraic, numerical, and scientific-scope claims;
- exactly 16 sequential worked examples and misconception checks;
- exactly 18 exercises with 18 matching complete solutions;
- at least 45 glossary entries and six reference capsules;
- no TODO, FIXME, TBD, or instruction to obtain a prerequisite elsewhere;
- byte agreement between committed TeX and a fresh in-memory conversion;
- exact Clifford chirality indices and volume-element signs from the fixture;
- exact split-octonion products, associator, and cyclic para-product values;
- exact triality rank, dimension, representation, and `S3` measurements;
- exact canonical transport and cosmology measurements.

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

The script also checks the frozen SHA-256 values of all three original
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
performs the same original-hash guards, backups, dual builds, content checks,
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

## Original-edition immutability

The teaching edition is parallel to, not a replacement for, the original. The
focused gate requires these unchanged hashes before doing any work:

```text
dissertation/dirac-triality.md  47d280353a02c37778775720cf2459b9866510bc89ddb1bbb83c6da2d3504b97
dissertation/dirac-triality.tex 414b966295ae8f5092553c1af5f339683a67bf8ed77844eb118751713795bfd0
dissertation/dirac-triality.pdf a2a6e366817cb17d4b4ba936a98f5e495a8ca9c0bc012540021bc548847073f3
```
