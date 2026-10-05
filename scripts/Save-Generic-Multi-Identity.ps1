[CmdletBinding()]
param([string]$Root=(Split-Path $PSScriptRoot -Parent),[switch]$Push)
$ErrorActionPreference='Stop'
$Root=[IO.Path]::GetFullPath($Root)
$gitRoot=git -C $Root rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0 -or [IO.Path]::GetFullPath($gitRoot) -ne $Root) { throw 'Expected the study repository root.' }
$branch=git -C $Root symbolic-ref --short HEAD
if ($LASTEXITCODE -ne 0) { throw 'A named branch is required.' }
$paths=@(
    'README-MULTI-IDENTITY.md',
    'docs/research/20261005/Mealie_Multi_Identity_Campaign.md',
    'generic-generator/generator_v56/render/compiled_relationships.py',
    'generic-generator/generator_v56/render/identity_program.py',
    'generic-generator/tools/relationship_execution.py',
    'generic-generator/tools/identity_receipts.py',
    'generic-generator/tools/identity_credentials.py',
    'generic-generator/tools/run_identity_campaign.py',
    'generic-generator/tests/test_identity_program.py',
    'generic-generator/tests/identity_http_mock.js',
    'generic-generator/multi_identity_validation.json',
    'scripts/Run-Generic-Multi-Identity.ps1',
    'scripts/Save-Generic-Multi-Identity.ps1',
    'generic-generator/profiles/mealie-identity-shared-scope.json',
    'generic-generator/profiles/mealie-identity-shared-runtime.json',
    'generic-generator/profiles/mealie-identity-separate-scope.json',
    'generic-generator/profiles/mealie-identity-separate-runtime.json'
)
foreach ($path in $paths) {
    if (-not (Test-Path -LiteralPath (Join-Path $Root $path))) { throw "Missing release file: $path" }
}
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python=Get-StudyPython
$savedPythonPath=$env:PYTHONPATH
try {
    $env:PYTHONPATH=(Join-Path $Root 'generic-generator')+[IO.Path]::PathSeparator+$savedPythonPath
    & $python.Exe @($python.Prefix) -B -m unittest discover `
        -s (Join-Path $Root 'generic-generator\tests') -p 'test_identity_program.py'
    if ($LASTEXITCODE -ne 0) { throw 'Multi-identity configuration tests failed. Git was not changed.' }
} finally { $env:PYTHONPATH=$savedPythonPath }
& (Join-Path $PSScriptRoot 'Test-Generic-Generator-Compatibility.ps1') -Root $Root
git -C $Root add -f -- @paths
if ($LASTEXITCODE -ne 0) { throw 'Multi-identity release staging failed.' }
git -C $Root diff --cached --quiet -- @paths
$diffCode=$LASTEXITCODE
if ($diffCode -eq 1) {
    git -C $Root commit --only -m 'Add generic per-actor identity and scope campaigns' -- @paths
    if ($LASTEXITCODE -ne 0) { throw 'Multi-identity release commit failed.' }
} elseif ($diffCode -ne 0) { throw 'Multi-identity release staged check failed.' }
if ($Push) {
    git -C $Root push origin HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Multi-identity release push failed.' }
    $localHead=git -C $Root rev-parse HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Local commit verification failed.' }
    $remoteLine=git -C $Root ls-remote origin ("refs/heads/"+$branch)
    if ($LASTEXITCODE -ne 0 -or -not $remoteLine -or (($remoteLine -split '\s+')[0] -ne $localHead)) { throw 'Remote commit verification failed.' }
    Write-Host "MULTI_IDENTITY_SOURCE_PUSH_VERIFIED: $localHead"
}
