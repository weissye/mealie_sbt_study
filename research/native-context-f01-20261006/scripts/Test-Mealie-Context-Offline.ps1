param([string]$Root = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath $Root).Path
& py -3 -B (Join-Path $Root 'tests\test_context_model.py')
if ($LASTEXITCODE -ne 0) { throw 'Generator regression failed.' }
& node (Join-Path $Root 'tests\check_context_callbacks.js') (Join-Path $Root 'generated\spec\js')
if ($LASTEXITCODE -ne 0) { throw 'Callback/DAL regression failed.' }
Write-Host 'OFFLINE_CHECKS_PASS. This is not a native Provengo or SUT acceptance.'
