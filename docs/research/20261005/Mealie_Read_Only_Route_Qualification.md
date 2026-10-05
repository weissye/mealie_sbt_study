# Read-only route state qualification

The source/evidence pull at work reached commit 2611e59. The preserved live campaign ran at home against that machine's local Mealie database. Git commits of code and evidence do not synchronize a later Docker database state. The original home resources may therefore be absent from the work server. This audit reports missing resources without treating them as semantic defects.

## Evidence boundary

The six original nested live ZIP digests and two successful controls are verified offline. Four failed runs sent an unchanged name with a new slug and failed on a new-route GET with 404. Their exact pre-write targets, source identities, protected projections and request bodies are loaded from the original archive. The pinned contract SHA is required. The outer campaign SHA is verified against the Git-preserved SHA256.txt before API requests. ZIP member names are canonicalized without weakening duplicate-member checks.

## Native audit

The generated project keeps transport in interfaces and orchestration in stories. Sampling is offline. Live execution performs one authentication POST, then 30 GETs: contract-version metadata, authenticated identity, and 28 resource reads. Four failed runs each supply three original recipe routes, three original shopping-list routes, and the attempted new recipe route. No resource creates, writes, deletes, resets or retries are performed.

Successful raw JSON responses and error responses are preserved in observations.json and redacted native logs. Recipe UUIDs, names, original aliases, instruction content, quantities and all protected source views are compared against archived baselines. Only the changed target's declared update timestamps and explicitly replaceable child instruction UUIDs may differ. Embedded expected target views are refreshed from that validated target, while unrelated recipes remain protected. Each observed instruction ID replacement is recorded. Unexpected quantities, stable identities, name changes, unrelated timestamps or alias resolution remain discrepancies requiring qualification.

## Outcomes and limits

ORIGINAL_RESOURCES_UNAVAILABLE: all six original resources in each failed run returned 404. The original data is unavailable on this server; do not claim a bug or close the home finding from these results. Complete the audit on the home server containing those resources.

DIRECT_SLUG_IGNORED_STATE_PRESERVED: the current original resources have their archived identities and protected state, and the requested route returns 404. This supports the pinned-source explanation that unchanged-name PUT retained the original slug. It is bounded current-state evidence; it cannot reconstruct the original PUT response or rule out intervening edits.

STATE_DISCREPANCY_REQUIRES_QUALIFICATION: a compared invariant differs. Preserve and examine it before any new mutation or counting a defect. Partial resources, unexpected HTTP errors, account differences or server-version differences have separate statuses.

The name-driven compiler change remains outside this delta and is not installed by it. Full reset/replay remains pending. Windows PowerShell cannot be executed in this Linux validation environment; native read-only behavior and the CLI are exercised with the pinned Provengo jar and local mock HTTP servers.
