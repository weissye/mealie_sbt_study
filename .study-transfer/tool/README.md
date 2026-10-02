# Two-study Git handoff

This tool transfers the two existing private repositories and an encrypted snapshot of project files and the 15 Docker containers listed in `transfer-plan.json`. Code remains in each original repository. Snapshot chunks travel through Git LFS in `vikunja_tse_study`. Subsequent handoffs use the tool committed under `.study-transfer/tool`; the installation ZIP is needed only once.

## Validation boundary

The supplied automated tests exercise encryption, corruption detection, archive round trips, unchanged-file staging, Docker configuration reconstruction, backup verification ordering and source restart on export failure. Docker tests use a simulated API. An additional local integration check uses real Git LFS to stage prelinked ciphertext, commit valid pointers and run LFS fsck. Windows hard-link behavior and native Docker transfer acceptance remain unverified. Windows PowerShell, Docker Desktop archives, native image loading and GitHub LFS upload/download have **not** been executed in the development environment. Successful export is not proof of successful home restoration. Treat the first export/import as migration acceptance, retain originals and read the resulting status.

## At work: first installation

```powershell
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\study_git_transfer_v1.zip" -DestinationPath 'C:\work\temp' -Force
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& 'C:\work\temp\study-git-transfer-v1\Invoke-Study-Git-Transfer.ps1' -Mode Export -InstallDependencies -Push
```

Prerequisites: both folders already contain Git repositories on `main`, the origin URLs are the existing `weissye` private repositories, Git LFS is installed, Docker Desktop uses Linux containers and is running, and Python 3.12 is installed. Complete any active test/campaign first. The wrapper rejects a visible active Provengo Java process; this is not a detector for every possible background writer.

Enter a new transfer password of at least 12 characters. Keep it independently of Git and use it on both computers. The tool does not recover forgotten passwords. It installs Python Docker/cryptography dependencies with pip when `-InstallDependencies` is supplied. The password is passed through a temporary process environment value, not a command-line argument or Git file.

Export commits tracked source edits and the tool. Previously untracked or ignored project files travel in the encrypted snapshot, rather than being automatically added to plaintext Git. Normal Git history that already contains secrets is not scrubbed by this tool. The source code is unchanged by the migration backend. The selected running Docker services are stopped during capture and restarted afterward; originally stopped services stay stopped. Source files and data are not deleted. New temporary commit images are removed after their archive is captured.

`SOURCE_EXPORT_AND_PUSH_COMPLETE` means both local commits were pushed without a reported Git error. Inspect `snapshot_encrypted_gib` and `new_encrypted_gib`. Compression size is not predictable from raw JSON sizes. Version 1.1 keeps each immutable encrypted chunk as a single physical file shared by hard links between the transfer tree and Git LFS storage. It verifies hard-link support before stopping services. Existing encrypted objects from the failed version 1 export are authenticated and reused. If duplicate encrypted copies already exist, their hashes are checked and their paths are joined without changing the ciphertext. No original study files, selected samples or server data are deleted. At least 1 GiB is reserved plus room for bounded LFS clean temporary files; the tool rejects excess capacity with measured free-space and capacity values. Hard links must be supported on the same filesystem (normally NTFS on the source Windows machine). Docker's own image commit storage also needs space in Docker Desktop's data disk. A failed upload leaves the local committed snapshot intact; after resolving Git/LFS capacity or authentication, use ordinary `git push origin main` in both repositories without recapturing the data.

For the inventory supplied, the two trees occupied about 26.4 GiB and free disk space was about 9.7 GiB. The new-object cap is at most 8 GiB per export and is reduced to the current free space minus 1 GiB. This replaces version 1's half-free-space cap. Existing authenticated encrypted chunks are reused and do not count as new bytes. The first export may fail cleanly if images/data do not compress sufficiently. No billing plan is changed. GitHub LFS quota and historical objects must be accounted for separately; this tool does not promise unlimited or free storage, and does not prune LFS history.

## At home: first checkout

Keep existing folders as backups; do not clone over them. Run the following after Git, Git LFS, Python and Docker Desktop are installed:

```powershell
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
foreach ($name in @('mealie_sbt_study','vikunja_tse_study')) {
    $path = Join-Path 'C:\work\temp' $name
    if (Test-Path -LiteralPath $path) {
        Move-Item -LiteralPath $path -Destination "$path.before-git-$stamp"
    }
}
git lfs install
git clone https://github.com/weissye/mealie_sbt_study.git C:\work\temp\mealie_sbt_study
if ($LASTEXITCODE -ne 0) { throw 'Mealie clone failed.' }
git clone https://github.com/weissye/vikunja_tse_study.git C:\work\temp\vikunja_tse_study
if ($LASTEXITCODE -ne 0) { throw 'Vikunja clone failed.' }
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& 'C:\work\temp\vikunja_tse_study\.study-transfer\tool\Invoke-Study-Git-Transfer.ps1' -Mode Import -InstallDependencies -Pull
```

The fixed project locations must be the same on both computers. The transfer plan is currently pinned to the supplied container inventory, not an automatic discovery of every container or disk. If names, mount sources/access modes, network requirements or volume drivers change, export rejects the discrepancy. Refresh the plan instead of bypassing that check.

Import validates the password and every encrypted chunk before touching existing Docker data. It stages changed project files and verifies their hashes. Byte-identical files are read and checked but not duplicated. Images are loaded before existing containers are stopped. Existing named-volume contents are captured into a separate encrypted local backup and authenticated before clearing those volumes. Existing bind directories and replaced project files are moved into the local backup tree. Existing containers are renamed with `.study-backup-...` and retained. Do not start old backup containers concurrently with restored containers: they can refer to the same named volumes.

Mounted data is restored into the original volume names/bind locations and checked independently through Docker, comparing file bytes, UID/GID, permissions and links. Containers retain their saved configuration, ports, environment, network aliases and running/stopped state. Both Keycloak containers have no mounts in this inventory, so their saved writable layers are essential and are captured with stopped-container image commits.

`HOME_FILES_AND_DOCKER_BYTES_RESTORED` means file checks, mount checks and the expected container running/stopped state passed. It does **not** establish service health, authentication, API behavior or test acceptance. Run the existing project smoke/acceptance scripts afterward. A running test process cannot resume mid-execution; existing selected samples and their files can be reused.

## Subsequent handoffs

At the computer where work was completed:

```powershell
& 'C:\work\temp\vikunja_tse_study\.study-transfer\tool\Invoke-Study-Git-Transfer.ps1' -Mode Export -Push
```

At the receiving computer, finish local work and then:

```powershell
& 'C:\work\temp\vikunja_tse_study\.study-transfer\tool\Invoke-Study-Git-Transfer.ps1' -Mode Import -Pull
```

Do not edit both machines independently before handoff. Import rejects tracked edits or code differing from the authenticated saved reference. Merge code deliberately before making a new complete snapshot. Nonconflicting extra untracked files on the receiving computer remain in place; import is an overlay, not a directory purge.

## VS Code

Open both existing folders without copying them:

```powershell
$workspace = @{
    folders = @(
        @{ path = 'C:\work\temp\mealie_sbt_study' },
        @{ path = 'C:\work\temp\vikunja_tse_study' }
    )
} | ConvertTo-Json -Depth 5
$workspace | Set-Content -LiteralPath 'C:\work\temp\research.code-workspace' -Encoding UTF8
code 'C:\work\temp\research.code-workspace'
```

## Scope and exclusions

Regular project files include ignored samples, ensembles, contracts, logs, downloaded archives/JARs and local configuration. `.git`, `.study-transfer`, `node_modules`, `.venv`, `venv`, `__pycache__` and `.pytest_cache` directories are excluded. Writable Docker bind roots are captured once through Docker instead of also being included in the Windows file archive. Project snapshots verify file content and restore file modification times to improve chunk reuse. They do not preserve Windows ACLs or empty directory structure. Symlinks/junctions in the included project tree are rejected rather than silently followed. Docker mount archives preserve and verify the Linux directory/file metadata recorded by Docker.

Git, Python, Java, Node, Docker Desktop and a system-installed Provengo CLI still need installation on the receiving computer. IDE sessions, running processes, credential-manager accounts, Docker Desktop settings, external paths and containers outside the selected 15 are not migrated. Read-only `/etc/localtime` remains a dependency on the destination Docker engine.

## Failure and local recovery evidence

`TRANSFER_NOT_ACCEPTED` is a failure, even when some stages completed. An export failure attempts to restart source services; a failed restart identifies their names for manual intervention. Partial encrypted objects remain available for inspection/reuse.

Import creates `.study-transfer/local/<timestamp-id>/restore-status.json`. Before cutover, failure attempts to restart the original destination containers. After cutover begins, automatic rollback is deliberately not attempted: the backup tree, original renamed containers and encrypted original volume snapshots are retained. The error provides the exact backup directory. Stop and inspect this evidence rather than blindly repeating import. `destination-before.json` refers to an encrypted backup manifest in `before-store`, using the same transfer password. `files-before` and `binds-before` contain moved original files/directories. Recovery of named volumes requires restoring the corresponding verified archive while all consumers are stopped; seek review before doing this manually. There is no unattended rollback command in this version.

Local backups are excluded from Git. The successful **source handoff snapshot** and its decryptor travel entirely through Git/LFS; destination rollback copies stay on that destination machine. Never delete either original project backup or local restore backups until application acceptance has passed.

## Development checks

```powershell
py -3 -m unittest discover -s C:\work\temp\study-git-transfer-v1\tests -v
```

See `validation.txt` for the checks run when this package was built.

## Updating a failed version 1 export

```powershell
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\study_git_transfer_v1_1_disk_fix_delta.zip" -DestinationPath 'C:\work\temp' -Force
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& 'C:\work\temp\study-git-transfer-v1\Invoke-Study-Git-Transfer.ps1' -Mode Export -Push
```

Use the same encryption password as the failed export. Dependencies are already installed. Do not delete `key.json` or partial `.blob` files; they are authenticated and reused. A failed export did not push a complete snapshot. The correction reduces local duplication and revises the overly conservative cap, but cannot guarantee that all project files plus Docker archives fit in the actual remaining space. GitHub LFS capacity is separate from local free space. The updated tool and README are copied into both repositories by the next export.
