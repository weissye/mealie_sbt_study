[CmdletBinding()]
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent)
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path (Join-Path $Root 'src\compile_maps.py'))) { throw 'Project source files are missing.' }
foreach ($name in @('model', 'maps', 'runs', 'evidence', 'data', 'generated', 'provengo', 'storage-audit')) {
    New-Item -ItemType Directory -Path (Join-Path $Root $name) -Force | Out-Null
}
$volumeRoot = [IO.Path]::GetPathRoot((Resolve-Path $Root).Path)
$drive = Get-PSDrive -Name $volumeRoot.Substring(0,1) -ErrorAction SilentlyContinue
if ($drive) { Write-Host ('Free disk space: {0:N2} GiB' -f ($drive.Free / 1GB)) }
& (Join-Path $PSScriptRoot 'Compile-Mealie-Maps.ps1') -Root $Root
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python = Get-StudyPython
$arguments = @($python.Prefix) + @('-m', 'unittest', 'discover', '-s', (Join-Path $Root 'tests'), '-v')
Push-Location $Root
try {
    & $python.Exe @arguments
    if ($LASTEXITCODE -ne 0) { throw 'Acceptance unit tests failed.' }
} finally { Pop-Location }
Write-Host 'MEALIE_STUDY_STATIC_INITIALIZATION_PASS'
Write-Host 'No server requests were sent. Live M1 acceptance has not been performed.'
