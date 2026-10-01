[CmdletBinding()]
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent),
    [string]$Username = 'changeme@example.com',
    [string]$ReviewZip = (Join-Path $env:USERPROFILE 'Downloads\mealie_fixture_review.zip')
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python = Get-StudyPython
$arguments = @($python.Prefix) + @((Join-Path $Root 'src\create_pilot_fixture.py'), '--root', $Root, '--username', $Username, '--review-zip', $ReviewZip)
& $python.Exe @arguments
if ($LASTEXITCODE -ne 0) { throw ('Serial fixture was not accepted. Upload the review ZIP before retrying: ' + $ReviewZip) }
Write-Host 'Serial fixture acceptance passed. Provengo schedules and reset/replay are still pending.'
