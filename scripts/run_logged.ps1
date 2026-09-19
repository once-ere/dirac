[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$LogPath,

    [Parameter(Mandatory = $true)]
    [string]$Command
)

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$resolvedLogPath = if ([System.IO.Path]::IsPathRooted($LogPath)) {
    $LogPath
} else {
    Join-Path $repositoryRoot $LogPath
}

$logDirectory = Split-Path -Parent $resolvedLogPath
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null

$startedAt = [DateTimeOffset]::UtcNow.ToString("o")
@(
    "started_utc=$startedAt"
    "repository=$repositoryRoot"
    "command=$Command"
) | Set-Content -LiteralPath $resolvedLogPath -Encoding utf8NoBOM

$script:commandExitCode = 0
$scriptBlock = [ScriptBlock]::Create($Command)
& {
    & $scriptBlock
    $commandSucceeded = $?
    $nativeExitCode = $LASTEXITCODE
    if (-not $commandSucceeded) {
        $script:commandExitCode = 1
    } elseif ($null -ne $nativeExitCode) {
        $script:commandExitCode = $nativeExitCode
    }
} 2>&1 | Tee-Object -FilePath $resolvedLogPath -Append

$finishedAt = [DateTimeOffset]::UtcNow.ToString("o")
@(
    "finished_utc=$finishedAt"
    "exit_code=$script:commandExitCode"
) | Add-Content -LiteralPath $resolvedLogPath -Encoding utf8NoBOM

exit $script:commandExitCode