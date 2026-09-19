[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$Path
)

$ErrorActionPreference = "Stop"
& python "$PSScriptRoot\backup_files.py" @Path
exit $LASTEXITCODE