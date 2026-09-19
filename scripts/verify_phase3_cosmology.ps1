[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repositoryRoot

$expectedVendorCommit = "d1836e6a279d63a90fe2839a0020123245487e76"
$actualVendorCommit = git -C vendor/sundials_rs rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $actualVendorCommit -ne $expectedVendorCommit) {
    Write-Output "ERROR: solver submodule commit mismatch"
    exit 1
}
if (git -C vendor/sundials_rs status --porcelain) {
    Write-Output "ERROR: solver submodule is dirty"
    exit 1
}

$generated = @(
    "studies/spinor_cosmology/src/generated.rs",
    "artifacts/spinor-cosmology/background.csv",
    "artifacts/spinor-cosmology/summary.json"
)
$existing = @($generated | Where-Object { Test-Path -LiteralPath $_ })
if ($existing.Count -gt 0) {
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\phase3-backup-generated-cosmology.log" `
        -Command ("python scripts/backup_files.py " + ($existing -join " "))
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

New-Item -ItemType Directory -Path "build\phase3" -Force | Out-Null

$steps = @(
    @(
        "logs/phase3-generate-cosmology-constants.log",
        "python scripts/generate_spinor_cosmology_constants.py"
    ),
    @(
        "logs/phase3-generate-cosmology-constants-repeat.log",
        "python scripts/generate_spinor_cosmology_constants.py --output build/phase3/generated-repeat.rs"
    ),
    @(
        "logs/phase3-cargo-fmt-check.log",
        "cargo fmt -p spinor_cosmology -- --check"
    ),
    @(
        "logs/phase3-spinor-cosmology-clippy.log",
        "cargo clippy -p spinor_cosmology --all-targets -- -D warnings"
    ),
    @(
        "logs/phase3-spinor-cosmology-tests.log",
        "cargo test -p spinor_cosmology"
    ),
    @(
        "logs/phase3-python-tests.log",
        "python -m unittest discover -s tests -v"
    ),
    @(
        "logs/phase3-spinor-cosmology-run.log",
        "cargo run --release -p spinor_cosmology -- --output artifacts/spinor-cosmology"
    ),
    @(
        "logs/phase3-spinor-cosmology-repeat.log",
        "cargo run --release -p spinor_cosmology -- --output build/phase3/spinor-cosmology-repeat"
    ),
    @(
        "logs/phase3-spinor-cosmology-check.log",
        "python scripts/check_spinor_cosmology.py --repeat build/phase3/spinor-cosmology-repeat"
    )
)

foreach ($step in $steps) {
    & "$PSScriptRoot\run_logged.ps1" -LogPath $step[0] -Command $step[1]
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$generatedHash = (
    Get-FileHash -LiteralPath "studies\spinor_cosmology\src\generated.rs" -Algorithm SHA256
).Hash
$repeatHash = (
    Get-FileHash -LiteralPath "build\phase3\generated-repeat.rs" -Algorithm SHA256
).Hash
if ($generatedHash -ne $repeatHash) {
    Write-Output "ERROR: generated cosmology constants changed bytes"
    exit 1
}

Write-Output "vendor_commit=$actualVendorCommit"
Write-Output "generated_constants_sha256=$($generatedHash.ToLowerInvariant())"
Write-Output "phase3_spinor_cosmology_verification=OK"
exit 0