[CmdletBinding()]
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent),
    [string]$Username = 'changeme@example.com',
    [string]$Project,
    [string]$ReviewZip = (Join-Path $env:USERPROFILE 'Downloads\mealie_standalone_review.zip')
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python = Get-StudyPython
$arguments = @($python.Prefix) + @((Join-Path $Root 'src\run_mealie_standalone.py'), '--root', $Root, '--username', $Username, '--review-zip', $ReviewZip)
if ($Project) { $arguments += @('--project', $Project) }
& $python.Exe @arguments
if ($LASTEXITCODE -ne 0) { throw ('Standalone acceptance did not pass. Inspect before retrying: ' + $ReviewZip) }
