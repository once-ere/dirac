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

$expectedVendorCommit = "d1836e6a279d63a90fe2839a0020123245487e76"
$actualVendorCommit = git -C vendor/sundials_rs rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $actualVendorCommit -ne $expectedVendorCommit) {
    throw "solver submodule commit mismatch"
}
if (git -C vendor/sundials_rs status --porcelain) {
    throw "solver submodule is dirty"
}

$generated = @("DEVELOPER_SUMMARY.tex", "DEVELOPER_SUMMARY.pdf")
$existing = @($generated | Where-Object { Test-Path -LiteralPath $_ })
if ($existing.Count -gt 0) {
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\developer-summary-backup.log" `
        -Command ("python scripts/backup_files.py " + ($existing -join " "))
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$buildDirectories = @(
    "build\developer-summary\pdf-a",
    "build\developer-summary\pdf-b"
)
Remove-Item "build\developer-summary" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $buildDirectories -Force | Out-Null

$steps = @(
    @("logs/developer-summary-check.log", "python scripts/check_developer_summary.py"),
    @("logs/developer-summary-build-tex.log", "python scripts/build_dissertation_tex.py --strip-heading-numbers --developer-layout --input DEVELOPER_SUMMARY.md --output DEVELOPER_SUMMARY.tex"),
    @("logs/developer-summary-build-tex-repeat.log", "python scripts/build_dissertation_tex.py --strip-heading-numbers --developer-layout --input DEVELOPER_SUMMARY.md --output build/developer-summary/DEVELOPER_SUMMARY-repeat.tex")
)
foreach ($step in $steps) {
    & "$PSScriptRoot\run_logged.ps1" -LogPath $step[0] -Command $step[1]
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

for ($pass = 1; $pass -le 3; $pass++) {
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\developer-summary-pdf-a$pass.log" `
        -Command "pdflatex -interaction=nonstopmode -halt-on-error -jobname=DEVELOPER_SUMMARY -output-directory=build/developer-summary/pdf-a DEVELOPER_SUMMARY.tex"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\developer-summary-pdf-b$pass.log" `
        -Command "pdflatex -interaction=nonstopmode -halt-on-error -jobname=DEVELOPER_SUMMARY -output-directory=build/developer-summary/pdf-b build/developer-summary/DEVELOPER_SUMMARY-repeat.tex"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Copy-Item "build\developer-summary\pdf-a\DEVELOPER_SUMMARY.pdf" `
    "DEVELOPER_SUMMARY.pdf" -Force

& "$PSScriptRoot\run_logged.ps1" `
    -LogPath "logs\developer-summary-check-pdf.log" `
    -Command "python scripts/check_provenance_pdf.py --edition developer-summary DEVELOPER_SUMMARY.pdf --repeat build/developer-summary/pdf-b/DEVELOPER_SUMMARY.pdf"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$pairs = @(
    @("DEVELOPER_SUMMARY.tex", "build\developer-summary\DEVELOPER_SUMMARY-repeat.tex"),
    @("DEVELOPER_SUMMARY.pdf", "build\developer-summary\pdf-b\DEVELOPER_SUMMARY.pdf")
)
foreach ($pair in $pairs) {
    $first = (Get-FileHash -LiteralPath $pair[0] -Algorithm SHA256).Hash
    $second = (Get-FileHash -LiteralPath $pair[1] -Algorithm SHA256).Hash
    if ($first -ne $second) {
        throw "generated artifact changed bytes: $($pair[0])"
    }
}

$warningPattern = "^!|LaTeX Warning|Package .* Warning|"
$warningPattern += "Overfull|Underfull|Undefined control sequence"
$issues = Select-String -Path `
    "build\developer-summary\pdf-a\DEVELOPER_SUMMARY.log", `
    "build\developer-summary\pdf-b\DEVELOPER_SUMMARY.log" `
    -Pattern $warningPattern
if ($issues) {
    $issues | ForEach-Object { Write-Output $_.Line }
    throw "Developer Summary LaTeX warnings remain"
}

& "$PSScriptRoot\run_logged.ps1" `
    -LogPath "logs\developer-summary-tests.log" `
    -Command "python -m unittest discover -s tests -v"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output "vendor_commit=$actualVendorCommit"
Write-Output "developer_summary_md_sha256=$((Get-FileHash DEVELOPER_SUMMARY.md -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "developer_summary_tex_sha256=$((Get-FileHash DEVELOPER_SUMMARY.tex -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "developer_summary_pdf_sha256=$((Get-FileHash DEVELOPER_SUMMARY.pdf -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "developer_summary_verification=OK"
exit 0
