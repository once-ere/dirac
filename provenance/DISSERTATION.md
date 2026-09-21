# Research dissertation provenance

This document covers the primary research edition. It includes the exact
algebra, all four numerical studies, curved Spin(4,4) geometry, the canonical
Einstein-spinor model, and its independently implemented Weitzenböck/TEGR
formulation. The parallel self-contained teaching edition is documented in
[LEARN_DISSERTATION.md](LEARN_DISSERTATION.md).

## Artifacts

```text
dissertation/dirac-triality.md
dissertation/dirac-triality.tex
dissertation/dirac-triality.pdf
```

The Markdown file is the authoritative dissertation text. The Python builder
expands it into a complete standalone LaTeX document; the LaTeX source does not
include the Markdown file at compile time. The PDF suppresses volatile engine
timestamps and trailer identifiers so isolated builds are byte-identical.
Three pdfTeX passes are required because inserting the first table of contents
shifts the section page numbers consumed by the final pass.

## Canonical measurements

```text
Markdown bytes=28697
Markdown lines=1042
Markdown SHA-256=44b76c2d872598ad1b038a8d4ad1293b18885ab228297c921579daa86eeb1381
LaTeX bytes=30979
LaTeX lines=962
LaTeX SHA-256=12df60627b5f11b09ccbbadd9ca38fd2ce7efcfccd769f69fd8280b78a6cec38
PDF bytes=396932
PDF pages=19
PDF MediaBox=612 x 792 points
PDF SHA-256=8531af531c91fbf366fbcb30759da63e3881dcc241931698a9f6ee3a6ae0b69e
```

## Complete Windows commands

```powershell
Set-Location C:\Users\nsh\Developer\code\vscode\dirac
$miktexBin = Join-Path $env:ProgramFiles "MiKTeX\miktex\bin\x64"
if (-not (Get-Command pdflatex.exe -ErrorAction SilentlyContinue)) {
  if (-not (Test-Path (Join-Path $miktexBin "pdflatex.exe"))) {
    throw "pdflatex.exe was not found"
  }
  $env:Path = "$miktexBin;$env:Path"
}
New-Item -ItemType Directory -Path build\phase4\pdf-a,build\phase4\pdf-b -Force | Out-Null
.\scripts\run_logged.ps1 `
  -LogPath logs\phase4-build-dissertation-tex.log `
  -Command "python scripts/build_dissertation_tex.py"
.\scripts\run_logged.ps1 `
  -LogPath logs\phase4-build-dissertation-tex-repeat.log `
  -Command "python scripts/build_dissertation_tex.py --output build/phase4/dirac-triality-repeat.tex"
$texFirst = (Get-FileHash dissertation\dirac-triality.tex -Algorithm SHA256).Hash
$texSecond = (Get-FileHash build\phase4\dirac-triality-repeat.tex -Algorithm SHA256).Hash
if ($texFirst -ne $texSecond) { throw "LaTeX generation changed bytes" }
.\scripts\run_logged.ps1 -LogPath logs\phase4-build-pdf-a1.log `
  -Command "pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build/phase4/pdf-a dissertation/dirac-triality.tex"
.\scripts\run_logged.ps1 -LogPath logs\phase4-build-pdf-a2.log `
  -Command "pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build/phase4/pdf-a dissertation/dirac-triality.tex"
.\scripts\run_logged.ps1 -LogPath logs\phase4-build-pdf-a3.log `
  -Command "pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build/phase4/pdf-a dissertation/dirac-triality.tex"
.\scripts\run_logged.ps1 -LogPath logs\phase4-build-pdf-b1.log `
  -Command "pdflatex -interaction=nonstopmode -halt-on-error -jobname=dirac-triality -output-directory=build/phase4/pdf-b build/phase4/dirac-triality-repeat.tex"
.\scripts\run_logged.ps1 -LogPath logs\phase4-build-pdf-b2.log `
  -Command "pdflatex -interaction=nonstopmode -halt-on-error -jobname=dirac-triality -output-directory=build/phase4/pdf-b build/phase4/dirac-triality-repeat.tex"
.\scripts\run_logged.ps1 -LogPath logs\phase4-build-pdf-b3.log `
  -Command "pdflatex -interaction=nonstopmode -halt-on-error -jobname=dirac-triality -output-directory=build/phase4/pdf-b build/phase4/dirac-triality-repeat.tex"
.\scripts\run_logged.ps1 -LogPath logs\phase4-check-dissertation-pdf.log `
  -Command "python scripts/check_dissertation_pdf.py build/phase4/pdf-a/dirac-triality.pdf --repeat build/phase4/pdf-b/dirac-triality.pdf"
$pdfFirst = (Get-FileHash build\phase4\pdf-a\dirac-triality.pdf -Algorithm SHA256).Hash
$pdfSecond = (Get-FileHash build\phase4\pdf-b\dirac-triality.pdf -Algorithm SHA256).Hash
if ($pdfFirst -ne $pdfSecond) { throw "PDF generation changed bytes" }
Copy-Item build\phase4\pdf-a\dirac-triality.pdf dissertation\dirac-triality.pdf -Force
$issues = Select-String -Path build\phase4\pdf-a\dirac-triality.log,build\phase4\pdf-b\dirac-triality.log `
  -Pattern '^!|LaTeX Warning|Package .* Warning|Overfull|Underfull|Undefined control sequence'
if ($issues) { throw "LaTeX warnings remain" }
```

Expected PDF metadata:

```text
pages=19
page_size=612 x 792 points
```

## Complete Git Bash or WSL commands

```bash
cd /c/Users/nsh/Developer/code/vscode/dirac
source ./scripts/resolve_wolframscript.sh
python_command="$(resolve_windows_command python.exe)"
pdflatex_command="$(resolve_miktex_pdflatex)"
mkdir -p build/phase4/pdf-a build/phase4/pdf-b
./scripts/run_logged.sh logs/phase4-build-dissertation-tex-bash.log -- \
  "$python_command" scripts/build_dissertation_tex.py
./scripts/run_logged.sh logs/phase4-build-dissertation-tex-repeat-bash.log -- \
  "$python_command" scripts/build_dissertation_tex.py \
    --output build/phase4/dirac-triality-repeat.tex
test "$(sha256sum dissertation/dirac-triality.tex | cut -d' ' -f1)" = \
  "$(sha256sum build/phase4/dirac-triality-repeat.tex | cut -d' ' -f1)"
./scripts/run_logged.sh logs/phase4-build-pdf-a1-bash.log -- \
  "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
    -output-directory=build/phase4/pdf-a dissertation/dirac-triality.tex
./scripts/run_logged.sh logs/phase4-build-pdf-a2-bash.log -- \
  "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
    -output-directory=build/phase4/pdf-a dissertation/dirac-triality.tex
./scripts/run_logged.sh logs/phase4-build-pdf-a3-bash.log -- \
  "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
    -output-directory=build/phase4/pdf-a dissertation/dirac-triality.tex
./scripts/run_logged.sh logs/phase4-build-pdf-b1-bash.log -- \
  "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
    -jobname=dirac-triality -output-directory=build/phase4/pdf-b \
    build/phase4/dirac-triality-repeat.tex
./scripts/run_logged.sh logs/phase4-build-pdf-b2-bash.log -- \
  "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
    -jobname=dirac-triality -output-directory=build/phase4/pdf-b \
    build/phase4/dirac-triality-repeat.tex
./scripts/run_logged.sh logs/phase4-build-pdf-b3-bash.log -- \
  "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
    -jobname=dirac-triality -output-directory=build/phase4/pdf-b \
    build/phase4/dirac-triality-repeat.tex
./scripts/run_logged.sh logs/phase4-check-dissertation-pdf-bash.log -- \
  "$python_command" scripts/check_dissertation_pdf.py \
    build/phase4/pdf-a/dirac-triality.pdf \
    --repeat build/phase4/pdf-b/dirac-triality.pdf
test "$(sha256sum build/phase4/pdf-a/dirac-triality.pdf | cut -d' ' -f1)" = \
  "$(sha256sum build/phase4/pdf-b/dirac-triality.pdf | cut -d' ' -f1)"
cp build/phase4/pdf-a/dirac-triality.pdf dissertation/dirac-triality.pdf
! grep -Ei '^!|LaTeX Warning|Package .* Warning|Overfull|Underfull|Undefined control sequence' \
  build/phase4/pdf-a/dirac-triality.log build/phase4/pdf-b/dirac-triality.log
```