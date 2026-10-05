[CmdletBinding()]
param([string]$Root=(Split-Path $PSScriptRoot -Parent),[switch]$Push)
$ErrorActionPreference='Stop'
$Root=[IO.Path]::GetFullPath($Root)
$gitRoot=git -C $Root rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0 -or [IO.Path]::GetFullPath($gitRoot) -ne $Root) { throw 'Expected the study repository root.' }
$branch=git -C $Root symbolic-ref --short HEAD
if ($LASTEXITCODE -ne 0) { throw 'A named branch is required.' }
$paths=@(
    'README-NAME-ROUTE-CAMPAIGN.md',
    'docs/research/20261005/Mealie_Name_Driven_Route_Campaign.md',
    'generic-generator/generator_v56/render/route_identity.py',
    'generic-generator/name_route_campaign_validation.json',
    'generic-generator/profiles/mealie-name-route-control-runtime.json',
    'generic-generator/profiles/mealie-name-route-control-scope.json',
    'generic-generator/profiles/mealie-name-route-rename-runtime.json',
    'generic-generator/profiles/mealie-name-route-rename-scope.json',
    'generic-generator/profiles/mealie-name-route-reuse-runtime.json',
    'generic-generator/profiles/mealie-name-route-reuse-scope.json',
    'generic-generator/tests/native_http_mock.js',
    'generic-generator/tests/test_name_route_identity.py',
    'generic-generator/tests/test_route_raw_evidence.py',
    'generic-generator/tests/test_route_server_check.py',
    'generic-generator/tools/check_route_server.py',
    'generic-generator/tools/route_raw_evidence.py',
    'generic-generator/tools/route_receipts.py',
    'scripts/Run-Generic-Name-Route-Campaign.ps1',
    'scripts/Save-Generic-Name-Route-Campaign.ps1'
)
foreach ($path in $paths) {
    if (-not (Test-Path -LiteralPath (Join-Path $Root $path))) { throw "Missing release file: $path" }
}
git -C $Root add -f -- @paths
if ($LASTEXITCODE -ne 0) { throw 'Name-route source staging failed.' }
git -C $Root diff --cached --quiet -- @paths
$diffCode=$LASTEXITCODE
if ($diffCode -eq 1) {
    git -C $Root commit --only -m 'Add generic name-driven route campaign with raw write and read evidence' -- @paths
    if ($LASTEXITCODE -ne 0) { throw 'Name-route source commit failed.' }
} elseif ($diffCode -ne 0) { throw 'Name-route source staged check failed.' }
if ($Push) {
    git -C $Root push origin HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Name-route source push failed.' }
    $localHead=git -C $Root rev-parse HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Local commit verification failed.' }
    $remoteLine=git -C $Root ls-remote origin ("refs/heads/"+$branch)
    if ($LASTEXITCODE -ne 0 -or -not $remoteLine -or (($remoteLine -split '\s+')[0] -ne $localHead)) { throw 'Remote commit verification failed.' }
    Write-Host "NAME_ROUTE_SOURCE_PUSH_VERIFIED: $localHead"
}
