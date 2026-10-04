# Mealie quantity discrepancy family freeze

Date: 2026-10-04. Scope: one retained defect family, with repeated addition and removal manifestations. No internal root cause or separate bug count is established.

Main evidence comprises 24 generated native runs: 18 semantic failures and 6 successful complete runs. The original two failed runs, ten scaling controls, four integer merge lifecycles, and eight removal isolation controls are all preserved. The authentication 401 attempt is excluded from semantic counts. Earlier successful campaigns are contextual controls and are not included in the 24-run count.

Raw source ZIP bytes are preserved. The checksum manifest covers every file in this frozen directory other than the manifest itself. verify_freeze.py validates checksums and independently recomputes semantic expectations from the preserved live logs; it makes no server requests. Generated plans, interfaces, stories, sampled schedules, acceptance records and logs are retained inside their original review ZIPs as supplied. No claim is made that packet captures, database snapshots or full reset/replay were collected.

work/generator-and-scripts-snapshot.zip is the source snapshot used when preparing this freeze. Existing live project paths appear in source-paths.json. The Git script stages the current local versions of those source files and records their current hashes in docs/research/20261004/git-source-hashes.json. It does not replace local source code with the archived snapshot. Differences are preserved as local work; evidence remains linked to the archived models and plans.

Run scripts/Save-Mealie-Research-Day.ps1 -Push after extracting the delivery. It verifies evidence, creates a checkpoint branch, commits only the explicit evidence/document/source paths, pushes the current branch, and checks the remote commit. Docker runtime state is not transferred by this commit. The existing home restoration remains a separate unfinished task.
