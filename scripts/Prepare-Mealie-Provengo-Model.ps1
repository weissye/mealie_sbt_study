[CmdletBinding()]
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent),
    [string]$ProvengoPath,
    [switch]$Sample,
    [string]$ReviewZip = (Join-Path $env:USERPROFILE 'Downloads\mealie_provengo_model_review.zip')
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python = Get-StudyPython
$arguments = @($python.Prefix) + @((Join-Path $Root 'src\prepare_provengo_model.py'), '--root', $Root)
$generated = & $python.Exe @arguments
if ($LASTEXITCODE -ne 0) { throw 'Offline model generation failed.' }
$model = ($generated -join "`n") | ConvertFrom-Json
$project = $model.project
$result = [ordered]@{ result = 'M4_OFFLINE_MODEL_READY'; project = $project; expectedSymbolicOrders = $model.expected_order_count
    provengoPath = $null; samplingRequested = [bool]$Sample; sampleFileCreated = $false
    sampleExitCode = $null; sampledCoverageVerified = $false; serverRequestsSent = 0 }
if ($Sample) {
    if (-not $ProvengoPath) {
        $command = Get-Command provengo -ErrorAction SilentlyContinue
        if ($command) { $ProvengoPath = $command.Source }
    }
    if ($ProvengoPath) {
        $result.provengoPath = $ProvengoPath
        $sampleFile = Join-Path $project 'samples.json'
        Write-Host 'Sampling the offline symbolic model. No server requests are sent.'
        $savedPreference = $ErrorActionPreference
        try {
            $ErrorActionPreference = 'Continue'
            $log = @(& $ProvengoPath sample --algorithm full --max-length 16 -o $sampleFile $project 2>&1 | ForEach-Object { $_.ToString() })
            $result.sampleExitCode = $LASTEXITCODE
            $log | Set-Content -LiteralPath (Join-Path $project 'sampling.log') -Encoding UTF8
            $log | ForEach-Object { Write-Host $_ }
            $result.sampleFileCreated = (Test-Path -LiteralPath $sampleFile -PathType Leaf) -and (Get-Item -LiteralPath $sampleFile).Length -gt 0
            if ($result.sampleExitCode -eq 0 -and $result.sampleFileCreated) { $result.result = 'M4_OFFLINE_SAMPLE_FILE_READY_FOR_REVIEW' }
            else { $result.result = 'M4_OFFLINE_SAMPLING_NOT_ACCEPTED' }
        } catch {
            $result.result = 'M4_OFFLINE_SAMPLING_NOT_ACCEPTED'
            $_.Exception.Message | Set-Content -LiteralPath (Join-Path $project 'sampling.log') -Encoding UTF8
        } finally { $ErrorActionPreference = $savedPreference }
    } else { $result.result = 'M4_OFFLINE_MODEL_READY_PROVENGO_NOT_FOUND' }
}
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $project 'readiness.json') -Encoding UTF8
New-Item -ItemType Directory -Path (Split-Path ([IO.Path]::GetFullPath($ReviewZip)) -Parent) -Force | Out-Null
Compress-Archive -Path (Join-Path $project '*') -DestinationPath $ReviewZip -Force
Write-Host $result.result
Write-Host ('Review ZIP: ' + $ReviewZip)
Write-Host 'This is an offline model. Sampling does not execute the modeled HTTP operations.'
