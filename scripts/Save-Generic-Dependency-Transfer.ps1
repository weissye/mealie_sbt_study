[CmdletBinding()]
param([string]$Root=(Split-Path $PSScriptRoot -Parent),[switch]$Push)
$ErrorActionPreference='Stop'
$Root=[IO.Path]::GetFullPath($Root)
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python=Get-StudyPython
& $python.Exe @($python.Prefix) -B (Join-Path $Root 'evidence\stale-snapshot-20261004\test_zip_portability.py')
if ($LASTEXITCODE -ne 0) { throw 'ZIP portability checks failed. Git was not changed.' }
& $python.Exe @($python.Prefix) -B (Join-Path $Root 'evidence\stale-snapshot-20261004\verify_campaign.py')
if ($LASTEXITCODE -ne 0) { throw 'Original evidence verification failed. Git was not changed.' }
$gitRoot=git -C $Root rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0 -or [IO.Path]::GetFullPath($gitRoot) -ne $Root) { throw 'Expected the study repository root.' }
$branch=git -C $Root symbolic-ref --short HEAD
if ($LASTEXITCODE -ne 0) { throw 'A named branch is required.' }
$paths=[string[]](ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $Root 'generic-generator\dependency_transfer_source_paths.json'))))
$paths += @('generic-generator/dependency_transfer_source_paths.json','scripts/Save-Generic-Dependency-Transfer.ps1')
foreach ($path in $paths) {
    if (-not ($path -is [string]) -or -not (Test-Path -LiteralPath (Join-Path $Root $path))) { throw "Missing release path: $path" }
}
$checkpoint='checkpoint-before-transfer-'+(Get-Date -Format 'yyyyMMdd-HHmmss')
git -C $Root branch $checkpoint
if ($LASTEXITCODE -ne 0) { throw 'Checkpoint creation failed.' }
$pathFile=Join-Path $env:TEMP ('stale-paths-'+[guid]::NewGuid().ToString('N')+'.txt')
try {
    [IO.File]::WriteAllText($pathFile,(($paths -join [char]0)+[char]0),[Text.UTF8Encoding]::new($false))
    git -C $Root add -f --pathspec-from-file=$pathFile --pathspec-file-nul
    if ($LASTEXITCODE -ne 0) { throw 'Staging failed.' }
    git -C $Root diff --cached --quiet -- @paths
    $changed=$LASTEXITCODE
    if ($changed -gt 1) { throw 'Staged comparison failed.' }
    if ($changed -eq 1) {
        git -C $Root commit --only -m 'Preserve stale snapshot evidence and add generic dependency transfer campaign' --pathspec-from-file=$pathFile --pathspec-file-nul
        if ($LASTEXITCODE -ne 0) { throw 'Commit failed.' }
    }
    $head=git -C $Root rev-parse HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Commit lookup failed.' }
    Write-Host "TRANSFER_WORK_COMMIT_READY: $head"
    if ($Push) {
        git -C $Root push -u origin $branch
        if ($LASTEXITCODE -ne 0) { throw 'Push failed.' }
        $remote=git -C $Root ls-remote origin "refs/heads/$branch"
        if ($LASTEXITCODE -ne 0 -or (($remote -split '\s+')[0]) -ne $head) { throw 'Remote commit verification failed.' }
        Write-Host "TRANSFER_WORK_PUSH_VERIFIED: $head"
    }
} finally { Remove-Item -LiteralPath $pathFile -ErrorAction SilentlyContinue }
