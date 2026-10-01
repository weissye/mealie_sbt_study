[CmdletBinding()]
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent),
    [string]$Username = 'changeme@example.com',
    [string]$ReviewZip = (Join-Path $env:USERPROFILE 'Downloads\mealie_identity_review.zip')
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python = Get-StudyPython
$arguments = @($python.Prefix) + @((Join-Path $Root 'src\accept_identity.py'), '--root', $Root, '--username', $Username, '--review-zip', $ReviewZip)
& $python.Exe @arguments
if ($LASTEXITCODE -ne 0) { throw ('Identity acceptance did not pass. Review package: ' + $ReviewZip) }
Write-Host 'Authentication and U1/G1/H1 identity acceptance passed. Fixture setup and replay are still pending.'
