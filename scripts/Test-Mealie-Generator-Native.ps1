param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [string]$ProvengoJar = '',
    [int]$MaxEvents = 600
)
$ErrorActionPreference = 'Stop'
$tool = Join-Path $Root 'tools\audit_mealie_generator_native.py'
$arguments = @('-3', '-B', $tool, '--root', $Root, '--max-events', "$MaxEvents")
if ($ProvengoJar) { $arguments += @('--jar', $ProvengoJar) }
Write-Host 'Checking the installed generator. Symbolic sampling only.'
& py @arguments
if ($LASTEXITCODE -ne 0) {
    throw 'Native acceptance did not complete. Preserve the printed review.zip; do not launch live replay.'
}
