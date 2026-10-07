param(
    [string]$Repository = 'C:\work\temp\mealie_sbt_study',
    [switch]$Push
)
$ErrorActionPreference = 'Stop'
$payload = $PSScriptRoot
& py -3 -B (Join-Path $payload 'verify_archive.py') $payload
if ($LASTEXITCODE -ne 0) { throw 'Offline archive qualification failed; Git unchanged.' }
& git -C $Repository fetch origin
if ($LASTEXITCODE -ne 0) { throw 'Fetch failed; Git unchanged.' }
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$branch = "archive-central-process-$stamp"
$worktree = Join-Path (Split-Path $Repository -Parent) $branch
# Avoid copying the complete repository on a nearly full disk.
& git -C $Repository worktree add --no-checkout -b $branch $worktree origin/main
if ($LASTEXITCODE -ne 0) { throw 'Archive worktree creation failed.' }
& git -C $worktree read-tree HEAD
if ($LASTEXITCODE -ne 0) { throw 'Archive index preparation failed.' }
$relative = 'evidence/native-central-process-binding-20261007'
$target = Join-Path $worktree $relative
New-Item -ItemType Directory -Path $target -Force | Out-Null
Get-ChildItem -LiteralPath $payload -Force | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $target -Recurse
}
& py -3 -B (Join-Path $target 'verify_archive.py') $target
if ($LASTEXITCODE -ne 0) { throw 'Copied archive qualification failed; no commit.' }
& git -C $worktree add -f -- $relative
if ($LASTEXITCODE -ne 0) { throw 'Archive staging failed.' }
& git -C $worktree commit --only -m 'Preserve direct central process generation and native acceptance' -- $relative
if ($LASTEXITCODE -ne 0) { throw 'Commit failed; archive worktree retained.' }
$head = & git -C $worktree rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'Commit verification failed.' }
& git -C $worktree cat-file -e "HEAD:$relative/review-original.zip"
if ($LASTEXITCODE -ne 0) { throw 'Original archive absent from commit.' }
Write-Host "CENTRAL_PROCESS_ARCHIVE_COMMIT_VERIFIED: $head"
Write-Host "Archive worktree: $worktree"
if ($Push) {
    & git -C $worktree push origin HEAD:main
    if ($LASTEXITCODE -ne 0) { throw 'Push failed; archive commit retained. No forced push performed.' }
    $remote = @(& git -C $worktree ls-remote --exit-code origin refs/heads/main)
    if ($LASTEXITCODE -ne 0 -or $remote.Count -ne 1) { throw 'Remote verification failed.' }
    if (($remote[0] -split '\s+')[0] -ne $head) { throw 'Remote HEAD differs; archive commit retained.' }
    Write-Host "CENTRAL_PROCESS_ARCHIVE_PUSH_VERIFIED: $head"
}
Write-Host 'Original checkout, Docker state and existing findings were not changed.'
