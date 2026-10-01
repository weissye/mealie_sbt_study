[CmdletBinding()]
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent),
    [switch]$Apply
)
$ErrorActionPreference = 'Stop'
$planPath = Join-Path $Root 'plans\storage-duplicate-review.json'
$plan = Get-Content -LiteralPath $planPath -Raw | ConvertFrom-Json
$allowed = 'C:\work\temp\RestEvo\FSE2027_artifact\generated_outputs\'
$reportDirectory = Join-Path $Root 'storage-audit'
New-Item -ItemType Directory -Path $reportDirectory -Force | Out-Null
$reportPath = Join-Path $reportDirectory ('duplicate-cleanup-' + [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss-fff') + '.json')
$rows = New-Object System.Collections.Generic.List[object]
$freedBytes = [long]0

function Assert-ReviewedPath([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    if (-not $full.StartsWith($allowed, [StringComparison]::OrdinalIgnoreCase)) { throw 'Path is outside the reviewed subtree.' }
    if ([IO.Path]::GetFileName($full) -notmatch '^network\.testing\.26592\.[123]\.txt$') { throw 'Unexpected filename in the plan.' }
    $cursor = $full
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            $entry = Get-Item -LiteralPath $cursor -Force
            if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse points are not permitted.' }
        }
        $cursor = Split-Path -Path $cursor -Parent
    }
}

foreach ($item in $plan.items) {
    $row = [ordered]@{ keep = $item.keep; remove = $item.remove; sha256 = $null; bytes = $item.expectedBytes; status = 'PENDING'; error = $null }
    $rows.Add([pscustomobject]$row)
    $record = $rows[$rows.Count - 1]
    try {
        Assert-ReviewedPath $item.keep
        Assert-ReviewedPath $item.remove
        if ($item.keep -eq $item.remove) { throw 'Keep and remove paths are equal.' }
        if ($item.keep -notlike '*\netbox_a11_evidence_releases\*') { throw 'Keep path is not the reviewed evidence release.' }
        if ($item.remove -notmatch '\\(netbox_restler_completed_20260902_204304|netbox_a11_task_scoped_v2)\\') { throw 'Removal path is not a reviewed completed-output copy.' }
        if ($item.remove -like '*\netbox_a11_evidence_releases\*') { throw 'Evidence release copies cannot be removed.' }
        if (-not (Test-Path -LiteralPath $item.remove -PathType Leaf)) { $record.status = 'ALREADY_ABSENT'; continue }
        $keepFile = Get-Item -LiteralPath $item.keep
        $removeFile = Get-Item -LiteralPath $item.remove
        if ($keepFile.Length -ne $item.expectedBytes -or $removeFile.Length -ne $item.expectedBytes) { throw 'File size differs from the reviewed audit.' }
        if ($removeFile.LastWriteTimeUtc -gt [DateTime]::UtcNow.AddDays(-14)) { throw 'Removal file was modified recently.' }
        $keepHash = (Get-FileHash -LiteralPath $item.keep -Algorithm SHA256).Hash
        $removeHash = (Get-FileHash -LiteralPath $item.remove -Algorithm SHA256).Hash
        if ($keepHash -ne $removeHash) { throw 'Contents differ. Nothing will be removed.' }
        $record.sha256 = $keepHash
        $record.status = 'VERIFIED_DUPLICATE_PREVIEW'
        # Persist the recovery source and hash before any deletion.
        $rows.ToArray() | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8
        if ($Apply) {
            # Verify the preserved source again immediately before deletion.
            if ((Get-FileHash -LiteralPath $item.keep -Algorithm SHA256).Hash -ne $keepHash -or
                (Get-FileHash -LiteralPath $item.remove -Algorithm SHA256).Hash -ne $keepHash) { throw 'A file changed after verification.' }
            Remove-Item -LiteralPath $item.remove -ErrorAction Stop
            $record.status = 'REMOVED_VERIFIED_DUPLICATE'
            $freedBytes += $removeFile.Length
        }
    } catch {
        $record.status = 'SKIPPED'; $record.error = $_.Exception.Message
    } finally {
        $rows.ToArray() | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8
    }
}
$rows | Select-Object status, bytes, remove | Format-Table -AutoSize
Write-Host ('Duplicate bytes removed: ' + $freedBytes)
Write-Host ('Recovery manifest: ' + $reportPath)
Write-Host 'The evidence release copies were preserved. No directories were removed.'
if (-not $Apply) { Write-Host 'Preview only. Use -Apply to remove verified duplicate files.' }
