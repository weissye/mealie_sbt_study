param([string]$Root = (Split-Path -Parent $PSScriptRoot), [switch]$Push)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $Root
& py -3 -B (Join-Path $Root 'tools\verify_native_f01_release.py') $Root
if ($LASTEXITCODE -ne 0) { throw 'Release verification failed. Git was not changed.' }
& py -3 -B (Join-Path $Root 'tools\test_native_f01.py')
if ($LASTEXITCODE -ne 0) { throw 'Regression failed. Git was not changed.' }
$manifest = Get-Content -LiteralPath (Join-Path $Root 'validation\native-f01-release.json') -Raw | ConvertFrom-Json
$paths = @($manifest.files | ForEach-Object { $_.path }) + @('validation/native-f01-release.json')
& git add -- @paths
if ($LASTEXITCODE -ne 0) { throw 'Staging failed.' }
& git diff --cached --quiet -- @paths
$diffCode = $LASTEXITCODE
if ($diffCode -eq 1) {
    & git commit --only -m 'Add newly compiled native lifecycle F01 quantity reproduction model' -- @paths
    if ($LASTEXITCODE -ne 0) { throw 'Commit failed.' }
} elseif ($diffCode -ne 0) { throw 'Staged change inspection failed.' }
if ($Push) {
    & git push origin HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Push failed. Local commit retained.' }
    $head = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Local HEAD inspection failed.' }
    $branch = (& git branch --show-current).Trim()
    $remote = @(& git ls-remote origin "refs/heads/$branch")
    if ($LASTEXITCODE -ne 0 -or $remote.Count -ne 1 -or ($remote[0] -split '\s+')[0] -ne $head) { throw 'Remote verification failed.' }
    Write-Host "NATIVE_F01_SOURCE_PUSH_VERIFIED: $head"
}
