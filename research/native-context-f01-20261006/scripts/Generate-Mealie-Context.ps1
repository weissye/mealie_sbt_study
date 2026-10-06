param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [string]$BaseUrl = 'http://127.0.0.1:9925',
    [int]$Instances = 1,
    [int]$Seed = (Get-Random -Minimum 1 -Maximum 1000000000)
)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath $Root).Path
$contract = Join-Path $Root 'model\mealie-openapi.v3.28.0.json'
$expected = '90e19aa713ab4ba15352627aca7dc37290f868b213eb65a3e1564f3b7a7ff292'
if ((Get-FileHash -LiteralPath $contract -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) {
    throw 'Pinned contract bytes differ. No files were generated.'
}
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$project = Join-Path $Root "runs\context-$stamp-$Seed"
$output = Join-Path $project 'spec\js'
$arguments = @(
    '-3', '-B', '-m', 'generator_v56', 'context-generate',
    '--openapi', $contract, '--output', $output, '--name', 'mealie',
    '--base-url', $BaseUrl, '--instances-per-entity', "$Instances", '--seed', "$Seed",
    '--resource', '/api/foods', '--resource', '/api/units', '--resource', '/api/recipes',
    '--resource', '/api/households/shopping/lists', '--resource', '/api/households/shopping/items'
)
Push-Location $Root
try {
    & py @arguments
    if ($LASTEXITCODE -ne 0) { throw 'Context generation failed.' }
} finally {
    Pop-Location
}
Write-Host 'CONTEXT_GENERATED_NOT_EXECUTED'
Write-Host "Stories: $(Join-Path $output 'stories.mealie.js')"
Write-Host "Interfaces: $(Join-Path $output 'interfaces.mealie.js')"
Write-Host "DAL: $(Join-Path $output 'dal.js')"
Write-Host "Provenance: $(Join-Path $output 'generation_report.json')"
Write-Host 'No HTTP requests, deletion, installation into the existing generator, Git commit or push were performed.'
