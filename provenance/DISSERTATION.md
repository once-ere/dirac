# Dissertation Markdown, LaTeX, and PDF provenance

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
.\scripts\run_logged.ps1 -LogPath logs\phase4-build-pdf-b1.log `
  -Command "pdflatex -interaction=nonstopmode -halt-on-error -jobname=dirac-triality -output-directory=build/phase4/pdf-b build/phase4/dirac-triality-repeat.tex"
.\scripts\run_logged.ps1 -LogPath logs\phase4-build-pdf-b2.log `
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
pages=13
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
./scripts/run_logged.sh logs/phase4-build-pdf-b1-bash.log -- \
  "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
    -jobname=dirac-triality -output-directory=build/phase4/pdf-b \
    build/phase4/dirac-triality-repeat.tex
./scripts/run_logged.sh logs/phase4-build-pdf-b2-bash.log -- \
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