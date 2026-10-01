[CmdletBinding()]
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent),
    [string]$Destination = (Join-Path $env:USERPROFILE 'Downloads\mealie_local_contract_review.zip')
)
$ErrorActionPreference = 'Stop'
$acceptanceFile = Get-ChildItem -LiteralPath (Join-Path $Root 'runs') -Filter 'acceptance-*.json' -File |
    Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
if (-not $acceptanceFile) { throw 'No local contract acceptance report was found.' }
$acceptance = Get-Content -LiteralPath $acceptanceFile.FullName -Raw | ConvertFrom-Json
if ($acceptance.result -ne 'M1_SERVER_CONTRACT_READ_PASS') { throw 'The latest report is not a server contract read acceptance.' }
$rootPath = [IO.Path]::GetFullPath($Root).TrimEnd('\') + '\'
foreach ($path in @($acceptance.contract, $acceptance.maps)) {
    if (-not [IO.Path]::GetFullPath($path).StartsWith($rootPath, [StringComparison]::OrdinalIgnoreCase)) { throw 'An acceptance path is outside the project.' }
}
if ((Get-FileHash -LiteralPath $acceptance.contract -Algorithm SHA256).Hash.ToLowerInvariant() -ne $acceptance.sha256) { throw 'The preserved local contract changed after acceptance.' }
& (Join-Path $PSScriptRoot 'Compile-Mealie-Maps.ps1') -Root $Root -Contract $acceptance.contract -OutputDirectory $acceptance.maps
$stage = Join-Path $Root ('runs\review-package-' + [guid]::NewGuid().ToString('N'))
foreach ($directory in @('model', 'maps', 'profiles', 'runs')) { New-Item -ItemType Directory -Path (Join-Path $stage $directory) -Force | Out-Null }
Copy-Item -LiteralPath $acceptance.contract -Destination (Join-Path $stage 'model\mealie-openapi.local.json')
Copy-Item -LiteralPath $acceptanceFile.FullName -Destination (Join-Path $stage 'runs\acceptance.json')
Copy-Item -LiteralPath (Join-Path $Root 'runs\server-manifest.json') -Destination (Join-Path $stage 'runs\server-manifest.json')
Copy-Item -LiteralPath (Join-Path $Root 'profiles\mealie.json') -Destination (Join-Path $stage 'profiles\mealie.json')
foreach ($name in @('01_data_map.json', '02_operation_map.json', '03_relationship_map.json', 'resource_catalog.json', 'cycle_report.json', 'manifest.json')) {
    Copy-Item -LiteralPath (Join-Path $acceptance.maps $name) -Destination (Join-Path $stage ('maps\' + $name))
}
New-Item -ItemType Directory -Path (Split-Path ([IO.Path]::GetFullPath($Destination)) -Parent) -Force | Out-Null
Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $Destination -Force
Write-Host 'MEALIE_LOCAL_REVIEW_PACKAGE_READY'
Write-Host ('Review ZIP: ' + $Destination)
Write-Host 'Included: contract, static maps, profile, public server metadata and acceptance report. Database and account credentials were not collected.'
