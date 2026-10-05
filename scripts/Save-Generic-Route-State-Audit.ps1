[CmdletBinding()]
param([string]$Root=(Split-Path $PSScriptRoot -Parent),[switch]$Push)
$ErrorActionPreference='Stop'
$Root=[IO.Path]::GetFullPath($Root)
$gitRoot=git -C $Root rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0 -or [IO.Path]::GetFullPath($gitRoot) -ne $Root) { throw 'Expected the study repository root.' }
$branch=git -C $Root symbolic-ref --short HEAD
if ($LASTEXITCODE -ne 0) { throw 'A named branch is required.' }
$paths=@(
    'README-ROUTE-STATE-AUDIT.md',
    'docs/research/20261005/Mealie_Read_Only_Route_Qualification.md',
    'generic-generator/route_state_audit_validation.json',
    'generic-generator/tests/test_route_state_audit.py',
    'generic-generator/tools/audit_route_state.py',
    'scripts/Inspect-Generic-Route-State.ps1',
    'scripts/Save-Generic-Route-State-Audit.ps1'
)
foreach ($path in $paths) {
    if (-not (Test-Path -LiteralPath (Join-Path $Root $path))) { throw "Missing release file: $path" }
}
git -C $Root add -f -- @paths
if ($LASTEXITCODE -ne 0) { throw 'Audit source staging failed.' }
git -C $Root diff --cached --quiet -- @paths
$diffCode=$LASTEXITCODE
if ($diffCode -eq 1) {
    git -C $Root commit --only -m 'Add read-only qualification of archived route resources' -- @paths
    if ($LASTEXITCODE -ne 0) { throw 'Audit source commit failed.' }
} elseif ($diffCode -ne 0) { throw 'Audit source staged check failed.' }
if ($Push) {
    git -C $Root push origin HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Audit source push failed.' }
    $localHead=git -C $Root rev-parse HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Local commit verification failed.' }
    $remoteLine=git -C $Root ls-remote origin ("refs/heads/"+$branch)
    if ($LASTEXITCODE -ne 0 -or -not $remoteLine -or (($remoteLine -split '\s+')[0] -ne $localHead)) { throw 'Remote commit verification failed.' }
    Write-Host "AUDIT_SOURCE_PUSH_VERIFIED: $localHead"
}
