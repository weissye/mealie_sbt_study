[CmdletBinding()]
param([string]$Root=(Split-Path $PSScriptRoot -Parent),[switch]$Push)
$ErrorActionPreference='Stop'
$Root=[IO.Path]::GetFullPath($Root)
$gitRoot=git -C $Root rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0 -or [IO.Path]::GetFullPath($gitRoot) -ne $Root) { throw 'Expected the study repository root.' }
$branch=git -C $Root symbolic-ref --short HEAD
if ($LASTEXITCODE -ne 0) { throw 'A named branch is required.' }
$paths=@(
    'README-COPY-ISOLATION.md',
    'docs/research/20261005/Mealie_Copy_Isolation_Campaign.md',
    'evidence/name-route-20261005/campaign-original.zip',
    'evidence/name-route-20261005/verification.json',
    'evidence/name-route-20261005/verify_campaign.py',
    'generic-generator/copy_isolation_validation.json',
    'generic-generator/generator_v56/render/compiled_relationships.py',
    'generic-generator/generator_v56/render/copy_isolation.py',
    'generic-generator/profiles/mealie-copy-control-runtime.json',
    'generic-generator/profiles/mealie-copy-control-scope.json',
    'generic-generator/profiles/mealie-copy-copy-first-runtime.json',
    'generic-generator/profiles/mealie-copy-copy-first-scope.json',
    'generic-generator/profiles/mealie-copy-internal-reference-runtime.json',
    'generic-generator/profiles/mealie-copy-internal-reference-scope.json',
    'generic-generator/profiles/mealie-copy-source-first-runtime.json',
    'generic-generator/profiles/mealie-copy-source-first-scope.json',
    'generic-generator/tests/native_http_mock.js',
    'generic-generator/tests/test_copy_isolation.py',
    'generic-generator/tools/classify_reference_review.py',
    'generic-generator/tools/copy_raw_evidence.py',
    'generic-generator/tools/copy_receipts.py',
    'generic-generator/tools/relationship_execution.py',
    'generic-generator/tools/verify_copy_campaign.py',
    'scripts/Run-Generic-Copy-Isolation.ps1',
    'scripts/Save-Generic-Copy-Evidence.ps1',
    'scripts/Save-Generic-Copy-Isolation.ps1'
)
foreach ($path in $paths) {
    if (-not (Test-Path -LiteralPath (Join-Path $Root $path))) { throw "Missing release file: $path" }
}
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python=Get-StudyPython
& $python.Exe @($python.Prefix) -B (Join-Path $Root 'evidence\name-route-20261005\verify_campaign.py')
if ($LASTEXITCODE -ne 0) { throw 'Archived route evidence verification failed. Git was not changed.' }
git -C $Root add -f -- @paths
if ($LASTEXITCODE -ne 0) { throw 'Copy-isolation source staging failed.' }
git -C $Root diff --cached --quiet -- @paths
$diffCode=$LASTEXITCODE
if ($diffCode -eq 1) {
    git -C $Root commit --only -m 'Add generic linked-copy isolation and archive qualified routing evidence' -- @paths
    if ($LASTEXITCODE -ne 0) { throw 'Copy-isolation source commit failed.' }
} elseif ($diffCode -ne 0) { throw 'Copy-isolation source staged check failed.' }
if ($Push) {
    git -C $Root push origin HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Copy-isolation source push failed.' }
    $localHead=git -C $Root rev-parse HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Local commit verification failed.' }
    $remoteLine=git -C $Root ls-remote origin ("refs/heads/"+$branch)
    if ($LASTEXITCODE -ne 0 -or -not $remoteLine -or (($remoteLine -split '\s+')[0] -ne $localHead)) { throw 'Remote commit verification failed.' }
    Write-Host "COPY_ISOLATION_SOURCE_PUSH_VERIFIED: $localHead"
}
