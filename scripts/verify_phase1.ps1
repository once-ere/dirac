[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repositoryRoot

$artifacts = @(
    "artifacts/exact/cl44-seed.json",
    "artifacts/exact/split-octonion.json",
    "artifacts/exact/triality44.json"
)
$existing = @($artifacts | Where-Object { Test-Path -LiteralPath $_ })
if ($existing.Count -gt 0) {
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\phase1-backup-generated-exact.log" `
        -Command ("python scripts/backup_files.py " + ($existing -join " "))
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$repeatDirectory = "build\phase1"
New-Item -ItemType Directory -Path $repeatDirectory -Force | Out-Null

$steps = @(
    @(
        "logs/phase1-cl44-seed.log",
        "wolframscript -file scripts/verify_cl44.wls -- artifacts/exact/cl44-seed.json"
    ),
    @(
        "logs/phase1-split-octonion.log",
        "wolframscript -file scripts/verify_split_octonion.wls -- artifacts/exact/split-octonion.json"
    ),
    @(
        "logs/phase1-triality44.log",
        "wolframscript -file scripts/verify_triality44.wls -- artifacts/exact/triality44.json"
    ),
    @(
        "logs/phase1-cl44-seed-repeat.log",
        "wolframscript -file scripts/verify_cl44.wls -- build/phase1/cl44-seed-repeat.json"
    ),
    @(
        "logs/phase1-split-octonion-repeat.log",
        "wolframscript -file scripts/verify_split_octonion.wls -- build/phase1/split-octonion-repeat.json"
    ),
    @(
        "logs/phase1-triality44-repeat.log",
        "wolframscript -file scripts/verify_triality44.wls -- build/phase1/triality44-repeat.json"
    ),
    @(
        "logs/phase1-cl44-independent.log",
        "python scripts/check_cl44_fixture.py"
    ),
    @(
        "logs/phase1-split-octonion-independent.log",
        "python scripts/check_split_octonion_fixture.py"
    ),
    @(
        "logs/phase1-triality44-independent.log",
        "python -u scripts/check_triality44_fixture.py"
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

$pairs = @(
    @("artifacts\exact\cl44-seed.json", "build\phase1\cl44-seed-repeat.json"),
    @("artifacts\exact\split-octonion.json", "build\phase1\split-octonion-repeat.json"),
    @("artifacts\exact\triality44.json", "build\phase1\triality44-repeat.json")
)
foreach ($pair in $pairs) {
    $primaryHash = (Get-FileHash -LiteralPath $pair[0] -Algorithm SHA256).Hash
    $repeatHash = (Get-FileHash -LiteralPath $pair[1] -Algorithm SHA256).Hash
    if ($primaryHash -ne $repeatHash) {
        Write-Output "ERROR: repeated exact generation changed bytes: $($pair[0])"
        exit 1
    }
    Write-Output "$($pair[0])_sha256=$($primaryHash.ToLowerInvariant())"
}

Write-Output "phase1_exact_verification=OK"
exit 0