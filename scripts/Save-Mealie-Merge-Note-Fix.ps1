param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [switch]$Push
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $Root
& py -3 -B (Join-Path $Root 'tools\verify_mealie_merge_note_patch.py')
if ($LASTEXITCODE -ne 0) { throw 'Repair package integrity check failed. Installed renderer and Git were not changed.' }
& py -3 -B (Join-Path $Root 'tools\verify_mealie_merge_note_original.py')
if ($LASTEXITCODE -ne 0) { throw 'Original evidence check failed. Installed renderer and Git were not changed.' }
& py -3 -B (Join-Path $Root 'tools\apply_mealie_merge_note_fix.py') --root $Root
if ($LASTEXITCODE -ne 0) { throw 'Renderer compatibility check failed. Git was not changed.' }
& py -3 -B (Join-Path $Root 'tools\test_mealie_merge_note_fix.py')
if ($LASTEXITCODE -ne 0) { throw 'Repair regression failed. Git was not changed. Original source backup is retained under runs.' }
& py -3 -B (Join-Path $Root 'tools\test_mealie_distinct_merge_renderer.py')
if ($LASTEXITCODE -ne 0) { throw 'Installed renderer verification failed. Git was not changed.' }
& py -3 -B (Join-Path $Root 'tools\verify_mealie_distinct_merge_release.py')
if ($LASTEXITCODE -ne 0) { throw 'Installed release integrity check failed. Git was not changed.' }
$release = Get-Content -LiteralPath (Join-Path $Root 'validation\mealie-merge-note-fix-paths.json') -Raw | ConvertFrom-Json
$paths = @($release.paths | ForEach-Object { [string]$_ })
if ($paths.Count -lt 1) { throw 'Release paths missing.' }
foreach ($path in $paths) {
    if (-not (Test-Path -LiteralPath (Join-Path $Root $path))) { throw "Missing release path: $path" }
}
git rev-parse --is-inside-work-tree | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Root is not a Git working tree.' }
git add -f -- @paths
if ($LASTEXITCODE -ne 0) { throw 'Git staging failed.' }
git diff --cached --quiet -- @paths
$diffCode = $LASTEXITCODE
if ($diffCode -eq 1) {
    git commit --only -m 'Preserve merge note-order false positive and correct native note multiplicity checks' -- @paths
    if ($LASTEXITCODE -ne 0) { throw 'Commit failed. Push was not started.' }
} elseif ($diffCode -ne 0) { throw 'Staged release check failed.' }
if ($Push) {
    $branch = (git branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $branch) { throw 'Named branch required for push.' }
    git push origin HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Push failed. Local commit was preserved.' }
    $head = (git rev-parse HEAD).Trim()
    $remote = @(git ls-remote --exit-code origin "refs/heads/$branch")
    if ($LASTEXITCODE -ne 0 -or $remote.Count -ne 1 -or ($remote[0] -split '\s+')[0] -ne $head) { throw 'Remote verification failed.' }
    Write-Host "MERGE_NOTE_FIX_AND_ORIGINAL_EVIDENCE_PUSH_VERIFIED: $head"
} else { Write-Host 'MERGE_NOTE_FIX_AND_ORIGINAL_EVIDENCE_COMMITTED. No push was performed.' }
