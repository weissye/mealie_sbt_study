[CmdletBinding()]
param([string]$Root = (Split-Path $PSScriptRoot -Parent), [switch]$Push)
$ErrorActionPreference = 'Stop'
$rootPath = [IO.Path]::GetFullPath($Root)
$evidence = Join-Path $rootPath 'evidence\reference-lifecycle-20261004'
$downloads = Join-Path $env:USERPROFILE 'Downloads'
$originals = @(
    @{Source=(Join-Path $downloads 'mealie-reference-lifecycle-20261004-183736\campaign.zip'); Name='accepted-campaign.zip'; Hash='d4cf480c916bc04b35e6eddbfac2a3da1892451af767f4984cc027d8389cab0d'},
    @{Source=(Join-Path $downloads 'mealie-reference-lifecycle-20261004-182535\campaign.zip'); Name='stopped-display-control.zip'; Hash='e23ef16382df8694fdbd7c4b4bf025521a3ea608dc6d11f54815f364c453f2d2'}
)
$gitRoot = & git -C $rootPath rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0 -or [IO.Path]::GetFullPath($gitRoot).TrimEnd([char]92,[char]47) -ne $rootPath.TrimEnd([char]92,[char]47)) { throw 'The requested study root must be its own Git repository.' }
$branch = & git -C $rootPath symbolic-ref --short HEAD
if ($LASTEXITCODE -ne 0) { throw 'A named Git branch is required.' }
foreach ($item in $originals) {
    $target = Join-Path $evidence $item.Name
    if (Test-Path -LiteralPath $target) {
        if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.Hash) { throw 'An existing evidence file differs; nothing was overwritten.' }
    } else {
        if (-not (Test-Path -LiteralPath $item.Source)) { throw "Original campaign is missing: $($item.Source)" }
        if ((Get-FileHash -LiteralPath $item.Source -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.Hash) { throw 'Original campaign checksum mismatch.' }
        Copy-Item -LiteralPath $item.Source -Destination $target
        if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.Hash) { throw 'Evidence copy verification failed.' }
    }
}
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python = Get-StudyPython
& $python.Exe @($python.Prefix) -B (Join-Path $evidence 'verify_reference_campaign.py')
if ($LASTEXITCODE -ne 0) { throw 'Offline campaign verification failed. Git commit was not started.' }
$pathsJson = [IO.File]::ReadAllText((Join-Path $evidence 'source-paths.json'))
$sourcePaths = ConvertFrom-Json -InputObject $pathsJson
$paths = [Collections.Generic.List[string]]::new()
foreach ($relative in $sourcePaths) {
    if ($relative -isnot [string] -or -not (Test-Path -LiteralPath (Join-Path $rootPath $relative))) { throw "Expected source is missing: $relative" }
    $paths.Add($relative)
}
$paths.Add('evidence/reference-lifecycle-20261004')
$paths.Add('docs/research/20261004/Mealie_Reference_Deletion_Findings.md')
$paths.Add('scripts/Save-Mealie-Reference-Work.ps1')
$checkpoint = 'checkpoint-before-reference-work-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
& git -C $rootPath branch $checkpoint
if ($LASTEXITCODE -ne 0) { throw 'Checkpoint branch creation failed.' }
$pathspec = Join-Path $env:TEMP ('reference-pathspec-' + [guid]::NewGuid().ToString('N'))
try {
    [IO.File]::WriteAllText($pathspec, (($paths.ToArray() -join [char]0) + [char]0), [Text.UTF8Encoding]::new($false))
    & git -C $rootPath add -f "--pathspec-from-file=$pathspec" --pathspec-file-nul
    if ($LASTEXITCODE -ne 0) { throw 'Git staging failed.' }
    & git -C $rootPath diff --cached --quiet "--" @($paths.ToArray())
    $diffCode = $LASTEXITCODE
    if ($diffCode -eq 1) {
        & git -C $rootPath commit --only -m 'Preserve reference deletion controls, evidence and generator fixes' "--pathspec-from-file=$pathspec" --pathspec-file-nul
        if ($LASTEXITCODE -ne 0) { throw 'Git commit failed.' }
    } elseif ($diffCode -ne 0) { throw 'Git staged comparison failed.' }
    $head = & git -C $rootPath rev-parse HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Reading the commit failed.' }
    Write-Host "REFERENCE_WORK_COMMIT_READY: $head"
    if ($Push) {
        & git -C $rootPath push -u origin $branch
        if ($LASTEXITCODE -ne 0) { throw 'Git push failed. The local commit and original evidence remain preserved.' }
        $remote = & git -C $rootPath ls-remote origin "refs/heads/$branch"
        if ($LASTEXITCODE -ne 0 -or (($remote -split '\s+')[0] -ne $head)) { throw 'Remote commit verification failed.' }
        Write-Host "REFERENCE_WORK_PUSH_VERIFIED: $head"
    }
} finally {
    if (Test-Path -LiteralPath $pathspec) { Remove-Item -LiteralPath $pathspec }
}
