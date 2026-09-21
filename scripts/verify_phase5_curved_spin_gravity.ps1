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
    "artifacts/curved-spin-geometry/geometry.json",
    "artifacts/curved-spin-geometry/wolfram-report.json",
    "studies/einstein_spinor_44/src/generated.rs",
    "artifacts/einstein-spinor-44/history.csv",
    "artifacts/einstein-spinor-44/summary.json",
    "provenance/CURVED_SPIN_BUNDLE.tex",
    "provenance/CURVED_SPIN_BUNDLE.pdf",
    "provenance/EINSTEIN_SPINOR_44.tex",
    "provenance/EINSTEIN_SPINOR_44.pdf"
)
$existing = @($generated | Where-Object { Test-Path -LiteralPath $_ })
if ($existing.Count -gt 0) {
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\phase5-backup-generated.log" `
        -Command ("python scripts/backup_files.py " + ($existing -join " "))
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$buildDirectories = @(
    "build\phase5\bundle-pdf-a",
    "build\phase5\bundle-pdf-b",
    "build\phase5\gravity-pdf-a",
    "build\phase5\gravity-pdf-b",
    "build\phase5\einstein-spinor-repeat",
    "build\phase5\einstein-spinor-refined"
)
Remove-Item $buildDirectories -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $buildDirectories -Force | Out-Null

$steps = @(
    @("logs/phase5-build-geometry.log", "python scripts/build_curved_spin_geometry.py"),
    @("logs/phase5-build-geometry-repeat.log", "python scripts/build_curved_spin_geometry.py --output build/phase5/geometry-repeat.json"),
    @("logs/phase5-wolfram-geometry.log", "wolframscript -file scripts/verify_curved_spin_geometry.wls -- artifacts/curved-spin-geometry/wolfram-report.json"),
    @("logs/phase5-wolfram-geometry-repeat.log", "wolframscript -file scripts/verify_curved_spin_geometry.wls -- build/phase5/wolfram-report-repeat.json"),
    @("logs/phase5-check-geometry.log", "python scripts/check_curved_spin_geometry.py"),
    @("logs/phase5-check-einstein-model.log", "python scripts/check_einstein_spinor_model.py"),
    @("logs/phase5-generate-constants.log", "python scripts/generate_einstein_spinor_constants.py"),
    @("logs/phase5-generate-constants-repeat.log", "python scripts/generate_einstein_spinor_constants.py --output build/phase5/einstein-spinor-generated-repeat.rs"),
    @("logs/phase5-cargo-fmt.log", "cargo fmt -p einstein_spinor_44 -- --check"),
    @("logs/phase5-cargo-clippy.log", "cargo clippy -p einstein_spinor_44 --all-targets -- -D warnings"),
    @("logs/phase5-cargo-test.log", "cargo test -p einstein_spinor_44"),
    @("logs/phase5-python-tests.log", "python -m unittest discover -s tests -v"),
    @("logs/phase5-run-gravity.log", "cargo run --release -p einstein_spinor_44 -- --output artifacts/einstein-spinor-44"),
    @("logs/phase5-run-gravity-repeat.log", "cargo run --release -p einstein_spinor_44 -- --output build/phase5/einstein-spinor-repeat"),
    @("logs/phase5-run-gravity-refined.log", "cargo run --release -p einstein_spinor_44 -- --output build/phase5/einstein-spinor-refined --relative-tolerance 1e-12 --absolute-tolerance 1e-14 --maximum-step 0.001"),
    @("logs/phase5-check-gravity.log", "python scripts/check_einstein_spinor_44.py --repeat build/phase5/einstein-spinor-repeat --refined build/phase5/einstein-spinor-refined"),
    @("logs/phase5-build-bundle-tex.log", "python scripts/build_dissertation_tex.py --strip-heading-numbers --input provenance/CURVED_SPIN_BUNDLE.md --output provenance/CURVED_SPIN_BUNDLE.tex"),
    @("logs/phase5-build-bundle-tex-repeat.log", "python scripts/build_dissertation_tex.py --strip-heading-numbers --input provenance/CURVED_SPIN_BUNDLE.md --output build/phase5/CURVED_SPIN_BUNDLE-repeat.tex"),
    @("logs/phase5-build-gravity-tex.log", "python scripts/build_dissertation_tex.py --strip-heading-numbers --input provenance/EINSTEIN_SPINOR_44.md --output provenance/EINSTEIN_SPINOR_44.tex"),
    @("logs/phase5-build-gravity-tex-repeat.log", "python scripts/build_dissertation_tex.py --strip-heading-numbers --input provenance/EINSTEIN_SPINOR_44.md --output build/phase5/EINSTEIN_SPINOR_44-repeat.tex")
)
foreach ($step in $steps) {
    & "$PSScriptRoot\run_logged.ps1" -LogPath $step[0] -Command $step[1]
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$pdfJobs = @(
    @("bundle", "CURVED_SPIN_BUNDLE", "provenance/CURVED_SPIN_BUNDLE.tex", "build/phase5/CURVED_SPIN_BUNDLE-repeat.tex"),
    @("gravity", "EINSTEIN_SPINOR_44", "provenance/EINSTEIN_SPINOR_44.tex", "build/phase5/EINSTEIN_SPINOR_44-repeat.tex")
)
foreach ($job in $pdfJobs) {
    $label, $jobName, $canonicalTex, $repeatTex = $job
    for ($pass = 1; $pass -le 3; $pass++) {
        & "$PSScriptRoot\run_logged.ps1" `
            -LogPath "logs\phase5-$label-pdf-a$pass.log" `
            -Command "pdflatex -interaction=nonstopmode -halt-on-error -jobname=$jobName -output-directory=build/phase5/$label-pdf-a $canonicalTex"
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & "$PSScriptRoot\run_logged.ps1" `
            -LogPath "logs\phase5-$label-pdf-b$pass.log" `
            -Command "pdflatex -interaction=nonstopmode -halt-on-error -jobname=$jobName -output-directory=build/phase5/$label-pdf-b $repeatTex"
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
}

$pdfChecks = @(
    @("curved-spin-bundle", "bundle", "CURVED_SPIN_BUNDLE"),
    @("einstein-spinor-44", "gravity", "EINSTEIN_SPINOR_44")
)
foreach ($check in $pdfChecks) {
    $edition, $label, $jobName = $check
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\phase5-check-$label-pdf.log" `
        -Command "python scripts/check_provenance_pdf.py --edition $edition build/phase5/$label-pdf-a/$jobName.pdf --repeat build/phase5/$label-pdf-b/$jobName.pdf"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$pairs = @(
    @("artifacts\curved-spin-geometry\geometry.json", "build\phase5\geometry-repeat.json"),
    @("artifacts\curved-spin-geometry\wolfram-report.json", "build\phase5\wolfram-report-repeat.json"),
    @("studies\einstein_spinor_44\src\generated.rs", "build\phase5\einstein-spinor-generated-repeat.rs"),
    @("artifacts\einstein-spinor-44\history.csv", "build\phase5\einstein-spinor-repeat\history.csv"),
    @("artifacts\einstein-spinor-44\summary.json", "build\phase5\einstein-spinor-repeat\summary.json"),
    @("provenance\CURVED_SPIN_BUNDLE.tex", "build\phase5\CURVED_SPIN_BUNDLE-repeat.tex"),
    @("provenance\EINSTEIN_SPINOR_44.tex", "build\phase5\EINSTEIN_SPINOR_44-repeat.tex"),
    @("build\phase5\bundle-pdf-a\CURVED_SPIN_BUNDLE.pdf", "build\phase5\bundle-pdf-b\CURVED_SPIN_BUNDLE.pdf"),
    @("build\phase5\gravity-pdf-a\EINSTEIN_SPINOR_44.pdf", "build\phase5\gravity-pdf-b\EINSTEIN_SPINOR_44.pdf")
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
    "build\phase5\bundle-pdf-a\CURVED_SPIN_BUNDLE.log", `
    "build\phase5\bundle-pdf-b\CURVED_SPIN_BUNDLE.log", `
    "build\phase5\gravity-pdf-a\EINSTEIN_SPINOR_44.log", `
    "build\phase5\gravity-pdf-b\EINSTEIN_SPINOR_44.log" `
    -Pattern $warningPattern
if ($issues) {
    $issues | ForEach-Object { Write-Output $_.Line }
    throw "Phase 5 LaTeX warnings remain"
}

Copy-Item "build\phase5\bundle-pdf-a\CURVED_SPIN_BUNDLE.pdf" `
    "provenance\CURVED_SPIN_BUNDLE.pdf" -Force
Copy-Item "build\phase5\gravity-pdf-a\EINSTEIN_SPINOR_44.pdf" `
    "provenance\EINSTEIN_SPINOR_44.pdf" -Force

Write-Output "vendor_commit=$actualVendorCommit"
Write-Output "geometry_sha256=$((Get-FileHash artifacts\curved-spin-geometry\geometry.json -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "gravity_history_sha256=$((Get-FileHash artifacts\einstein-spinor-44\history.csv -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "gravity_summary_sha256=$((Get-FileHash artifacts\einstein-spinor-44\summary.json -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "bundle_pdf_sha256=$((Get-FileHash provenance\CURVED_SPIN_BUNDLE.pdf -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "gravity_pdf_sha256=$((Get-FileHash provenance\EINSTEIN_SPINOR_44.pdf -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "phase5_curved_spin_gravity_verification=OK"
exit 0
