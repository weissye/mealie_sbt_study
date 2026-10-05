[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$CampaignZip,
    [string]$Root=(Split-Path $PSScriptRoot -Parent),
    [switch]$Push
)
$ErrorActionPreference='Stop'
$Root=[IO.Path]::GetFullPath($Root)
if (-not (Test-Path -LiteralPath $CampaignZip -PathType Leaf)) { throw 'Campaign archive not found.' }
. (Join-Path $PSScriptRoot 'Resolve-Python.ps1')
$python=Get-StudyPython
$hash=(Get-FileHash -LiteralPath $CampaignZip -Algorithm SHA256).Hash.ToLowerInvariant()
$relative='evidence/copy-isolation-'+$hash.Substring(0,12)
$destination=Join-Path $Root $relative
New-Item -ItemType Directory -Path $destination -Force | Out-Null
$target=Join-Path $destination 'campaign-original.zip'
if (Test-Path -LiteralPath $target) {
    if ((Get-FileHash -LiteralPath $target).Hash.ToLowerInvariant() -ne $hash) { throw 'Existing evidence differs. Nothing was overwritten.' }
} else { Copy-Item -LiteralPath $CampaignZip -Destination $target }
if ((Get-FileHash -LiteralPath $target).Hash.ToLowerInvariant() -ne $hash) { throw 'Evidence copy verification failed.' }
& $python.Exe @($python.Prefix) -B (Join-Path $Root 'generic-generator\tools\verify_copy_campaign.py') `
    --campaign $target --output (Join-Path $destination 'verification.json')
if ($LASTEXITCODE -ne 0) { throw 'Campaign verification failed. Original archive was preserved; Git was not changed.' }
@'
# Copy campaign handoff

Raw reviews and checksums are archived. Read verification.json before declaring
a finding. COPY_CANDIDATE requires independent analysis of request/response bodies
and fresh-resource reproduction. Repeated manifestations of one mechanism count
as one bug. PASS covers only the configured field/reference scope. Full reset/replay
remains pending. No new bug is automatically confirmed by this archive operation.
'@ | Set-Content -LiteralPath (Join-Path $destination 'HANDOFF.md') -Encoding UTF8
git -C $Root add -f -- $relative
if ($LASTEXITCODE -ne 0) { throw 'Evidence staging failed.' }
git -C $Root diff --cached --quiet -- $relative
$diffCode=$LASTEXITCODE
if ($diffCode -eq 1) {
    git -C $Root commit --only -m 'Archive independently qualified linked-copy campaign' -- $relative
    if ($LASTEXITCODE -ne 0) { throw 'Evidence commit failed.' }
} elseif ($diffCode -ne 0) { throw 'Evidence staged check failed.' }
if ($Push) {
    git -C $Root push origin HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Evidence push failed.' }
    $branch=git -C $Root symbolic-ref --short HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Branch verification failed.' }
    $localHead=git -C $Root rev-parse HEAD
    $remoteLine=git -C $Root ls-remote origin ('refs/heads/'+$branch)
    if ($LASTEXITCODE -ne 0 -or -not $remoteLine -or (($remoteLine -split '\s+')[0] -ne $localHead)) { throw 'Remote evidence commit verification failed.' }
    Write-Host "COPY_EVIDENCE_PUSH_VERIFIED: $localHead"
}
Write-Host "Evidence directory: $destination"
