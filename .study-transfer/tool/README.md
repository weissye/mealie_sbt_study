# Abandoned encrypted export cleanup

Run Clear-Abandoned-Study-Transfer.ps1 without -Apply to preview, or with -Apply to remove authenticated transfer objects unreferenced by the current transfer manifest, Git index, Git history, reflogs, or Git LFS history. Keep all transfer/export processes stopped and avoid Git changes during cleanup. Use the existing encryption password.

Only exact .study-transfer/objects/<digest>.blob files and their matching, unreferenced local LFS copies are candidates. Key metadata, source files, completed snapshots, Docker data and historical Git objects are preserved. Candidates with additional hard links are preserved. An audit report is written before deletion. If a file is locked, cleanup stops; the report records completed deletions.

Removing abandoned objects discards partial export reuse. It does not remove source data. Do not start another export until free space is checked.

Validation: six tests on a local real Git/Git LFS repository cover preview, hard-link deletion, completed manifest protection, index/history protection, wrong password, corrupted ciphertext and malformed manifest. Native Windows execution has not been performed here.
