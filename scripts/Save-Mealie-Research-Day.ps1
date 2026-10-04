[CmdletBinding()]
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent),
    [switch]$Push
)
$ErrorActionPreference = 'Stop'
$rootPath = [IO.Path]::GetFullPath($Root).TrimEnd([char]92,[char]47)
$repoRoot = git -C $rootPath rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0) { throw 'The study folder is not a Git repository.' }
if ([IO.Path]::GetFullPath($repoRoot.Trim()).TrimEnd([char]92,[char]47) -ne $rootPath) {
    throw 'The supplied folder must be the repository root.'
}
$branch = git -C $rootPath branch --show-current
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($branch)) { throw 'A named branch is required.' }
$branch = $branch.Trim()
$evidencePath = 'evidence/mealie-quantity-family-20261004'
$evidence = Join-Path $rootPath $evidencePath
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python = Get-StudyPython
& $python.Exe @($python.Prefix) -B (Join-Path $evidence 'verify_freeze.py')
if ($LASTEXITCODE -ne 0) { throw 'Evidence verification failed. Nothing was staged.' }
$sourcePathsJson = [IO.File]::ReadAllText((Join-Path $evidence 'source-paths.json'))
$sourcePaths = ConvertFrom-Json -InputObject $sourcePathsJson
$selected = @($evidencePath, 'docs/research/20261004', 'scripts/Save-Mealie-Research-Day.ps1')
$sourceHashes = @()
foreach ($relative in $sourcePaths) {
    if ($relative -isnot [string]) { throw 'Source path entries must be individual strings.' }
    if ($relative -match '(^|/)\.\.' -or [IO.Path]::IsPathRooted($relative)) { throw 'Invalid source path.' }
    $path = Join-Path $rootPath $relative
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        if ((Get-Item -LiteralPath $path).Length -gt 50MB) { throw "Unexpected large source file: $relative" }
        $selected += $relative
        $sourceHashes += [pscustomobject]@{path=$relative; sha256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
    } else {
        $sourceHashes += [pscustomobject]@{path=$relative; status='NOT_PRESENT_LOCALLY'; archived_snapshot_preserved=$true}
    }
}
$sourceHashes | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $rootPath 'docs/research/20261004/git-source-hashes.json') -Encoding UTF8
$checkpoint = 'checkpoint-before-research-freeze-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
git -C $rootPath branch $checkpoint HEAD
if ($LASTEXITCODE -ne 0) { throw 'Checkpoint branch creation failed.' }
$pathList = Join-Path ([IO.Path]::GetTempPath()) ('mealie-git-paths-' + [guid]::NewGuid().ToString('N') + '.txt')
try {
    $selected = @($selected | Sort-Object -Unique)
    [IO.File]::WriteAllText($pathList, (($selected -join [char]0) + [char]0), [Text.UTF8Encoding]::new($false))
    git -C $rootPath add -f --pathspec-from-file=$pathList --pathspec-file-nul
    if ($LASTEXITCODE -ne 0) { throw 'Staging selected research files failed.' }
    git -C $rootPath commit --only -m 'Freeze Mealie quantity discrepancy evidence and research work for 2026-10-04' --pathspec-from-file=$pathList --pathspec-file-nul
    if ($LASTEXITCODE -ne 0) {
        $selectedChanges = @(git -C $rootPath status --porcelain --untracked-files=no -- $evidencePath 'docs/research/20261004' 'generic-generator' 'scripts')
        if ($LASTEXITCODE -ne 0 -or $selectedChanges.Count -gt 0) { throw 'Research commit failed. Files and checkpoint were preserved.' }
        Write-Host 'No selected changes needed a new commit.'
    }
    $head = (git -C $rootPath rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read the final commit.' }
    Write-Host "RESEARCH_COMMIT_READY: $head"
    Write-Host "Branch: $branch"
    Write-Host "Checkpoint: $checkpoint"
    if ($Push) {
        git -C $rootPath push -u origin $branch
        if ($LASTEXITCODE -ne 0) { throw 'Push failed. The local research commit is preserved; no reset or merge was performed.' }
        $remote = @(git -C $rootPath ls-remote origin ('refs/heads/' + $branch))
        if ($LASTEXITCODE -ne 0 -or $remote.Count -ne 1 -or (($remote[0] -split '\s+')[0] -ne $head)) {
            throw 'Remote branch head could not be verified.'
        }
        Write-Host "RESEARCH_PUSH_VERIFIED: $head"
    }
    Write-Host 'Docker data and running server state were not transferred.'
} finally {
    if (Test-Path -LiteralPath $pathList) { Remove-Item -LiteralPath $pathList -Force }
}
