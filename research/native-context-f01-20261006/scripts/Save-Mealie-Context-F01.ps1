param(
    [Parameter(Mandatory=$true)][string]$Repository,
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [Parameter(Mandatory=$true)][string]$AcceptedProject,
    [switch]$Push
)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath $Root).Path
$Repository = (Resolve-Path -LiteralPath $Repository).Path
& py -3 -B (Join-Path $Root 'tools\archive_context_acceptance.py') `
    --package $Root --repository $Repository --accepted-project $AcceptedProject
if ($LASTEXITCODE -ne 0) { throw 'Archive verification failed. Git was not changed.' }
$relative = 'research/native-context-f01-20261006'
& git -C $Repository add -- $relative
if ($LASTEXITCODE -ne 0) { throw 'Staging failed.' }
& git -C $Repository diff --cached --quiet -- $relative
$code = $LASTEXITCODE
if ($code -eq 1) {
    & git -C $Repository commit --only -m 'Freeze verified native Context baseline and add generated contribution experiment' -- $relative
    if ($LASTEXITCODE -ne 0) { throw 'Commit failed. Archive is retained.' }
} elseif ($code -ne 0) { throw 'Staged change inspection failed.' }
if ($Push) {
    $branch = & git -C $Repository branch --show-current
    if ($LASTEXITCODE -ne 0 -or -not $branch) { throw 'No active branch.' }
    & git -C $Repository push origin "HEAD:refs/heads/$branch"
    if ($LASTEXITCODE -ne 0) { throw 'Push failed. Local commit was preserved. No force push was attempted.' }
    $head = & git -C $Repository rev-parse HEAD
    if ($LASTEXITCODE -ne 0) { throw 'HEAD verification failed.' }
    $remote = @(& git -C $Repository ls-remote --exit-code origin "refs/heads/$branch")
    if ($LASTEXITCODE -ne 0 -or $remote.Count -ne 1 -or ($remote[0] -split '\s+')[0] -ne $head) { throw 'Remote commit verification failed.' }
    Write-Host "CONTEXT_BASELINE_AND_F01_SOURCE_PUSH_VERIFIED: $head"
} else { Write-Host 'CONTEXT_BASELINE_AND_F01_SOURCE_COMMITTED_LOCALLY' }
