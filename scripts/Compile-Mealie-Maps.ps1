[CmdletBinding()]
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent),
    [string]$Contract = '',
    [string]$OutputDirectory = ''
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
if (-not $Contract) { $Contract = Join-Path $Root 'model\mealie-openapi.reference.json' }
if (-not $OutputDirectory) { $OutputDirectory = Join-Path $Root 'maps\reference' }
$python = Get-StudyPython
$arguments = @($python.Prefix) + @(
    (Join-Path $Root 'src\compile_maps.py'), '--contract', $Contract,
    '--profile', (Join-Path $Root 'profiles\mealie.json'), '--out', $OutputDirectory
)
& $python.Exe @arguments
if ($LASTEXITCODE -ne 0) { throw 'Map compilation failed.' }
