param([string]$HomeRoot='D:\Yeshayahu\Temp',[string]$Branch,[string]$ProvengoJar,[switch]$Run)
$ErrorActionPreference='Stop'
Write-Host 'MEALIE_HOME_TRANSFER v001'
$remote='https://github.com/weissye/mealie_sbt_study.git'
if(-not $Branch){
 $lines=& git ls-remote --heads $remote 'refs/heads/research/mealie-20261008-v001-*'
 if($LASTEXITCODE -ne 0){throw 'Cannot list research branches.'}
 $Branch=@($lines | ForEach-Object {($_ -split '\s+')[1] -replace '^refs/heads/',''} | Sort-Object -Descending)[0]
 if(-not $Branch){throw 'No uploaded Mealie day branch found.'}
}
$destination=Join-Path $HomeRoot ('mealie-day-v001-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
New-Item -ItemType Directory -Path $HomeRoot -Force | Out-Null
$previousLfs=$env:GIT_LFS_SKIP_SMUDGE
$env:GIT_LFS_SKIP_SMUDGE='1'
try{& git clone --single-branch --branch $Branch $remote $destination;$cloneExit=$LASTEXITCODE}finally{$env:GIT_LFS_SKIP_SMUDGE=$previousLfs}
if($cloneExit -ne 0){throw 'Clone failed.'}
$head=(& git -C $destination rev-parse HEAD).Trim()
$remoteHead=& git -C $destination ls-remote origin ('refs/heads/'+$Branch)
if($LASTEXITCODE -ne 0 -or ($remoteHead -split '\s+')[0] -ne $head){throw 'Downloaded commit not verified.'}
$day=Join-Path $destination 'research\mealie-20261008-v001'
$hashes=Get-Content (Join-Path $day 'checksums_v001.json') -Raw | ConvertFrom-Json
foreach($entry in $hashes.PSObject.Properties){if((Get-FileHash -LiteralPath (Join-Path $day $entry.Name) -Algorithm SHA256).Hash -ne $entry.Value){throw ('Checksum mismatch: '+$entry.Name)}}
$generator=Join-Path $destination 'generator-current'
Expand-Archive -LiteralPath (Join-Path $day 'generator-source-v001.zip') -DestinationPath $generator
$packages=@(Get-ChildItem (Join-Path $day 'artifacts') -Filter '*Mealie_Generator_Provengo_v007*.zip')
if($packages.Count -ne 1){throw 'Expected exactly one v007 package; inspect inventory for distinct copies.'}
$package=Join-Path $destination 'v007'
Expand-Archive -LiteralPath $packages[0].FullName -DestinationPath $package
Get-ChildItem $package -Recurse -File | Unblock-File
Write-Host "HOME_DOWNLOAD_V001_VERIFIED: $head"
Write-Host "Generator: $generator"
Write-Host "Evidence and packages: $day"
if($Run){
 if($ProvengoJar){& (Join-Path $package 'Run-Generator-Provengo-v007.ps1') -GeneratorRoot $generator -ProvengoJar $ProvengoJar}
 else{& (Join-Path $package 'Run-Generator-Provengo-v007.ps1') -GeneratorRoot $generator}
}else{Write-Host ('Run: & "'+(Join-Path $package 'Run-Generator-Provengo-v007.ps1')+'" -GeneratorRoot "'+$generator+'"')}
