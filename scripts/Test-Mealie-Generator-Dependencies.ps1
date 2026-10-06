param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [string]$Username = 'changeme@example.com',
    [string]$BaseUrl = 'http://127.0.0.1:9925',
    [string]$ProvengoJar = ''
)
$ErrorActionPreference = 'Stop'
$arguments = @('-3', '-B', (Join-Path $Root 'tools\run_mealie_dependency_acceptance.py'), '--root', $Root, '--username', $Username, '--base-url', $BaseUrl)
if ($ProvengoJar) { $arguments += @('--jar', $ProvengoJar) }
& py @arguments
if ($LASTEXITCODE -ne 0) {
    throw 'Dependency acceptance did not complete. Preserve the printed review.zip. No automatic retry was performed.'
}
