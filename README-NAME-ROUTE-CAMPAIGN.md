# Name-driven route migration and old-alias reuse

This delta targets the existing generic generator installed at source commit fb00bc2 or later. It adds new profiles and a new runner; the previous route profiles and runner are retained.

Run `scripts/Save-Generic-Name-Route-Campaign.ps1 -Push` to commit only the release files, then `scripts/Run-Generic-Name-Route-Campaign.ps1 -Username changeme@example.com`.
The root defaults to the parent of the scripts directory on both computers. Start the existing Mealie study container if needed. No reset, deletion or full snapshot import is required.

## Six new-resource runs

- Control, two sampled schedules: change description twice while protecting route, UUID, instruction content, quantities and references.
- Rename, two sampled schedules: change the original linked recipe name twice, checking the derived route and the retirement of each old alias.
- Reuse, two sampled schedules: rename the original linked recipe, then rename the third owned recipe to the original name. The reused old alias must resolve to the third UUID; links and shopping quantities must still refer to the original UUID.

The reuse probe renames an already-created third recipe rather than creating a second recipe mid-probe. All three recipes are newly created separately for every replay.

## Generic explicit policy

`route_driver_field` is optional and defaults to `route_field` for older profiles. The new Mealie profiles explicitly set it to `name`. Generated new values use safe lower-case ASCII names with hyphens, whose expected alias is declared by this probe. Alias reuse uses the original observed name and alias, not an inferred UUID/name equivalence. The compiler validates the driver against request and read schemas and rejects use of the stable identity field.

`capture_route_evidence` is optional and defaults to false. Enabled probes save the exact write body and raw write response code/body, then read the old alias, requested alias and six referrers before semantic validation. A semantic failure therefore retains the current phase's raw observations. Transport failures can still leave partial evidence; they are not successful bug confirmations.

HTTP runs through generated interfaces. Stories only orchestrate interface calls, including the pinned-version metadata preflight. The Python classifier and evidence extractor send no HTTP.

## Results and limits

The unique Downloads campaign directory contains generation, sampling, each live ZIP, independent classification and raw-evidence JSON, plus the campaign summary and `campaign.zip`. Upload `campaign.zip` from the printed Review ZIP path.

PASS means the defined checks completed, not full dependency-graph coverage. A ROUTE_CANDIDATE needs independent examination and a fresh-resource reproduction. Multiple orders with the same defect count as one bug. Historical home candidates remain open; these new work resources do not reconstruct their state.

The runner caps Java heap at 512 MiB and checks for 1024 MiB free RAM and 1 GiB free disk. Closing Chrome is not required if those resources are available. Samples exceeding 128 MiB stop the campaign.

Native regression tests were run on Linux using the pinned Provengo jar and a controlled HTTP fixture. This is not a live Mealie acceptance or a Windows execution claim. PowerShell must be verified by the local run.
