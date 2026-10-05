[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Username,
    [string]$Root = (Split-Path $PSScriptRoot -Parent),
    [string]$BaseUrl = 'http://127.0.0.1:9925',
    [int]$Seed = (Get-Random -Minimum 1000 -Maximum 1000000)
)
$ErrorActionPreference = 'Stop'
$Root = [IO.Path]::GetFullPath($Root)
$freeRAMMiB = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1KB
if ($freeRAMMiB -lt 1024) { throw 'At least 1024 MiB free RAM is required.' }
$drive = [IO.Path]::GetPathRoot($Root).Substring(0,1)
if ((Get-PSDrive -Name $drive).Free -lt 512MB) { throw 'At least 512 MiB free disk space is required.' }
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python = Get-StudyPython
$savedUsername = $env:SBT_REL_USERNAME
$savedPassword = $env:SBT_REL_PASSWORD
$savedOptions = $env:JAVA_TOOL_OPTIONS
$secret = $null
$pointer = [IntPtr]::Zero
try {
    $env:JAVA_TOOL_OPTIONS = ("$savedOptions -Xmx512m").Trim()
    $secret = Read-Host 'Provisioning administrator password (hidden)' -AsSecureString
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
    $env:SBT_REL_USERNAME = $Username
    $env:SBT_REL_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    Write-Host 'The administrator creates isolated fixtures. Resource probes use two regular users.'
    & $python.Exe @($python.Prefix) -B (Join-Path $Root 'generic-generator\tools\run_identity_campaign.py') `
        --root $Root --base-url $BaseUrl --seed $Seed
    if ($LASTEXITCODE -ne 0) { throw 'Multi-identity campaign stopped. Preserve the printed review ZIP.' }
} finally {
    $env:SBT_REL_USERNAME = $savedUsername
    $env:SBT_REL_PASSWORD = $savedPassword
    $env:JAVA_TOOL_OPTIONS = $savedOptions
    if ($pointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
    if ($null -ne $secret) { $secret.Dispose() }
}
