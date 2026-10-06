param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [string]$BaseUrl = 'http://127.0.0.1:9925',
    [string]$Username = 'changeme@example.com'
)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath $Root).Path
& (Join-Path $Root 'scripts\Test-Mealie-Context-Offline.ps1') -Root $Root
$Seed = Get-Random -Minimum 1 -Maximum 1000000000
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$project = Join-Path $Root "runs\live-context-$stamp-$Seed"
$output = Join-Path $project 'spec\js'
$contract = Join-Path $Root 'model\mealie-openapi.v3.28.0.json'
if ((Get-FileHash -LiteralPath $contract -Algorithm SHA256).Hash.ToLowerInvariant() -ne '90e19aa713ab4ba15352627aca7dc37290f868b213eb65a3e1564f3b7a7ff292') {
    throw 'Pinned contract differs. No replay was started.'
}
$arguments = @(
    '-3', '-B', '-m', 'generator_v56', 'context-generate',
    '--openapi', $contract, '--output', $output, '--name', 'mealie',
    '--base-url', $BaseUrl, '--instances-per-entity', '1', '--seed', "$Seed",
    '--resource', '/api/foods', '--resource', '/api/units', '--resource', '/api/recipes',
    '--resource', '/api/households/shopping/lists', '--resource', '/api/households/shopping/items'
)
Push-Location $Root
try {
    & py @arguments
    if ($LASTEXITCODE -ne 0) { throw 'Generation failed. Replay was not started.' }
} finally { Pop-Location }
Write-Host "Project: $project"
Write-Host "Stories: $(Join-Path $output 'stories.mealie.js')"
Write-Host "Interfaces: $(Join-Path $output 'interfaces.mealie.js')"
Write-Host 'Native Context acceptance: fresh food, unit, recipe, list and item; two linked ingredients; updates and independent readbacks.'
Write-Host 'All resources are retained. No automatic retry, deletion or reset.'
$secure = Read-Host 'Mealie password (hidden)' -AsSecureString
$pointer = [IntPtr]::Zero
$previousUsername = [Environment]::GetEnvironmentVariable('SBT_USERNAME', 'Process')
$previousPassword = [Environment]::GetEnvironmentVariable('SBT_PASSWORD', 'Process')
$previousPreference = $ErrorActionPreference
try {
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    [Environment]::SetEnvironmentVariable('SBT_USERNAME', $Username, 'Process')
    [Environment]::SetEnvironmentVariable('SBT_PASSWORD', [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer), 'Process')
    $ErrorActionPreference = 'Continue'
    & provengo run $project 2>&1 | Tee-Object -FilePath (Join-Path $project 'native-run.log')
    $exitCode = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $previousPreference
    [Environment]::SetEnvironmentVariable('SBT_USERNAME', $previousUsername, 'Process')
    [Environment]::SetEnvironmentVariable('SBT_PASSWORD', $previousPassword, 'Process')
    if ($pointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
    $secure = $null
}
Write-Host "PROVENGO_EXIT_CODE: $exitCode"
Write-Host "Evidence project: $project"
if ($exitCode -ne 0) { throw 'Native run stopped. Preserve this project; no automatic retry was performed.' }
Write-Host 'NATIVE_RUN_EXIT_ZERO. Review completion and independent readbacks before classifying acceptance.'
