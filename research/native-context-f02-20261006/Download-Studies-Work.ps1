param([string]$Parent = 'C:\work\temp')
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$destination = Join-Path $Parent "study-sync-$stamp"
New-Item -ItemType Directory -Path $destination | Out-Null
$previousLfs = $env:GIT_LFS_SKIP_SMUDGE
$failures = @()
try {
    $env:GIT_LFS_SKIP_SMUDGE = '1'
    foreach ($name in @('mealie_sbt_study','vikunja_tse_study','paperless_sbt_study')) {
        $target = Join-Path $destination $name
        & git clone --branch main --single-branch "https://github.com/weissye/$name.git" $target
        if ($LASTEXITCODE -ne 0) { $failures += $name; continue }
        $local = & git -C $target rev-parse HEAD
        if ($LASTEXITCODE -ne 0) { throw "Local verification failed: $name" }
        $remote = @(& git -C $target ls-remote --exit-code origin refs/heads/main)
        if ($LASTEXITCODE -ne 0 -or $remote.Count -ne 1 -or ($remote[0] -split '\s+')[0] -ne $local) { throw "Remote HEAD differs: $name" }
        Write-Host "SOURCE_DOWNLOAD_VERIFIED: $name $local"
    }
} finally { $env:GIT_LFS_SKIP_SMUDGE = $previousLfs }
Write-Host "Projects: $destination"
if ($failures.Count -gt 0) { throw "Failed projects: $($failures -join ', ')" }
$checkpoint = Join-Path $destination 'mealie_sbt_study\research\native-context-f02-20261006'
$archive = Join-Path $checkpoint 'package.zip'
if (-not (Test-Path -LiteralPath $archive -PathType Leaf)) { throw 'F02 package is absent from Git. Run Save-Tomorrow.ps1 at home first.' }
$manifest = Get-Content -Raw -LiteralPath (Join-Path $checkpoint 'checksums.json') | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $archive).Hash.ToLowerInvariant() -ne $manifest.'package.zip') { throw 'F02 package checksum differs.' }
$package = Join-Path $destination 'mealie-context-f02'
Expand-Archive -LiteralPath $archive -DestinationPath $package
Write-Host "F02_PACKAGE_READY: $package"
Write-Host 'Large LFS archives remain pointers. Existing projects and Docker data were not changed.'
Write-Host "Run food: & '$package\scripts\Run-Mealie-Context-F02.ps1' -Root '$package' -Variant food -Username 'changeme@example.com'"
