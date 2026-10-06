param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [string]$Username = 'changeme@example.com',
    [string]$BaseUrl = 'http://127.0.0.1:9925',
    [ValidateSet('Both', 'Distinct', 'Merge')][string]$Scenario = 'Both',
    [string]$Jar
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $Root
& py -3 -B (Join-Path $Root 'tools\test_mealie_distinct_merge_renderer.py')
if ($LASTEXITCODE -ne 0) { throw 'Offline renderer verification failed. Live execution was not started.' }
$scenarios = if ($Scenario -eq 'Both') { @('distinct', 'merge') } else { @($Scenario.ToLowerInvariant()) }
foreach ($case in $scenarios) {
    $arguments = @('-3', '-B', (Join-Path $Root 'tools\run_mealie_distinct_merge.py'),
        '--root', $Root, '--username', $Username, '--base-url', $BaseUrl, '--scenario', $case)
    if ($Jar) { $arguments += @('--jar', $Jar) }
    & py @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Scenario $case was not accepted. Preserve its printed review.zip. No live retry or remaining scenario was performed."
    }
}
Write-Host 'REQUESTED_NATIVE_SCENARIOS_COMPLETED. Preserve each printed review.zip.'
