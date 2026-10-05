[CmdletBinding()]
param([string]$Root = (Split-Path $PSScriptRoot -Parent), [switch]$Push)
$ErrorActionPreference = 'Stop'
$Root = [IO.Path]::GetFullPath($Root)
$top = git -C $Root rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0 -or [IO.Path]::GetFullPath($top.Trim()) -ne $Root) { throw 'Expected the study repository root.' }
$branch = git -C $Root branch --show-current
if ($LASTEXITCODE -ne 0 -or $branch.Trim() -ne 'main') { throw 'Expected main branch.' }
$paths = @(
    'README-SCOPE-CONTROLS.md',
    'docs/research/20261005/Mealie_Reference_And_Household_Controls.md',
    'generic-generator/profiles/mealie-household-controls-runtime.json',
    'generic-generator/profiles/mealie-household-controls-scope.json',
    'generic-generator/profiles/mealie-reference-controls-runtime.json',
    'generic-generator/profiles/mealie-reference-controls-scope.json',
    'generic-generator/scope_controls_validation.json',
    'generic-generator/tests/scope_controls_http_mock.js',
    'generic-generator/tests/test_scope_controls.py',
    'generic-generator/tools/run_scope_controls.py',
    'scripts/Run-Generic-Scope-Controls.ps1',
    'scripts/Save-Generic-Scope-Controls.ps1'
)
foreach ($path in $paths) {
    if (-not (Test-Path -LiteralPath (Join-Path $Root $path) -PathType Leaf)) { throw "Missing release file: $path" }
}
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python = Get-StudyPython
$savedPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = (Join-Path $Root 'generic-generator') + [IO.Path]::PathSeparator + $savedPythonPath
    foreach ($pattern in @('test_scope_controls.py', 'test_identity_program.py')) {
        & $python.Exe @($python.Prefix) -B -m unittest discover -s (Join-Path $Root 'generic-generator/tests') -p $pattern
        if ($LASTEXITCODE -ne 0) { throw "Configuration regression tests failed: $pattern. Git was not changed." }
    }
} finally { $env:PYTHONPATH = $savedPythonPath }
git -C $Root add -f -- @paths
if ($LASTEXITCODE -ne 0) { throw 'Release staging failed.' }
git -C $Root diff --cached --quiet -- @paths
$difference = $LASTEXITCODE
if ($difference -eq 1) {
    git -C $Root commit --only -m 'Add focused reference and household boundary controls' -- @paths
    if ($LASTEXITCODE -ne 0) { throw 'Release commit failed.' }
} elseif ($difference -ne 0) { throw 'Staged release check failed.' }
$head = git -C $Root rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'Cannot identify release commit.' }
if ($Push) {
    git -C $Root push origin HEAD:refs/heads/main
    if ($LASTEXITCODE -ne 0) { throw 'Git push failed. Local files are preserved.' }
    $remote = git -C $Root ls-remote origin refs/heads/main
    if ($LASTEXITCODE -ne 0 -or -not $remote -or (($remote -split '\s+')[0] -ne $head.Trim())) { throw 'Remote commit verification failed.' }
    Write-Host "SCOPE_CONTROLS_SOURCE_PUSH_VERIFIED: $($head.Trim())"
} else { Write-Host "SCOPE_CONTROLS_SOURCE_COMMITTED_LOCALLY: $($head.Trim())" }
