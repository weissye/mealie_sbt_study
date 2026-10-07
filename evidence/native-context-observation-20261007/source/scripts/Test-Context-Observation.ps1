param([string]$Root = (Split-Path $PSScriptRoot -Parent))
$ErrorActionPreference = 'Stop'
& py -3 -B (Join-Path $Root 'tests\test_generation.py')
if ($LASTEXITCODE -ne 0) { throw 'Generation regression failed.' }
& py -3 -B (Join-Path $Root 'tools\run_fixture.py') --root $Root
if ($LASTEXITCODE -ne 0) {
    throw 'Context acceptance not completed. Preserve the printed review.zip.'
}
