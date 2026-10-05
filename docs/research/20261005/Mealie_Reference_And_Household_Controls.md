# Reference and household boundary controls

Engineering and research protocol — 2026-10-05

## Objective

Qualify the previously reproduced foreign-recipe HTTP 500 and test a new boundary:
two regular users in one group but distinct households. These are sequential
Provengo schedules, not overlapping HTTP requests. Existing generator modules,
profiles and runners are unchanged; this release adds explicit profiles and a
separate runner using the same generic OpenAPI compiler.

## Case 1: reference-controls

Create two private groups, households and regular users. Each owns one seeded
recipe and one list. A successful own-recipe addition is the positive control.
In each direction, read the foreign recipe and try adding its UUID to the actor's
own list. Expected controlled denial: 403 or 404. Preserve the immediate own-list
readback and verify selected identity/content/reference fields remain unchanged.
Then GET a fixed sentinel recipe UUID and require observed absence (404) during
qualification. Submit that same UUID through the same add operation. Expected
controlled rejection: 400, 404 or 422; 500 is a candidate. Preserve another own-list
readback and final owner recipe reads. If sentinel absence is not established,
the runner classifies the run as inconclusive and stops before a further replay.

Two sampled schedules are replayed with fresh namespaces, users and resources.
Each complete schedule contains 47 HTTP requests, including setup/authentication.
The server error with foreign and missing UUIDs may represent one shared lookup
error. Do not count these as independent bugs without a distinct mechanism.

## Case 2: household-controls

Create one private group, two separate households, and two regular users. Group
IDs must match; household and user IDs must differ. Each owns one recipe/list.
Both recipes are group-visible through authenticated recipe operations. Each
actor reads the other household's recipe and adds it to their own list (expected
200), then reads back the list. Both own and cross-household recipe UUIDs must
appear in recipeReferences, and list ownership remains unchanged.

Each actor then attempts to read the other household's list and add their own
recipe to that foreign list. Expected 403 or 404. The list owner reads it again;
selected list IDs, ownership, listItems and recipeReferences must be unchanged.
Final reads verify selected original recipe fields are unchanged.

The source policy is grounded in pinned v3.28.0 recipe group lookup and the
shopping-list household repository filter. It is not a policy inferred merely
from similarly named identifiers. A successful cross-household recipe addition
is expected sharing, not unauthorized access. Fixture guard checks ensure regular
roles and group/household bindings before recipe and list creation.

Two fresh complete schedules contain 46 requests each. Planned total across both
cases: 186 HTTP requests, plus the read-only server metadata preflight.

## Evidence and qualification

All HTTP runs through generated interfaces; stories coordinate actor tasks.
Every response and mutation request body is retained. Separate tokens are used
per actor. A native zero exit code is not a semantic verdict: independent receipt
validation applies status and state policies. Probes tolerate HTTP errors at the
transport layer so immediate readbacks can complete, while required setup/control
failures stop native execution. This does not waive the independent oracle.

The runner audits complete samples, limits sample files to 4 MiB, checks generated
model/sample hashes before replay, and preserves separate live ZIPs with their
SHA256 values. Fresh run credentials are preserved locally with existing Windows
DPAPI support. Passwords and tokens are scrubbed from campaign output.

If any complete run produces a candidate, the runner attempts a read-only Docker
log capture since campaign start (last 2000 lines, 15-second timeout). Failure to
collect logs is reported separately and does not convert a failure into a pass.
No automatic resource deletion, rollback, retry or full reset occurs.

## Tests and limits

Local generation is deterministic and stories contain no HTTP session calls.
Native tests at -Xmx512m replay two schedules for each profile against an
independent HTTP fixture. All four healthy runs pass, use fresh namespaces and
have maximum simultaneous HTTP requests equal to one. An additional injected
missing-reference 500 is rejected by independent qualification. Sample files
remain below 4 MiB; incomplete receipts are rejected.

The complete runner also passes against the independent fixture: generation,
native preflight, four replays and archive assembly complete with 187 observed
requests (186 modeled requests and one preflight); maximum simultaneous requests
is one.

These are mock acceptance tests, not live Mealie acceptance. Actual server
results remain pending. Protected-field comparisons do not assert equality of
all timestamps or detect effects outside the inspected resources. Windows
PowerShell execution of the new launch/save scripts remains to be validated on
the user's computer; they reuse the established Python resolver and credential
wrapper. No core generator changes are included.

## Primary source reviewed

https://github.com/mealie-recipes/mealie/blob/v3.28.0/mealie/services/recipe/recipe_service.py
https://github.com/mealie-recipes/mealie/blob/v3.28.0/mealie/routes/households/controller_shopping_lists.py
https://github.com/mealie-recipes/mealie/blob/v3.28.0/mealie/services/household_services/shopping_lists.py

The shopping-list ingredient lookup explicitly raises UnexpectedNone when the
recipe lookup has no result. This is a source-level hypothesis for the observed
500, not an observed traceback or proof of the complete exception path. The
existing single-recipe add endpoint is marked deprecated; this campaign keeps
that endpoint for comparable controls. Its bulk replacement is a separate future
experiment and must not silently replace the current reproduction.
