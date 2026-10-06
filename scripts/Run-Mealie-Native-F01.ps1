param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [string]$Username = 'changeme@example.com',
    [string]$BaseUrl = 'http://127.0.0.1:9925',
    [string]$Jar,
    [switch]$GenerateOnly
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $Root
& py -3 -B (Join-Path $Root 'tools\test_native_f01.py')
if ($LASTEXITCODE -ne 0) { throw 'Offline callback/HTTP fixture verification failed. No live replay started.' }
$argsList = @('-3', '-B', (Join-Path $Root 'tools\run_native_f01.py'), '--root', $Root, '--base-url', $BaseUrl)
if ($Jar) { $argsList += @('--jar', $Jar) }
if ($GenerateOnly) {
    $argsList += '--generate-only'
    & py @argsList
    if ($LASTEXITCODE -ne 0) { throw 'Generation failed. Inspect the printed review directory.' }
    return
}
$secure = Read-Host 'Mealie password (hidden)' -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
$savedUser = $env:MEALIE_ACCEPTANCE_USERNAME
$savedPassword = $env:MEALIE_ACCEPTANCE_PASSWORD
$savedOptions = $env:JAVA_TOOL_OPTIONS
try {
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    $env:MEALIE_ACCEPTANCE_USERNAME = [Uri]::EscapeDataString($Username)
    $env:MEALIE_ACCEPTANCE_PASSWORD = [Uri]::EscapeDataString($plain)
    $env:JAVA_TOOL_OPTIONS = '-Xmx1g'
    Write-Host 'F01: fresh owned food, unit, recipe, list and item; whole then half recipe contribution. Resources retained.'
    & py @argsList
    if ($LASTEXITCODE -ne 0) { throw 'F01 stopped. Preserve the printed review.zip; no automatic retry was performed.' }
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    $plain = $null
    $secure = $null
    $env:MEALIE_ACCEPTANCE_USERNAME = $savedUser
    $env:MEALIE_ACCEPTANCE_PASSWORD = $savedPassword
    $env:JAVA_TOOL_OPTIONS = $savedOptions
}
