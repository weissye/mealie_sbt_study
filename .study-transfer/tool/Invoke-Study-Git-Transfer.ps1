[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidateSet('Export','Import')][string]$Mode,
    [switch]$Push,
    [switch]$Pull,
    [switch]$InstallDependencies
)
$ErrorActionPreference = 'Stop'
if ($Mode -eq 'Export' -and $Pull) { throw 'Pull is only supported for Import.' }
if ($Mode -eq 'Import' -and $Push) { throw 'Push is only supported for Export.' }
$python = Get-Command py -ErrorAction SilentlyContinue
$prefix = @('-3')
if (-not $python) {
    $python = Get-Command python -ErrorAction Stop
    $prefix = @()
}
if ($InstallDependencies) {
    & $python.Source @prefix -m pip install --user -r (Join-Path $PSScriptRoot 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Transfer dependency installation failed.' }
}
& $python.Source @prefix -c 'import docker, cryptography'
if ($LASTEXITCODE -ne 0) { throw 'Run this command once with -InstallDependencies.' }

$active = @(Get-CimInstance Win32_Process | Where-Object {
    $_.Name -match '^java(w)?\.exe$' -and $_.CommandLine -match 'provengo'
})
if ($active.Count -gt 0) { throw 'Finish the active Provengo execution or sampling before transferring study state.' }

$password = Read-Host 'Transfer encryption password (12 or more characters; keep it for both computers)' -AsSecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
$previous = $env:STUDY_TRANSFER_PASSWORD
try {
    $env:STUDY_TRANSFER_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    $arguments = @($prefix) + @((Join-Path $PSScriptRoot 'study_transfer.py'), $Mode.ToLowerInvariant())
    if ($Push) { $arguments += '--push' }
    if ($Pull) { $arguments += '--pull' }
    & $python.Source @arguments
    if ($LASTEXITCODE -ne 0) { throw 'Study transfer was not accepted. Keep the original files and inspect the last message before retrying.' }
} finally {
    $env:STUDY_TRANSFER_PASSWORD = $previous
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    $password.Dispose()
}
