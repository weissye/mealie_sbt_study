[CmdletBinding()]
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent),
    [ValidatePattern('^http://127\.0\.0\.1:\d+/?$')][string]$BaseUrl = 'http://127.0.0.1:9925'
)
$ErrorActionPreference = 'Stop'
$BaseUrl = $BaseUrl.TrimEnd('/')
New-Item -ItemType Directory -Path (Join-Path $Root 'model'), (Join-Path $Root 'runs') -Force | Out-Null
$stamp = [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss-fff')
$about = Invoke-RestMethod -Uri ($BaseUrl + '/api/app/about') -TimeoutSec 10
$temporary = Join-Path $Root ('model\mealie-openapi.' + $stamp + '.tmp')
$contract = Join-Path $Root ('model\mealie-openapi.local-' + $stamp + '.json')
Invoke-WebRequest -Uri ($BaseUrl + '/openapi.json') -OutFile $temporary -UseBasicParsing -TimeoutSec 30
$spec = Get-Content -LiteralPath $temporary -Raw | ConvertFrom-Json
if (-not $spec.openapi -or -not $spec.paths -or -not $spec.components.schemas) { throw 'The downloaded file is not a supported OpenAPI contract.' }
Move-Item -LiteralPath $temporary -Destination $contract
$hash = (Get-FileHash -LiteralPath $contract -Algorithm SHA256).Hash.ToLowerInvariant()
$outputDirectory = Join-Path $Root ('maps\local-' + $stamp)
& (Join-Path $PSScriptRoot 'Compile-Mealie-Maps.ps1') -Root $Root -Contract $contract -OutputDirectory $outputDirectory
$acceptance = [ordered]@{
    result = 'M1_SERVER_CONTRACT_READ_PASS'; baseUrl = $BaseUrl; appInfo = $about
    contract = $contract; sha256 = $hash; maps = $outputDirectory
    authenticatedRequestsTested = $false; fixturesValidated = $false
    resetReplayValidated = $false; readyForLivePilot = $false
}
$acceptance | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath (Join-Path $Root ('runs\acceptance-' + $stamp + '.json')) -Encoding UTF8
Write-Host 'MEALIE_M1_SERVER_CONTRACT_READ_PASS'
Write-Host ('Local contract: ' + $contract)
Write-Host 'This confirms server reachability and contract access only.'
