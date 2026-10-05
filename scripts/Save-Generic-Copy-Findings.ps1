[CmdletBinding()]
param([string]$Root=(Split-Path $PSScriptRoot -Parent),[switch]$Push)
$ErrorActionPreference='Stop'
$Root=[IO.Path]::GetFullPath($Root)
$gitRoot=git -C $Root rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0 -or [IO.Path]::GetFullPath($gitRoot) -ne $Root) { throw 'Expected the study repository root.' }
$branch=git -C $Root symbolic-ref --short HEAD
if ($LASTEXITCODE -ne 0) { throw 'A named branch is required.' }
$paths=@(
    'docs/research/20261005/Mealie_Copy_Internal_Reference_Defect.md',
    'evidence/copy-isolation-20261005-082853/HANDOFF.md',
    'evidence/copy-isolation-20261005-082853/campaign-original.zip',
    'evidence/copy-isolation-20261005-082853/minimal-reproductions.json',
    'evidence/copy-isolation-20261005-082853/provenance.json',
    'evidence/copy-isolation-20261005-082853/requalification.json',
    'generic-generator/copy_live_qualification_validation.json',
    'generic-generator/tests/test_copy_live_qualification.py',
    'generic-generator/tools/classify_reference_review.py',
    'generic-generator/tools/copy_receipts.py',
    'generic-generator/tools/verify_copy_campaign.py',
    'scripts/Save-Generic-Copy-Findings.ps1'
)
foreach ($path in $paths) {
    if (-not (Test-Path -LiteralPath (Join-Path $Root $path))) { throw "Missing release file: $path" }
}
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python=Get-StudyPython
$archive=Join-Path $Root 'evidence\copy-isolation-20261005-082853\campaign-original.zip'
& $python.Exe @($python.Prefix) -B (Join-Path $Root 'generic-generator\tools\verify_copy_campaign.py') `
    --campaign $archive --output (Join-Path $Root 'evidence\copy-isolation-20261005-082853\requalification.json')
if ($LASTEXITCODE -ne 0) { throw 'Original copy evidence verification failed. Git was not changed.' }
$savedPythonPath=$env:PYTHONPATH
try {
    $env:PYTHONPATH=(Join-Path $Root 'generic-generator')+[IO.Path]::PathSeparator+$savedPythonPath
    & $python.Exe @($python.Prefix) -B -m unittest discover `
        -s (Join-Path $Root 'generic-generator\tests') -p 'test_copy_live_qualification.py'
    if ($LASTEXITCODE -ne 0) { throw 'Live evidence regression tests failed. Git was not changed.' }
} finally { $env:PYTHONPATH=$savedPythonPath }
git -C $Root add -f -- @paths
if ($LASTEXITCODE -ne 0) { throw 'Copy findings staging failed.' }
git -C $Root diff --cached --quiet -- @paths
$diffCode=$LASTEXITCODE
if ($diffCode -eq 1) {
    git -C $Root commit --only -m 'Archive reproduced copy reference defect and correct display oracle' -- @paths
    if ($LASTEXITCODE -ne 0) { throw 'Copy findings commit failed.' }
} elseif ($diffCode -ne 0) { throw 'Copy findings staged check failed.' }
if ($Push) {
    git -C $Root push origin HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Copy findings push failed.' }
    $localHead=git -C $Root rev-parse HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Local commit verification failed.' }
    $remoteLine=git -C $Root ls-remote origin ("refs/heads/"+$branch)
    if ($LASTEXITCODE -ne 0 -or -not $remoteLine -or (($remoteLine -split '\s+')[0] -ne $localHead)) { throw 'Remote commit verification failed.' }
    Write-Host "COPY_FINDINGS_PUSH_VERIFIED: $localHead"
}
