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

$generated = @(
    "artifacts/weitzenbock-spin-geometry/geometry.json",
    "artifacts/weitzenbock-spin-geometry/wolfram-report.json",
    "studies/weitzenbock_spinor_44/src/generated.rs",
    "artifacts/weitzenbock-spinor-44/history.csv",
    "artifacts/weitzenbock-spinor-44/summary.json",
    "notebooks/DiracTriality.nb",
    "provenance/WEITZENBOCK_SPINOR_44.tex",
    "provenance/WEITZENBOCK_SPINOR_44.pdf"
)
$existing = @($generated | Where-Object { Test-Path -LiteralPath $_ })
if ($existing.Count -gt 0) {
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\phase6-backup-generated.log" `
        -Command ("python scripts/backup_files.py " + ($existing -join " "))
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$buildDirectories = @(
    "build\phase6\pdf-a",
    "build\phase6\pdf-b",
    "build\phase6\weitzenbock-repeat",
    "build\phase6\weitzenbock-refined"
)
Remove-Item $buildDirectories -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $buildDirectories -Force | Out-Null

$steps = @(
    @("logs/phase6-build-geometry.log", "python scripts/build_weitzenbock_spin_geometry.py"),
    @("logs/phase6-build-geometry-repeat.log", "python scripts/build_weitzenbock_spin_geometry.py --output build/phase6/geometry-repeat.json"),
    @("logs/phase6-wolfram-geometry.log", "wolframscript -file scripts/verify_weitzenbock_spin_geometry.wls -- artifacts/weitzenbock-spin-geometry/wolfram-report.json"),
    @("logs/phase6-wolfram-geometry-repeat.log", "wolframscript -file scripts/verify_weitzenbock_spin_geometry.wls -- build/phase6/wolfram-report-repeat.json"),
    @("logs/phase6-check-geometry.log", "python scripts/check_weitzenbock_spin_geometry.py"),
    @("logs/phase6-check-model.log", "python scripts/check_weitzenbock_spinor_model.py"),
    @("logs/phase6-generate-constants.log", "python scripts/generate_weitzenbock_spinor_constants.py"),
    @("logs/phase6-generate-constants-repeat.log", "python scripts/generate_weitzenbock_spinor_constants.py --output build/phase6/generated-repeat.rs"),
    @("logs/phase6-cargo-fmt.log", "cargo fmt -p weitzenbock_spinor_44 -- --check"),
    @("logs/phase6-cargo-clippy.log", "cargo clippy -p weitzenbock_spinor_44 --all-targets -- -D warnings"),
    @("logs/phase6-cargo-test.log", "cargo test -p weitzenbock_spinor_44"),
    @("logs/phase6-python-tests.log", "python -m unittest discover -s tests -v"),
    @("logs/phase6-run.log", "cargo run --release -p weitzenbock_spinor_44 -- --output artifacts/weitzenbock-spinor-44"),
    @("logs/phase6-run-repeat.log", "cargo run --release -p weitzenbock_spinor_44 -- --output build/phase6/weitzenbock-repeat"),
    @("logs/phase6-run-refined.log", "cargo run --release -p weitzenbock_spinor_44 -- --output build/phase6/weitzenbock-refined --relative-tolerance 1e-12 --absolute-tolerance 1e-14 --maximum-step 0.001"),
    @("logs/phase6-check-output.log", "python scripts/check_weitzenbock_spinor_44.py --repeat build/phase6/weitzenbock-repeat --refined build/phase6/weitzenbock-refined"),
    @("logs/phase6-build-mathematica.log", "wolframscript -file scripts/build_mathematica_notebook.wls -- notebooks/DiracTriality.nb"),
    @("logs/phase6-build-mathematica-repeat.log", "wolframscript -file scripts/build_mathematica_notebook.wls -- build/phase6/DiracTriality-repeat.nb"),
    @("logs/phase6-check-mathematica.log", "wolframscript -file scripts/verify_mathematica_notebook.wls -- notebooks/DiracTriality.nb"),
    @("logs/phase6-build-tex.log", "python scripts/build_dissertation_tex.py --strip-heading-numbers --input provenance/WEITZENBOCK_SPINOR_44.md --output provenance/WEITZENBOCK_SPINOR_44.tex"),
    @("logs/phase6-build-tex-repeat.log", "python scripts/build_dissertation_tex.py --strip-heading-numbers --input provenance/WEITZENBOCK_SPINOR_44.md --output build/phase6/WEITZENBOCK_SPINOR_44-repeat.tex")
)
foreach ($step in $steps) {
    & "$PSScriptRoot\run_logged.ps1" -LogPath $step[0] -Command $step[1]
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

for ($pass = 1; $pass -le 3; $pass++) {
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\phase6-pdf-a$pass.log" `
        -Command "pdflatex -interaction=nonstopmode -halt-on-error -jobname=WEITZENBOCK_SPINOR_44 -output-directory=build/phase6/pdf-a provenance/WEITZENBOCK_SPINOR_44.tex"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\phase6-pdf-b$pass.log" `
        -Command "pdflatex -interaction=nonstopmode -halt-on-error -jobname=WEITZENBOCK_SPINOR_44 -output-directory=build/phase6/pdf-b build/phase6/WEITZENBOCK_SPINOR_44-repeat.tex"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

& "$PSScriptRoot\run_logged.ps1" `
    -LogPath "logs\phase6-check-pdf.log" `
    -Command "python scripts/check_provenance_pdf.py --edition weitzenbock-spinor-44 build/phase6/pdf-a/WEITZENBOCK_SPINOR_44.pdf --repeat build/phase6/pdf-b/WEITZENBOCK_SPINOR_44.pdf"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$pairs = @(
    @("artifacts\weitzenbock-spin-geometry\geometry.json", "build\phase6\geometry-repeat.json"),
    @("artifacts\weitzenbock-spin-geometry\wolfram-report.json", "build\phase6\wolfram-report-repeat.json"),
    @("studies\weitzenbock_spinor_44\src\generated.rs", "build\phase6\generated-repeat.rs"),
    @("artifacts\weitzenbock-spinor-44\history.csv", "build\phase6\weitzenbock-repeat\history.csv"),
    @("artifacts\weitzenbock-spinor-44\summary.json", "build\phase6\weitzenbock-repeat\summary.json"),
    @("notebooks\DiracTriality.nb", "build\phase6\DiracTriality-repeat.nb"),
    @("provenance\WEITZENBOCK_SPINOR_44.tex", "build\phase6\WEITZENBOCK_SPINOR_44-repeat.tex"),
    @("build\phase6\pdf-a\WEITZENBOCK_SPINOR_44.pdf", "build\phase6\pdf-b\WEITZENBOCK_SPINOR_44.pdf")
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
    "build\phase6\pdf-a\WEITZENBOCK_SPINOR_44.log", `
    "build\phase6\pdf-b\WEITZENBOCK_SPINOR_44.log" `
    -Pattern $warningPattern
if ($issues) {
    $issues | ForEach-Object { Write-Output $_.Line }
    throw "Phase 6 LaTeX warnings remain"
}

Copy-Item "build\phase6\pdf-a\WEITZENBOCK_SPINOR_44.pdf" `
    "provenance\WEITZENBOCK_SPINOR_44.pdf" -Force

Write-Output "vendor_commit=$actualVendorCommit"
Write-Output "geometry_sha256=$((Get-FileHash artifacts\weitzenbock-spin-geometry\geometry.json -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "wolfram_sha256=$((Get-FileHash artifacts\weitzenbock-spin-geometry\wolfram-report.json -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "history_sha256=$((Get-FileHash artifacts\weitzenbock-spinor-44\history.csv -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "summary_sha256=$((Get-FileHash artifacts\weitzenbock-spinor-44\summary.json -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "notebook_sha256=$((Get-FileHash notebooks\DiracTriality.nb -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "provenance_pdf_sha256=$((Get-FileHash provenance\WEITZENBOCK_SPINOR_44.pdf -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "phase6_weitzenbock_spinor_verification=OK"
exit 0