[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repositoryRoot

$branch = git branch --show-current
$head = git rev-parse --verify HEAD 2>$null
if ($LASTEXITCODE -ne 0) {
    $head = "unborn"
}
$phaseTag = git tag --list "phase5-curved-spin-gravity-green" |
    Select-Object -First 1
if (-not $phaseTag) {
    $phaseTag = git tag --list "learn-dissertation-green" |
        Select-Object -First 1
}
if (-not $phaseTag) {
    $phaseTag = git tag --list "final-release-green" |
        Select-Object -First 1
}
if (-not $phaseTag) {
    $phaseTag = git tag --list "phase*" --sort=-creatordate |
        Select-Object -First 1
}
if (-not $phaseTag) {
    $phaseTag = "none"
}
$dirty = @(git status --short)
$manifestPath = Join-Path $repositoryRoot "audit\source-manifest.json"
$manifestHash = if (Test-Path -LiteralPath $manifestPath) {
    (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
} else {
    "missing"
}
$nextActionMatch = Select-String -LiteralPath "PROGRESS.md" -Pattern "^Next action:" |
    Select-Object -First 1
$nextAction = if ($nextActionMatch) {
    $nextActionMatch.Line.Substring("Next action:".Length).Trim()
} else {
    "missing"
}

Write-Output "repository=$repositoryRoot"
Write-Output "branch=$branch"
Write-Output "head=$head"
Write-Output "dirty_count=$($dirty.Count)"
Write-Output "latest_phase_tag=$phaseTag"
Write-Output "source_manifest_sha256=$manifestHash"
Write-Output "latest_verification=public phase5 release f9fef6a47b9cb5767c2f1150e9795798bfe8adef"
Write-Output "next_action=$nextAction"
if ($dirty.Count -gt 0) {
    Write-Output "dirty_files_begin"
    $dirty | ForEach-Object { Write-Output $_ }
    Write-Output "dirty_files_end"
}