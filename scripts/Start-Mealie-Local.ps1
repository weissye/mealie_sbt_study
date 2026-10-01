[CmdletBinding()]
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent),
    [ValidateRange(1024,65535)][int]$Port = 9925,
    [ValidatePattern('^v\d+\.\d+\.\d+$')][string]$Version = 'v3.28.0'
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Resolve-Docker.ps1')
$dockerPrefix = @(Wait-StudyDocker)
$composeCheck = Invoke-StudyDocker -Arguments ($dockerPrefix + @('compose', 'version'))
if ($composeCheck.ExitCode -ne 0 -or $composeCheck.Stdout -notmatch 'Docker Compose version v?2\.') { throw 'Docker Compose v2 is required.' }
Write-Host $composeCheck.Stdout.Trim()
New-Item -ItemType Directory -Path (Join-Path $Root 'data'), (Join-Path $Root 'runs') -Force | Out-Null
$compose = Join-Path $Root 'compose.yaml'
$image = 'ghcr.io/mealie-recipes/mealie:' + $Version
$config = @"
services:
  mealie:
    image: $image
    restart: unless-stopped
    ports:
      - "127.0.0.1:${Port}:9000"
    mem_limit: 1000m
    volumes:
      - ./data:/app/data
    environment:
      ALLOW_SIGNUP: "false"
      PUID: "1000"
      PGID: "1000"
      TZ: Asia/Jerusalem
      BASE_URL: http://127.0.0.1:$Port
"@
if (Test-Path $compose) {
    $old = Get-Content -LiteralPath $compose -Raw
    if ($old.Trim() -ne $config.Trim()) {
        throw 'Existing compose configuration differs. This script will not change the server version, port or existing data automatically.'
    }
} else { [IO.File]::WriteAllText($compose, $config, (New-Object Text.UTF8Encoding($false))) }
Write-Host ('Starting isolated Mealie server using ' + $image + '. Image download may take several minutes.')
$startup = Invoke-StudyDocker -Arguments ($dockerPrefix + @('compose', '-p', 'mealie-sbt-study', '-f', $compose, 'up', '-d')) -TimeoutSeconds 900
if ($startup.Stdout) { Write-Host $startup.Stdout }
if ($startup.Stderr) { Write-Host $startup.Stderr }
if ($startup.ExitCode -ne 0) { throw 'Mealie startup failed. Existing data was not deleted.' }
$baseUrl = 'http://127.0.0.1:' + $Port
$ready = $false
for ($attempt = 0; $attempt -lt 60; $attempt++) {
    try {
        $about = Invoke-RestMethod -Uri ($baseUrl + '/api/app/about') -TimeoutSec 3
        $ready = $true; break
    } catch { Start-Sleep -Seconds 2 }
}
if (-not $ready) { throw 'The local server did not become ready. Inspect docker compose logs for this project.' }
$digestResult = Invoke-StudyDocker -Arguments ($dockerPrefix + @('image', 'inspect', $image, '--format', '{{json .RepoDigests}}'))
if ($digestResult.ExitCode -ne 0) { throw 'Could not record the image digest.' }
$digest = $digestResult.Stdout
$record = [ordered]@{
    image = $image; imageDigests = ($digest | ConvertFrom-Json); baseUrl = $baseUrl
    appInfo = $about; timestampUtc = [DateTime]::UtcNow.ToString('o')
    contractSource = 'local server'; dataDeleted = $false; dockerContext = $dockerPrefix[1]
}
$record | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath (Join-Path $Root 'runs\server-manifest.json') -Encoding UTF8
& (Join-Path $PSScriptRoot 'Accept-Mealie-Local.ps1') -Root $Root -BaseUrl $baseUrl
Write-Host 'MEALIE_LOCAL_SERVER_READY'
Write-Host ('Local URL: ' + $baseUrl)
Write-Host 'Authentication, fixture bootstrap and reset/replay acceptance are still pending.'
