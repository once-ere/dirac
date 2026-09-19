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
    "studies/triality_transport/src/generated.rs",
    "artifacts/triality-transport/trajectory.csv",
    "artifacts/triality-transport/summary.json"
)
$existing = @($generated | Where-Object { Test-Path -LiteralPath $_ })
if ($existing.Count -gt 0) {
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\phase2-backup-generated-transport.log" `
        -Command ("python scripts/backup_files.py " + ($existing -join " "))
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

New-Item -ItemType Directory -Path "build\phase2" -Force | Out-Null

$steps = @(
    @(
        "logs/phase2-generate-triality-constants.log",
        "python scripts/generate_triality_transport_constants.py"
    ),
    @(
        "logs/phase2-generate-triality-constants-repeat.log",
        "python scripts/generate_triality_transport_constants.py --output build/phase2/generated-repeat.rs"
    ),
    @(
        "logs/phase2-cargo-fmt-check.log",
        "cargo fmt -p triality_transport -- --check"
    ),
    @(
        "logs/phase2-triality-transport-clippy.log",
        "cargo clippy -p triality_transport --all-targets -- -D warnings"
    ),
    @(
        "logs/phase2-triality-transport-tests.log",
        "cargo test -p triality_transport"
    ),
    @(
        "logs/phase2-python-tests.log",
        "python -m unittest discover -s tests -v"
    ),
    @(
        "logs/phase2-triality-transport-run.log",
        "cargo run --release -p triality_transport -- --output artifacts/triality-transport"
    ),
    @(
        "logs/phase2-triality-transport-repeat.log",
        "cargo run --release -p triality_transport -- --output build/phase2/triality-transport-repeat"
    ),
    @(
        "logs/phase2-triality-transport-check.log",
        "python scripts/check_triality_transport.py --repeat build/phase2/triality-transport-repeat"
    )
)

foreach ($step in $steps) {
    & "$PSScriptRoot\run_logged.ps1" -LogPath $step[0] -Command $step[1]
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$generatedHash = (
    Get-FileHash -LiteralPath "studies\triality_transport\src\generated.rs" -Algorithm SHA256
).Hash
$repeatHash = (
    Get-FileHash -LiteralPath "build\phase2\generated-repeat.rs" -Algorithm SHA256
).Hash
if ($generatedHash -ne $repeatHash) {
    Write-Output "ERROR: generated Rust constants changed bytes"
    exit 1
}

Write-Output "vendor_commit=$actualVendorCommit"
Write-Output "generated_constants_sha256=$($generatedHash.ToLowerInvariant())"
Write-Output "phase2_triality_transport_verification=OK"
exit 0