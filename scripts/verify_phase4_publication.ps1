[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repositoryRoot

if (-not (Get-Command pdflatex.exe -ErrorAction SilentlyContinue)) {
    $miktexBin = Join-Path $env:ProgramFiles "MiKTeX\miktex\bin\x64"
    if (-not (Test-Path -LiteralPath (Join-Path $miktexBin "pdflatex.exe"))) {
        throw "pdflatex.exe was not found on PATH or in $miktexBin"
    }
    $env:Path = "$miktexBin;$env:Path"
}

$generated = @(
    "artifacts/wolfram/dirac-triality-report.json",
    "notebooks/DiracTriality.nb",
    "notebooks/dirac_triality.ipynb",
    "notebooks/dirac_triality.executed.ipynb",
    "artifacts/notebooks/jupyter-report.json",
    "dissertation/dirac-triality.tex",
    "dissertation/dirac-triality.pdf"
)
$existing = @($generated | Where-Object { Test-Path -LiteralPath $_ })
if ($existing.Count -gt 0) {
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\phase4-backup-generated-publication.log" `
        -Command ("python scripts/backup_files.py " + ($existing -join " "))
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

New-Item -ItemType Directory -Path `
    "build\phase4\pdf-a", "build\phase4\pdf-b" -Force | Out-Null

$steps = @(
    @("logs/phase4-standalone-wolfram.log", "wolframscript -file wolfram/dirac_triality.wls -- artifacts/wolfram/dirac-triality-report.json"),
    @("logs/phase4-build-mathematica-notebook.log", "wolframscript -file scripts/build_mathematica_notebook.wls -- notebooks/DiracTriality.nb"),
    @("logs/phase4-build-mathematica-notebook-repeat.log", "wolframscript -file scripts/build_mathematica_notebook.wls -- build/phase4/DiracTriality-repeat.nb"),
    @("logs/phase4-verify-mathematica-notebook.log", "wolframscript -file scripts/verify_mathematica_notebook.wls -- notebooks/DiracTriality.nb"),
    @("logs/phase4-build-jupyter.log", "python scripts/build_jupyter_notebook.py"),
    @("logs/phase4-build-jupyter-repeat.log", "python scripts/build_jupyter_notebook.py --output build/phase4/dirac_triality-repeat.ipynb"),
    @("logs/phase4-run-jupyter.log", "python scripts/run_jupyter_notebook.py notebooks/dirac_triality.ipynb --output notebooks/dirac_triality.executed.ipynb"),
    @("logs/phase4-run-jupyter-repeat.log", "python scripts/run_jupyter_notebook.py build/phase4/dirac_triality-repeat.ipynb --output build/phase4/dirac_triality-repeat.executed.ipynb"),
    @("logs/phase4-check-jupyter.log", "python scripts/check_jupyter_notebook.py notebooks/dirac_triality.executed.ipynb --repeat build/phase4/dirac_triality-repeat.executed.ipynb"),
    @("logs/phase4-build-dissertation-tex.log", "python scripts/build_dissertation_tex.py"),
    @("logs/phase4-build-dissertation-tex-repeat.log", "python scripts/build_dissertation_tex.py --output build/phase4/dirac-triality-repeat.tex"),
    @("logs/phase4-build-pdf-a1.log", "pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build/phase4/pdf-a dissertation/dirac-triality.tex"),
    @("logs/phase4-build-pdf-a2.log", "pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build/phase4/pdf-a dissertation/dirac-triality.tex"),
    @("logs/phase4-build-pdf-a3.log", "pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build/phase4/pdf-a dissertation/dirac-triality.tex"),
    @("logs/phase4-build-pdf-b1.log", "pdflatex -interaction=nonstopmode -halt-on-error -jobname=dirac-triality -output-directory=build/phase4/pdf-b build/phase4/dirac-triality-repeat.tex"),
    @("logs/phase4-build-pdf-b2.log", "pdflatex -interaction=nonstopmode -halt-on-error -jobname=dirac-triality -output-directory=build/phase4/pdf-b build/phase4/dirac-triality-repeat.tex"),
    @("logs/phase4-build-pdf-b3.log", "pdflatex -interaction=nonstopmode -halt-on-error -jobname=dirac-triality -output-directory=build/phase4/pdf-b build/phase4/dirac-triality-repeat.tex"),
    @("logs/phase4-check-dissertation-pdf.log", "python scripts/check_dissertation_pdf.py build/phase4/pdf-a/dirac-triality.pdf --repeat build/phase4/pdf-b/dirac-triality.pdf"),
    @("logs/phase4-python-tests.log", "python -m unittest discover -s tests -v")
)
foreach ($step in $steps) {
    & "$PSScriptRoot\run_logged.ps1" -LogPath $step[0] -Command $step[1]
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$pairs = @(
    @("notebooks\DiracTriality.nb", "build\phase4\DiracTriality-repeat.nb"),
    @("notebooks\dirac_triality.ipynb", "build\phase4\dirac_triality-repeat.ipynb"),
    @("notebooks\dirac_triality.executed.ipynb", "build\phase4\dirac_triality-repeat.executed.ipynb"),
    @("dissertation\dirac-triality.tex", "build\phase4\dirac-triality-repeat.tex"),
    @("build\phase4\pdf-a\dirac-triality.pdf", "build\phase4\pdf-b\dirac-triality.pdf")
)
foreach ($pair in $pairs) {
    $first = (Get-FileHash -LiteralPath $pair[0] -Algorithm SHA256).Hash
    $second = (Get-FileHash -LiteralPath $pair[1] -Algorithm SHA256).Hash
    if ($first -ne $second) {
        Write-Output "ERROR: generated artifact changed bytes: $($pair[0])"
        exit 1
    }
}
$issues = Select-String `
    -Path "build\phase4\pdf-a\dirac-triality.log", "build\phase4\pdf-b\dirac-triality.log" `
    -Pattern "^!|LaTeX Warning|Package .* Warning|Overfull|Underfull|Undefined control sequence"
if ($issues) {
    Write-Output "ERROR: LaTeX warnings remain"
    $issues | ForEach-Object { Write-Output $_.Line }
    exit 1
}
Copy-Item -LiteralPath "build\phase4\pdf-a\dirac-triality.pdf" `
    -Destination "dissertation\dirac-triality.pdf" -Force

Write-Output "mathematica_notebook_sha256=$((Get-FileHash notebooks\DiracTriality.nb -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "jupyter_notebook_sha256=$((Get-FileHash notebooks\dirac_triality.executed.ipynb -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "dissertation_pdf_sha256=$((Get-FileHash dissertation\dirac-triality.pdf -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "phase4_publication_verification=OK"
exit 0