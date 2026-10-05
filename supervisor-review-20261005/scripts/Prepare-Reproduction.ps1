param(
 [ValidateSet('F01-addition','F02-food-removal','F02-unit-removal','F03-copy-reference','F04-recorded','F05-recorded')][string]$Case='F01-addition',
 [string]$Root=(Split-Path -Parent $PSScriptRoot)
)
$ErrorActionPreference='Stop'
$destination=Join-Path $Root ('runs/'+$Case+'-'+(Get-Date -Format 'yyyyMMdd-HHmmss')+'-'+[guid]::NewGuid().ToString('N').Substring(0,8))
$js=Join-Path $destination 'spec/js'
New-Item -ItemType Directory -Path $js -Force|Out-Null
$config=Join-Path $destination 'config'
New-Item -ItemType Directory -Path $config -Force|Out-Null
[IO.File]::WriteAllText((Join-Path $config 'provengo.yml'),"version: 2`n",[Text.UTF8Encoding]::new($false))
Copy-Item -LiteralPath (Join-Path $Root 'reproductions/interfaces.shared.js') -Destination (Join-Path $js 'interfaces.shared.js')
Copy-Item -LiteralPath (Join-Path $Root "reproductions/$Case/stories.js") -Destination (Join-Path $js 'stories.js')
Get-ChildItem -LiteralPath (Join-Path $Root "reproductions/$Case") -Filter '*.json' -File | Copy-Item -Destination $destination
Write-Output $destination
