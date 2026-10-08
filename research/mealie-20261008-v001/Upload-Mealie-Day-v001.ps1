param(
 [string]$StudyRoot='C:\work\temp\mealie_sbt_study',
 [string]$GeneratorRoot='C:\work\temp\central-process-binding-20261007-133307-073\payload'
)
$ErrorActionPreference='Stop'
Write-Host 'MEALIE_GIT_UPLOAD v001'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$remote='https://github.com/weissye/mealie_sbt_study.git'
$downloads=Join-Path $env:USERPROFILE 'Downloads'
$stamp=Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$branch='research/mealie-20261008-v001-'+$stamp
$checkout=Join-Path $downloads ('mealie-git-upload-v001-'+$stamp)
function GitRun([string[]]$Arguments){& git @Arguments;if($LASTEXITCODE -ne 0){throw ('Git failed: '+($Arguments -join ' '))}}
if(-not (Test-Path (Join-Path $GeneratorRoot 'generator_v56\__main__.py'))){throw 'Complete generator not found at GeneratorRoot.'}
$previousLfs=$env:GIT_LFS_SKIP_SMUDGE
$env:GIT_LFS_SKIP_SMUDGE='1'
try{GitRun -Arguments @('clone','--single-branch','--branch','main',$remote,$checkout)}finally{$env:GIT_LFS_SKIP_SMUDGE=$previousLfs}
foreach($key in @('user.name','user.email')){
 $value=& git -C $StudyRoot config --get $key
 if($LASTEXITCODE -eq 0 -and $value){GitRun -Arguments @('-C',$checkout,'config',$key,$value)}
}
GitRun -Arguments @('-C',$checkout,'switch','-c',$branch)
$relative='research/mealie-20261008-v001'
$dest=Join-Path $checkout $relative
New-Item -ItemType Directory -Path (Join-Path $dest 'artifacts') -Force | Out-Null
$patterns=@('Mealie_Generator_Provengo_v007*.zip','Mealie_Shared_Consistency_v005*.zip','Mealie_Consistency_v006_SourceBundle*.zip','Mealie_Consistency_v006.zip','review_v006*.zip','regression-v006-*.zip','Mealie_v005_Review_and_Server_Log_v001*.zip','Mealie_Server_Log_v001*.txt','Mealie_Quantity_Consistency_Engineering_and_Research*.docx','Mealie_Research_Collector_v00*.zip','Mealie_Context_Actors_Logical_Interleaving_Delta*.zip','Context_Actors_Run_Repair*.zip')
$matches=New-Object 'System.Collections.Generic.List[object]'
foreach($root in @($downloads,$StudyRoot)){
 if(Test-Path -LiteralPath $root){
  Get-ChildItem -LiteralPath $root -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
   $file=$_
   if(-not $file.FullName.StartsWith($checkout,[StringComparison]::OrdinalIgnoreCase)){
    foreach($pattern in $patterns){if($file.Name -like $pattern){$matches.Add($file);break}}
   }
  }
 }
}
# Keep every distinct byte version; number collisions instead of silently selecting a stale file.
Get-ChildItem "$downloads\mealie-provengo-v007-*\runs\v007-*\review_v007.zip" -ErrorAction SilentlyContinue | ForEach-Object {$matches.Add($_)}
$hashes=@{};$inventory=New-Object 'System.Collections.Generic.List[object]';$i=0
foreach($file in ($matches | Sort-Object FullName -Unique)){
 $hash=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
 if($hashes.ContainsKey($hash)){continue};$hashes[$hash]=$true;$i++
 $name=('{0:D4}-' -f $i)+$file.Name
 $out=Join-Path (Join-Path $dest 'artifacts') $name
 Copy-Item -LiteralPath $file.FullName -Destination $out
 $inventory.Add([pscustomobject]@{source=$file.FullName;file=('artifacts/'+$name);sha256=$hash;bytes=$file.Length})
}
# Preserve successful v005 review even when the upload filename differs.
$reviews=@(Get-ChildItem "$downloads\mealie-shared-v005-*\runs\v005-*\review.zip" -ErrorAction SilentlyContinue)
foreach($file in $reviews){
 $archive=[IO.Compression.ZipFile]::OpenRead($file.FullName)
 try{
  $entry=$archive.GetEntry('result.json')
  if($entry){$reader=New-Object IO.StreamReader($entry.Open());try{$result=$reader.ReadToEnd()|ConvertFrom-Json}finally{$reader.Dispose()}
   if($result.status -eq 'SHARED_CONSISTENCY_PASS'){
    $hash=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
    if(-not $hashes.ContainsKey($hash)){$hashes[$hash]=$true;$i++;$name=('{0:D4}-review_v005-' -f $i)+$file.Directory.Name+'.zip';Copy-Item -LiteralPath $file.FullName -Destination (Join-Path $dest ('artifacts/'+$name));$inventory.Add([pscustomobject]@{source=$file.FullName;file=('artifacts/'+$name);sha256=$hash;bytes=$file.Length})}
   }
  }
 }finally{$archive.Dispose()}
}
$sourceStage=Join-Path $downloads ('mealie-generator-stage-v001-'+$stamp)
New-Item -ItemType Directory -Path (Join-Path $sourceStage 'generator_v56') -Force | Out-Null
Get-ChildItem (Join-Path $GeneratorRoot 'generator_v56') -Recurse -File -Filter '*.py' | ForEach-Object {
 $relativeSource=$_.FullName.Substring($GeneratorRoot.TrimEnd('\').Length).TrimStart('\')
 $target=Join-Path $sourceStage $relativeSource
 New-Item -ItemType Directory -Path (Split-Path $target -Parent) -Force | Out-Null
 Copy-Item -LiteralPath $_.FullName -Destination $target
}
$generatorZip=Join-Path $dest 'generator-source-v001.zip'
[IO.Compression.ZipFile]::CreateFromDirectory($sourceStage,$generatorZip)
Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $dest 'Upload-Mealie-Day-v001.ps1')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Download-Run-Mealie-Home-v001.ps1') -Destination $dest
$missing=@()
foreach($pattern in @('Mealie_Generator_Provengo_v007*.zip','Mealie_Consistency_v006_SourceBundle*.zip','review_v006*.zip','regression-v006-*.zip')){
 if(-not ($matches | Where-Object {$_.Name -like $pattern})){$missing+=$pattern}
}
$summary=[ordered]@{version='v001';repository=$remote;branch=$branch;day='2026-10-08';generator_source=$GeneratorRoot;copied_artifacts=$inventory.Count;missing=$missing;notes=@('Only generator Python source is snapshotted.','Docker data, databases, credentials, products and JARs are not separately collected.','Original archives may contain sensitive material; reviewed for common token/key patterns before commit.','All distinct artifact hashes are preserved. Missing artifacts do not disappear silently.')}
ConvertTo-Json -InputObject $inventory.ToArray() -Depth 6 | Set-Content (Join-Path $dest 'inventory_v001.json') -Encoding UTF8
ConvertTo-Json -InputObject $summary -Depth 6 | Set-Content (Join-Path $dest 'summary_v001.json') -Encoding UTF8
$checksums=@{}
Get-ChildItem $dest -Recurse -File | ForEach-Object {$checksums[$_.FullName.Substring($dest.Length+1).Replace('\','/')]=(Get-FileHash $_.FullName -Algorithm SHA256).Hash}
ConvertTo-Json -InputObject $checksums -Depth 4 | Set-Content (Join-Path $dest 'checksums_v001.json') -Encoding UTF8
# Avoid publishing common bearer/JWT/private-key material. This check is not exhaustive.
function CheckText([string]$Text,[string]$Label){if($Text -match 'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}|Bearer\s+[A-Za-z0-9._-]{80,}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----'){throw ('Potential credential in '+$Label+'. Nothing pushed; inspect the staged collection.')}}
foreach($file in (Get-ChildItem $dest -Recurse -File)){
 if($file.Length -gt 90MB){throw ('Artifact exceeds transfer limit: '+$file.FullName)}
 if($file.Extension -eq '.zip'){
  $archive=[IO.Compression.ZipFile]::OpenRead($file.FullName)
  try{foreach($entry in $archive.Entries){
   if($entry.FullName -match '\.(json|txt|log|py|js|ps1|yml|yaml|md|patch)$' -and $entry.Length -lt 20MB){$reader=New-Object IO.StreamReader($entry.Open());try{CheckText $reader.ReadToEnd() ($file.Name+'/'+$entry.FullName)}finally{$reader.Dispose()}}
  }}finally{$archive.Dispose()}
 }elseif($file.Extension -in @('.json','.txt','.log','.py','.ps1','.md')){CheckText (Get-Content -LiteralPath $file.FullName -Raw) $file.Name}
}
Set-Content (Join-Path $dest '.gitattributes') -Encoding ASCII -Value @('*.zip -filter -diff -merge -text','*.docx -filter -diff -merge -text')
GitRun -Arguments @('-C',$checkout,'add','-f','--',$relative)
GitRun -Arguments @('-C',$checkout,'commit','-m','Save Mealie 2026-10-08 source, v007 and evidence (transfer v001)')
GitRun -Arguments @('-C',$checkout,'push','-u','origin',$branch)
$head=(& git -C $checkout rev-parse HEAD).Trim();if($LASTEXITCODE -ne 0){throw 'Cannot read local commit.'}
$line=& git -C $checkout ls-remote origin ('refs/heads/'+$branch);if($LASTEXITCODE -ne 0){throw 'Remote verification failed.'}
if(-not $line -or ($line -split '\s+')[0] -ne $head){throw 'Remote commit mismatch.'}
Write-Host 'MEALIE_UPLOAD_V001_VERIFIED'
Write-Host "Branch: $branch"
Write-Host "Commit: $head"
Write-Host "Home download command: -Branch '$branch'"
if($missing.Count){Write-Host ('Missing artifacts: '+($missing -join ', '))}
