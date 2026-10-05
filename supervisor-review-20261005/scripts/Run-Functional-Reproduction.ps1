param(
 [ValidateSet('F01-addition','F02-food-removal','F02-unit-removal','F03-copy-reference')][string]$Case='F01-addition',
 [Parameter(Mandatory=$true)][string]$Username,
 [string]$Root=(Split-Path -Parent $PSScriptRoot)
)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python=Get-StudyPython
# Dedicated local fixture: do not direct this wrapper at the original study service.
$response=Invoke-WebRequest -Uri 'http://127.0.0.1:9928/openapi.json' -UseBasicParsing -TimeoutSec 15
$contract=$response.Content|ConvertFrom-Json
if($contract.info.version -ne 'v3.28.0'){throw 'The dedicated fixture must run Mealie v3.28.0.'}
$project=& (Join-Path $PSScriptRoot 'Prepare-Reproduction.ps1') -Case $Case -Root $Root
$tool=Join-Path $Root 'source/generic-generator/tools/relationship_execution.py'
$savedOptions=$env:JAVA_TOOL_OPTIONS
$savedUsername=$env:SBT_REL_USERNAME
$savedPassword=$env:SBT_REL_PASSWORD
$password=$null;$pointer=[IntPtr]::Zero
try{
 $env:JAVA_TOOL_OPTIONS='-Xmx1g'
 & $python.Exe @($python.Prefix) -B $tool sample --project $project --size 1 --review-zip (Join-Path $project 'sampling-review.zip')
 if($LASTEXITCODE -ne 0){throw 'Sampling audit failed. Live replay was not started.'}
 $password=Read-Host 'Dedicated fixture password (hidden)' -AsSecureString
 $pointer=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
 $env:SBT_REL_USERNAME=$Username
 $env:SBT_REL_PASSWORD=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
 & $python.Exe @($python.Prefix) -B $tool run --project $project --sample-id 1 --review-zip (Join-Path $project 'live-review.zip')
 $nativeCode=$LASTEXITCODE
 Write-Host "Native wrapper exit code: $nativeCode"
 Write-Host "Review: $project"
 Write-Host 'A nonzero exit code alone does not confirm a defect. Compare the recorded callback mismatch and fresh response bodies with the finding invariant.'
 if($nativeCode -ne 0){throw "Replay stopped. Inspect $project/execution-review/run-acceptance.json and run-output.txt. Authentication and infrastructure failures are not findings."}
}finally{
 $env:JAVA_TOOL_OPTIONS=$savedOptions;$env:SBT_REL_USERNAME=$savedUsername;$env:SBT_REL_PASSWORD=$savedPassword
 if($pointer -ne [IntPtr]::Zero){[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)}
 if($password){$password.Dispose()}
}
