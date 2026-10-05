param([string]$Root=(Split-Path -Parent $PSScriptRoot),[switch]$Push)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Verify-Evidence.ps1') -Root $Root
if($LASTEXITCODE -ne 0){throw 'Archive validation failed.'}
$repo=Split-Path -Parent $Root
$relative=Split-Path -Leaf $Root
if($relative -ne 'supervisor-review-20261005'){throw 'Unexpected package directory name.'}
$top=git -C $repo rev-parse --show-toplevel
if($LASTEXITCODE -ne 0){throw 'The parent directory is not a Git repository.'}
if([IO.Path]::GetFullPath($top.Trim()) -ne [IO.Path]::GetFullPath($repo)){throw 'Package must be directly beneath the repository root.'}
$staged=@(git -C $repo diff --cached --name-only)
if($LASTEXITCODE -ne 0){throw 'Could not inspect staging.'}
$outside=@($staged|Where-Object{$_ -notlike "$relative/*"})
if($outside.Count -gt 0){throw 'Other changes are already staged. Preserve that staging before saving this package.'}
$oversized=@(Get-ChildItem -LiteralPath $Root -File -Recurse|Where-Object{$_.Length -ge 100MB -and $_.FullName -notlike '*\runs\*'})
if($oversized.Count -gt 0){throw 'Package contains a file of 100 MiB or more; review its storage policy first.'}
git -C $repo add -f -- $relative ":(exclude)$relative/runs" ":(exclude)$relative/validation/local"
if($LASTEXITCODE -ne 0){throw 'Package staging failed.'}
git -C $repo diff --cached --quiet -- $relative
$diffCode=$LASTEXITCODE
if($diffCode -eq 1){
 git -C $repo commit -m 'Freeze five Mealie finding groups with research and engineering reports' -- $relative
 if($LASTEXITCODE -ne 0){throw 'Package commit failed.'}
}elseif($diffCode -ne 0){throw 'Staged package inspection failed.'}
if($Push){
 $branch=git -C $repo branch --show-current
 if($LASTEXITCODE -ne 0 -or -not $branch){throw 'A named branch is required.'}
 git -C $repo push origin "HEAD:refs/heads/$branch"
 if($LASTEXITCODE -ne 0){throw 'Push failed; local commit retained.'}
 $local=git -C $repo rev-parse HEAD
 $remote=git -C $repo ls-remote origin "refs/heads/$branch"
 if($LASTEXITCODE -ne 0 -or -not $remote -or ($remote -split '\s+')[0] -ne $local){throw 'Remote SHA verification failed.'}
 Write-Host "SUPERVISOR_REVIEW_PUSH_VERIFIED: $local"
}else{Write-Host 'SUPERVISOR_REVIEW_COMMITTED_LOCALLY; use -Push to publish to the configured origin.'}
