param([string]$Root=(Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python=Get-StudyPython
& $python.Exe @($python.Prefix) -B (Join-Path $Root 'scripts/verify_bundle.py')
if($LASTEXITCODE -ne 0){throw 'Evidence verification failed. No API requests were sent.'}
