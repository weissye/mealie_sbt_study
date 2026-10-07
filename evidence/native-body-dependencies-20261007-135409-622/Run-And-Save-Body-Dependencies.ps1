param(
    [string]$GeneratorRoot = 'C:\work\temp\f03-inline-20261007-090737-711',
    [string]$Repository = 'C:\work\temp\mealie_sbt_study',
    [switch]$Push
)
$ErrorActionPreference = 'Stop'
& py -3 -B (Join-Path $PSScriptRoot 'test_qualification.py')
if ($LASTEXITCODE -ne 0) { throw 'Qualification regressions failed; native run not started.' }
& py -3 -B (Join-Path $PSScriptRoot 'run_native.py') --generator-root $GeneratorRoot
if ($LASTEXITCODE -ne 0) { throw 'Native acceptance stopped; preserve review.zip. No Git changes.' }
$review = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'last-review-path.txt'))
& py -3 -B (Join-Path $PSScriptRoot 'verify_archive.py') $review
if ($LASTEXITCODE -ne 0) { throw 'Archive verification stopped; no Git changes.' }
& git -C $Repository fetch origin
if ($LASTEXITCODE -ne 0) { throw 'Fetch failed; accepted archive retained.' }
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$branch = "archive-body-dependencies-$stamp"
$worktree = Join-Path (Split-Path $Repository -Parent) $branch
& git -C $Repository worktree add --no-checkout -b $branch $worktree origin/main
if ($LASTEXITCODE -ne 0) { throw 'Archive worktree creation failed.' }
& git -C $worktree read-tree HEAD
if ($LASTEXITCODE -ne 0) { throw 'Archive index preparation failed.' }
$relative = "evidence/native-body-dependencies-$stamp"
$target = Join-Path $worktree $relative
New-Item -ItemType Directory -Path $target -Force | Out-Null
Copy-Item -LiteralPath $review -Destination (Join-Path $target 'review-original.zip')
foreach ($name in @('fixture-openapi.json','fixture_server.py','qualification.py','verify_archive.py','run_native.py','test_qualification.py','test_wire_expression.js','Run-And-Save-Body-Dependencies.ps1','README.md')) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination $target
}
[IO.File]::WriteAllText((Join-Path $target '.gitattributes'), "* -text`n", [Text.UTF8Encoding]::new($false))
$hash = (Get-FileHash -LiteralPath (Join-Path $target 'review-original.zip') -Algorithm SHA256).Hash
[IO.File]::WriteAllText((Join-Path $target 'SHA256.txt'), "$hash  review-original.zip`n", [Text.UTF8Encoding]::new($false))
& py -3 -B (Join-Path $target 'verify_archive.py') (Join-Path $target 'review-original.zip')
if ($LASTEXITCODE -ne 0) { throw 'Copied archive verification failed; no commit.' }
& git -C $worktree add -f -- $relative
if ($LASTEXITCODE -ne 0) { throw 'Archive staging failed.' }
& git -C $worktree commit --only -m 'Preserve native contract body dependencies and exact reproducible compiler' -- $relative
if ($LASTEXITCODE -ne 0) { throw 'Archive commit failed; worktree retained.' }
& git -C $worktree cat-file -e "HEAD:$relative/review-original.zip"
if ($LASTEXITCODE -ne 0) { throw 'Original archive missing from commit.' }
$head = & git -C $worktree rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'Commit inspection failed.' }
Write-Host "BODY_DEPENDENCIES_ARCHIVE_COMMIT_VERIFIED: $head"
if ($Push) {
    & git -C $worktree push origin HEAD:main
    if ($LASTEXITCODE -ne 0) { throw 'Push failed. Accepted evidence and local commit retained; no force push.' }
    $remote = @(& git -C $worktree ls-remote --exit-code origin refs/heads/main)
    if ($LASTEXITCODE -ne 0 -or $remote.Count -ne 1) { throw 'Remote inspection failed.' }
    if (($remote[0] -split '\s+')[0] -ne $head) { throw 'Remote commit differs.' }
    Write-Host "BODY_DEPENDENCIES_ARCHIVE_PUSH_VERIFIED: $head"
}
Write-Host "Archive worktree: $worktree"
Write-Host 'Original checkout, Docker and Mealie were not changed.'
