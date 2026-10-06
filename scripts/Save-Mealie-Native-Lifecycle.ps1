param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [switch]$Push
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $Root
& py -3 -B (Join-Path $Root 'tools\verify_mealie_interleaving_evidence.py')
if ($LASTEXITCODE -ne 0) { throw 'Evidence verification failed. Git was not changed.' }
$release = Get-Content -LiteralPath (Join-Path $Root 'validation\mealie-native-lifecycle-source-paths.json') -Raw | ConvertFrom-Json
$paths = @($release.paths | ForEach-Object { [string]$_ })
if ($paths.Count -lt 1) { throw 'Release paths missing.' }
foreach ($path in $paths) {
    if (-not (Test-Path -LiteralPath (Join-Path $Root $path))) { throw "Missing release path: $path" }
}
git rev-parse --is-inside-work-tree | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Study root is not a Git working tree.' }
git add -f -- @paths
if ($LASTEXITCODE -ne 0) { throw 'Git staging failed.' }
git diff --cached --quiet -- @paths
$diffCode = $LASTEXITCODE
if ($diffCode -eq 1) {
    git commit --only -m 'Preserve native interleaving acceptance and add verified child deletion lifecycle' -- @paths
    if ($LASTEXITCODE -ne 0) { throw 'Commit failed. Push was not started.' }
} elseif ($diffCode -ne 0) { throw 'Staged release check failed.' }
if ($Push) {
    $branch = (git branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $branch) { throw 'Named branch required for push.' }
    git push origin HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Push failed. Local commit was preserved.' }
    $head = (git rev-parse HEAD).Trim()
    $remote = @(git ls-remote --exit-code origin "refs/heads/$branch")
    if ($LASTEXITCODE -ne 0 -or $remote.Count -ne 1) { throw 'Remote verification failed.' }
    if (($remote[0] -split '\s+')[0] -ne $head) { throw 'Remote branch does not match local HEAD.' }
    Write-Host "NATIVE_LIFECYCLE_SOURCE_AND_EVIDENCE_PUSH_VERIFIED: $head"
} else {
    Write-Host 'NATIVE_LIFECYCLE_SOURCE_AND_EVIDENCE_COMMITTED. No push was performed.'
}
