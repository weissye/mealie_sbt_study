[CmdletBinding()]
param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [switch]$Push
)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath $Root).Path
$evidence = 'evidence/multi-identity-20261005-065704'
$paths = @(
    'evidence/multi-identity-20261005-065704/campaign-original.zip',
    'evidence/multi-identity-20261005-065704/execution-original.txt',
    'evidence/multi-identity-20261005-065704/qualification_oracle.py',
    'evidence/multi-identity-20261005-065704/qualification.json',
    'evidence/multi-identity-20261005-065704/checksums.json',
    'evidence/multi-identity-20261005-065704/HANDOFF.md',
    'evidence/multi-identity-20261005-065704/verify_campaign.py',
    'docs/research/20261005/Mealie_Foreign_Recipe_Reference_Server_Error.md',
    'scripts/Save-Generic-Multi-Identity-Findings.ps1'
)
foreach ($path in $paths) {
    if (-not (Test-Path -LiteralPath (Join-Path $Root $path) -PathType Leaf)) {
        throw "Missing release file: $path"
    }
}
$top = git -C $Root rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0) { throw 'Git repository was not found.' }
if ([IO.Path]::GetFullPath($top.Trim()) -ne [IO.Path]::GetFullPath($Root)) {
    throw 'The selected directory is not the repository root.'
}
$branch = git -C $Root branch --show-current
if ($LASTEXITCODE -ne 0 -or $branch.Trim() -ne 'main') {
    throw 'Expected the main branch. Git was not changed.'
}
# Prefer the existing project resolver so the verifier uses the same Python.
$resolver = Join-Path $PSScriptRoot 'Resolve-Python.ps1'
if (-not (Test-Path -LiteralPath $resolver)) { throw 'Project Python resolver is missing.' }
. $resolver
$python = Get-StudyPython
& $python.Exe @($python.Prefix) -B (Join-Path $Root "$evidence/verify_campaign.py")
if ($LASTEXITCODE -ne 0) { throw 'Evidence verification failed. Git was not changed.' }
git -C $Root add -f -- @paths
if ($LASTEXITCODE -ne 0) { throw 'Evidence staging failed.' }
git -C $Root diff --cached --quiet -- @paths
$difference = $LASTEXITCODE
if ($difference -eq 1) {
    git -C $Root commit --only -m 'Preserve reproduced foreign recipe reference server error' -- @paths
    if ($LASTEXITCODE -ne 0) { throw 'Evidence commit failed.' }
} elseif ($difference -ne 0) {
    throw 'Staged evidence check failed.'
}
$head = git -C $Root rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'Cannot identify the evidence commit.' }
if ($Push) {
    git -C $Root push origin HEAD:refs/heads/main
    if ($LASTEXITCODE -ne 0) { throw 'Git push failed. Local evidence remains preserved.' }
    $remote = git -C $Root ls-remote origin refs/heads/main
    if ($LASTEXITCODE -ne 0 -or -not $remote) { throw 'Remote SHA verification failed.' }
    $remoteHead = ($remote -split '\s+')[0]
    if ($remoteHead -ne $head.Trim()) { throw 'Remote main does not match the local evidence commit.' }
    Write-Host "MULTI_IDENTITY_FINDINGS_PUSH_VERIFIED: $($head.Trim())"
} else {
    Write-Host "MULTI_IDENTITY_FINDINGS_COMMITTED_LOCALLY: $($head.Trim())"
}
