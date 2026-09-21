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

$originalHashes = @{
    "dissertation\dirac-triality.md" = "44b76c2d872598ad1b038a8d4ad1293b18885ab228297c921579daa86eeb1381"
    "dissertation\dirac-triality.tex" = "12df60627b5f11b09ccbbadd9ca38fd2ce7efcfccd769f69fd8280b78a6cec38"
    "dissertation\dirac-triality.pdf" = "8531af531c91fbf366fbcb30759da63e3881dcc241931698a9f6ee3a6ae0b69e"
}
foreach ($entry in $originalHashes.GetEnumerator()) {
    $actual = (Get-FileHash -LiteralPath $entry.Key -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $entry.Value) {
        throw "Primary dissertation drifted: $($entry.Key)"
    }
}

$generated = @(
    "dissertation/Learn_dirac-triality.tex",
    "dissertation/Learn_dirac-triality.pdf"
)
$existing = @($generated | Where-Object { Test-Path -LiteralPath $_ })
if ($existing.Count -gt 0) {
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\learn-backup-generated.log" `
        -Command ("python scripts/backup_files.py " + ($existing -join " "))
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Remove-Item "build\learn\verify-pdf-a", "build\learn\verify-pdf-b" `
    -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path `
    "build\learn\verify-pdf-a", "build\learn\verify-pdf-b" -Force | Out-Null

$steps = @(
    @("logs/learn-build-tex.log", "python scripts/build_dissertation_tex.py --strip-heading-numbers --input dissertation/Learn_dirac-triality.md --output dissertation/Learn_dirac-triality.tex"),
    @("logs/learn-build-tex-repeat.log", "python scripts/build_dissertation_tex.py --strip-heading-numbers --input dissertation/Learn_dirac-triality.md --output build/learn/Learn_dirac-triality-repeat.tex"),
    @("logs/learn-check-content.log", "python scripts/check_learn_dissertation.py"),
    @("logs/learn-build-pdf-a1.log", "pdflatex -interaction=nonstopmode -halt-on-error -jobname=Learn_dirac-triality -output-directory=build/learn/verify-pdf-a dissertation/Learn_dirac-triality.tex"),
    @("logs/learn-build-pdf-a2.log", "pdflatex -interaction=nonstopmode -halt-on-error -jobname=Learn_dirac-triality -output-directory=build/learn/verify-pdf-a dissertation/Learn_dirac-triality.tex"),
    @("logs/learn-build-pdf-a3.log", "pdflatex -interaction=nonstopmode -halt-on-error -jobname=Learn_dirac-triality -output-directory=build/learn/verify-pdf-a dissertation/Learn_dirac-triality.tex"),
    @("logs/learn-build-pdf-b1.log", "pdflatex -interaction=nonstopmode -halt-on-error -jobname=Learn_dirac-triality -output-directory=build/learn/verify-pdf-b build/learn/Learn_dirac-triality-repeat.tex"),
    @("logs/learn-build-pdf-b2.log", "pdflatex -interaction=nonstopmode -halt-on-error -jobname=Learn_dirac-triality -output-directory=build/learn/verify-pdf-b build/learn/Learn_dirac-triality-repeat.tex"),
    @("logs/learn-build-pdf-b3.log", "pdflatex -interaction=nonstopmode -halt-on-error -jobname=Learn_dirac-triality -output-directory=build/learn/verify-pdf-b build/learn/Learn_dirac-triality-repeat.tex"),
    @("logs/learn-check-pdf.log", "python scripts/check_dissertation_pdf.py --edition learn build/learn/verify-pdf-a/Learn_dirac-triality.pdf --repeat build/learn/verify-pdf-b/Learn_dirac-triality.pdf"),
    @("logs/learn-test-builder.log", "python -m unittest discover -s tests -p test_dissertation_builder.py -v"),
    @("logs/learn-test-content.log", "python -m unittest discover -s tests -p test_learn_dissertation.py -v"),
    @("logs/learn-test-pdf.log", "python -m unittest discover -s tests -p test_dissertation_pdf.py -v")
)
foreach ($step in $steps) {
    & "$PSScriptRoot\run_logged.ps1" -LogPath $step[0] -Command $step[1]
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$texFirst = (Get-FileHash -LiteralPath "dissertation\Learn_dirac-triality.tex" -Algorithm SHA256).Hash
$texSecond = (Get-FileHash -LiteralPath "build\learn\Learn_dirac-triality-repeat.tex" -Algorithm SHA256).Hash
if ($texFirst -ne $texSecond) {
    throw "Learn LaTeX generation changed bytes"
}
$pdfFirst = (Get-FileHash -LiteralPath "build\learn\verify-pdf-a\Learn_dirac-triality.pdf" -Algorithm SHA256).Hash
$pdfSecond = (Get-FileHash -LiteralPath "build\learn\verify-pdf-b\Learn_dirac-triality.pdf" -Algorithm SHA256).Hash
if ($pdfFirst -ne $pdfSecond) {
    throw "Learn PDF generation changed bytes"
}
$issues = Select-String `
    -Path "build\learn\verify-pdf-a\Learn_dirac-triality.log", "build\learn\verify-pdf-b\Learn_dirac-triality.log" `
    -Pattern "^!|LaTeX Warning|Package .* Warning|Overfull|Underfull|Undefined control sequence"
if ($issues) {
    Write-Output "ERROR: Learn LaTeX warnings remain"
    $issues | ForEach-Object { Write-Output $_.Line }
    exit 1
}

Copy-Item -LiteralPath "build\learn\verify-pdf-a\Learn_dirac-triality.pdf" `
    -Destination "dissertation\Learn_dirac-triality.pdf" -Force

Write-Output "learn_markdown_sha256=$((Get-FileHash dissertation\Learn_dirac-triality.md -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "learn_tex_sha256=$($texFirst.ToLowerInvariant())"
Write-Output "learn_pdf_sha256=$($pdfFirst.ToLowerInvariant())"
Write-Output "learn_dissertation_verification=OK"
exit 0
