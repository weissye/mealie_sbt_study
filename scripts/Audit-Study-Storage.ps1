[CmdletBinding()]
param(
    [string]$ScanRoot = 'C:\work\temp',
    [string]$OutputDirectory = (Join-Path (Split-Path $PSScriptRoot -Parent) 'storage-audit'),
    [ValidateRange(1,3650)][int]$OlderThanDays = 14,
    [switch]$SkipDocker
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $ScanRoot -PathType Container)) { throw 'The scan root does not exist.' }
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$scan = (Resolve-Path -LiteralPath $ScanRoot).Path.TrimEnd('\')
$output = [IO.Path]::GetFullPath($OutputDirectory).TrimEnd('\')
$cutoff = [DateTime]::UtcNow.AddDays(-$OlderThanDays)
$stamp = [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')
$totals = @{}; $candidates = New-Object System.Collections.Generic.List[object]
$errors = @(); $totalBytes = [long]0; $count = [long]0
Get-ChildItem -LiteralPath $scan -Recurse -File -ErrorAction SilentlyContinue -ErrorVariable +errors | ForEach-Object {
    $file = $_
    if (-not ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -and -not $file.FullName.StartsWith($output + '\', [StringComparison]::OrdinalIgnoreCase)) {
        $relative = $file.FullName.Substring($scan.Length).TrimStart('\')
        $folder = ($relative -split '\\')[0]
        if (-not $totals.ContainsKey($folder)) { $totals[$folder] = [long]0 }
        $totals[$folder] += $file.Length; $totalBytes += $file.Length; $count++
        $lower = $file.FullName.ToLowerInvariant()
        $protected = ($lower -match '\\(evidence|model|models|src|scripts|profiles|docs|tests|\.git|data)\\') -or ($file.Extension -eq '.zip')
        $temporary = $relative.ToLowerInvariant() -match '(^|\\)(runs|logs|tmp|temp|cache)\\' -or $file.Extension -in @('.log', '.tmp', '.trace')
        if (-not $protected -and $temporary -and $file.LastWriteTimeUtc -lt $cutoff) {
            $candidates.Add([pscustomobject]@{ Path = $file.FullName; Bytes = $file.Length; LastWriteTimeUtc = $file.LastWriteTimeUtc.ToString('o'); Status = 'REVIEW_ONLY_NOT_SAFE_TO_DELETE_AUTOMATICALLY' })
        }
    }
}
$folderRows = @($totals.GetEnumerator() | ForEach-Object { [pscustomobject]@{ Folder = $_.Key; Bytes = $_.Value; GiB = [math]::Round($_.Value / 1GB, 3) } } | Sort-Object Bytes -Descending)
$folderRows | Export-Csv -LiteralPath (Join-Path $output ('folder-sizes-' + $stamp + '.csv')) -NoTypeInformation -Encoding UTF8
$candidates | Sort-Object Bytes -Descending | Export-Csv -LiteralPath (Join-Path $output ('review-candidates-' + $stamp + '.csv')) -NoTypeInformation -Encoding UTF8
$drive = Get-PSDrive -Name ([IO.Path]::GetPathRoot($scan).Substring(0,1)) -ErrorAction SilentlyContinue
$dockerSummary = @()
$dockerStatus = 'CLIENT_NOT_FOUND'
$dockerExitCode = $null
if ($SkipDocker) {
    $dockerStatus = 'SKIPPED_BY_REQUEST'
} elseif (Get-Command docker -ErrorAction SilentlyContinue) {
    $savedPreference = $ErrorActionPreference
    try {
        # Windows PowerShell can turn native stderr into ErrorRecord objects.
        # Docker availability must not abort the completed filesystem audit.
        $ErrorActionPreference = 'Continue'
        $dockerSummary = @(& docker system df 2>&1 | ForEach-Object { $_.ToString() })
        $dockerExitCode = $LASTEXITCODE
        if ($dockerExitCode -eq 0) { $dockerStatus = 'AVAILABLE' }
        else { $dockerStatus = 'UNAVAILABLE' }
    } catch {
        $dockerStatus = 'UNAVAILABLE'
        $dockerSummary = @($_.Exception.Message)
    } finally {
        $ErrorActionPreference = $savedPreference
    }
}
[ordered]@{ scannedRoot = $scan; fileCount = $count; totalBytes = $totalBytes
    freeBytes = $(if ($drive) { $drive.Free } else { $null }); scanErrors = $errors.Count
    reviewCandidateCount = $candidates.Count; deletedFiles = 0; dockerSummary = $dockerSummary
    dockerStatus = $dockerStatus; dockerExitCode = $dockerExitCode
    warning = 'Age and folder names do not prove that a file is disposable. No files, images, containers or volumes were removed.'
} | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $output ('summary-' + $stamp + '.json')) -Encoding UTF8
$folderRows | Select-Object -First 15 | Format-Table -AutoSize
Write-Host 'STORAGE_AUDIT_COMPLETE_NO_DELETIONS'
Write-Host ('Docker storage status: ' + $dockerStatus)
Write-Host ('Reports: ' + $output)
