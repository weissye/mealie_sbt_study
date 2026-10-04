# Stale snapshot writes after shared dependency deletion

## Goal and provenance

This optional generic-generator extension probes a new lifecycle mechanism. It does not repeat quantity-merge confirmation. It generates interfaces and actors from the pinned OpenAPI contract plus explicit relationship/policy profiles. Stories contain no HTTP service calls. Requests remain sequential; Provengo varies the surrounding construction order.

Four matched cases: food control, unit control, food deletion, unit deletion. Two sampled schedules per case execute with fresh owned resources. All structural bindings and one shopping-list association precede the probe; remaining associations follow it. Three recipes include two shared referrers and an independent control; three lists protect recipe association identifiers.

## Program

1. GET the target and all recipe/list controls. Retain the original full recipe response before deletion.
2. In deletion cases, DELETE the shared target; qualify successful nulling or unchanged rejection using fresh GETs.
3. GET the source again, but construct the PUT body from the retained pre-deletion snapshot, projected through the operation's request schema. Change only the description field.
4. Send the stale PUT; accept 200/204 or explicit 400/409/422 for observation.
5. Read all source/control resources and the original target again.
6. A rejected write must preserve the current source's protected ingredients and description, all other protected sources and list associations, and the observed target state. A control write must update description and preserve ingredients.
7. A successful write after a successful deletion is classified `POLICY_OBSERVATION`, not a confirmed bug. Preserve submitted/observed ingredient projections, status and target readback. Inline resource recreation can be legitimate; detailed qualification must precede any defect claim.

Derived ingredient display text is explicitly excluded, preserving the previous corrected oracle. Quantity, identities and other writable ingredient fields remain protected. A mismatch produces `REFERENCE_CANDIDATE`; a non-authentication 5xx produces `SERVER_ERROR_CANDIDATE`. Neither constitutes confirmation without fresh-resource reproduction and independent review. Authentication/transport/unclassified failures stop the campaign.

## Running at home

Requires the preceding generator/reference-lifecycle changes, Python, Node, Provengo CLI and a reachable Mealie v3.28.0 instance. Home Docker restoration is a separate prerequisite: this package does not restore databases, reset a server, or start backup containers. If `/openapi.json` is unreachable, finish restoration before running.

Extract the delta into `D:\Yeshayahu\Temp\mealie_sbt_study`, then run `scripts\Run-Generic-Stale-Snapshot.ps1 -Username 'changeme@example.com'`. The root defaults to the script's parent. Java heap is 512 MiB; preflight requires 1024 MiB free RAM and 1 GiB free disk. There is no requirement to close Chrome if these checks pass.

The runner generates models and samples locally; evidence is saved under `Downloads\mealie-stale-snapshot-<timestamp>\campaign.zip`, including generation, sampling, live run, classification and summary. Upload that campaign ZIP after completion or failure. No automatic retries, cleanup, reset or Git push occur.

## Limits

A successful stale write is deliberately observation-only until recreation policy is qualified. The target GET queries the original identity; newly created identities must subsequently be checked independently. Protected list checks cover recipe references, not complete shopping-item arithmetic. This campaign does not test simultaneous HTTP, reset/replay, database internals, or cross-user authorization. Passing these cases does not negate the previously archived quantity discrepancy.

## Git checkpoint

An optional `scripts/Save-Generic-Stale-Snapshot.ps1 -Push` stages and commits only the listed release paths, preserving unrelated staged work. It creates a local checkpoint branch first and verifies the pushed branch's remote SHA. It does not archive new live campaign evidence; preserve that evidence separately after review. A divergent remote stops normal push; no force push or reset is used.
