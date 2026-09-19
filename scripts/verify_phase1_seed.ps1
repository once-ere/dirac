[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repositoryRoot

$artifactPath = "artifacts\exact\cl44-seed.json"
$repeatPath = "build\phase1\cl44-seed-repeat.json"

if (Test-Path -LiteralPath $artifactPath) {
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\phase1-backup-generated-seed.log" `
        -Command "python scripts/backup_files.py artifacts/exact/cl44-seed.json"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

New-Item -ItemType Directory -Path (Split-Path -Parent $repeatPath) -Force |
    Out-Null

$steps = @(
    @(
        "logs/phase1-cl44-seed.log",
        "wolframscript -file scripts/verify_cl44.wls -- $artifactPath"
    ),
    @(
        "logs/phase1-cl44-seed-repeat.log",
        "wolframscript -file scripts/verify_cl44.wls -- $repeatPath"
    ),
    @(
        "logs/phase1-cl44-independent.log",
        "python scripts/check_cl44_fixture.py"
    ),
    @(
        "logs/phase1-python-tests.log",
        "python -m unittest discover -s tests -v"
    )
)

foreach ($step in $steps) {
    & "$PSScriptRoot\run_logged.ps1" -LogPath $step[0] -Command $step[1]
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$artifactHash = (Get-FileHash -LiteralPath $artifactPath -Algorithm SHA256).Hash
$repeatHash = (Get-FileHash -LiteralPath $repeatPath -Algorithm SHA256).Hash
if ($artifactHash -ne $repeatHash) {
    Write-Output "ERROR: repeated seed generation changed bytes"
    exit 1
}

Write-Output "cl44_seed_sha256=$($artifactHash.ToLowerInvariant())"
Write-Output "phase1_seed_verification=OK"
exit 0