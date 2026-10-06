param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [string]$Username = 'changeme@example.com',
    [string]$BaseUrl = 'http://127.0.0.1:9925',
    [string]$Jar
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $Root
$policy = Get-Content -LiteralPath (Join-Path $Root 'profiles\mealie-native-merge-policy.json') -Raw | ConvertFrom-Json
if ($policy.note_comparison -ne 'unordered_multiset') { throw 'Install the note repair before replay. No live replay was started.' }
# Use named parameters for the existing wrapper, preserving explicit merge-only scope.
if ($Jar) {
    & (Join-Path $Root 'scripts\Test-Mealie-Native-Distinct-Merge.ps1') -Root $Root -Username $Username -BaseUrl $BaseUrl -Scenario Merge -Jar $Jar
} else {
    & (Join-Path $Root 'scripts\Test-Mealie-Native-Distinct-Merge.ps1') -Root $Root -Username $Username -BaseUrl $BaseUrl -Scenario Merge
}
