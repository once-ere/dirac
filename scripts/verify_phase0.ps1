[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repositoryRoot

$generated = @(
    "audit/source-manifest.json",
    "audit/source-manifest.csv",
    "audit/SHA256SUMS",
    "audit/audit-ledger.md",
    "audit/wolfram-structure.json",
    "audit/structural-audit.json"
)
$existing = @($generated | Where-Object { Test-Path -LiteralPath $_ })
if ($existing.Count -gt 0) {
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs/phase0-verify-backup.log" `
        -Command ("python scripts/backup_files.py " + ($existing -join " "))
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$steps = @(
    @("logs/phase0-verify-tests.log", "python -m unittest discover -s tests -v"),
    @("logs/phase0-verify-manifest.log", "python scripts/build_source_manifest.py"),
    @(
        "logs/phase0-verify-wolfram.log",
        "wolframscript -file scripts/audit_wolfram.wls -- audit/source-manifest.json audit/wolfram-structure.json"
    ),
    @(
        "logs/phase0-verify-structural.log",
        "python scripts/build_structural_audit.py"
    ),
    @("logs/phase0-verify-check.log", "python scripts/check_phase0.py")
)

foreach ($step in $steps) {
    & "$PSScriptRoot\run_logged.ps1" -LogPath $step[0] -Command $step[1]
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Output "phase0_verification=OK"
exit 0