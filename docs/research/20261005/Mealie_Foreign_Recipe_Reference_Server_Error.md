# Foreign recipe reference causes shopping-list HTTP 500

Engineering and research report — 2026-10-05

## Observed defect

Mealie v3.28.0 returns HTTP 500 with the response body `Internal Server Error`
when a regular authenticated user adds a recipe belonging to a different group
to the user's own shopping list:

`POST /api/households/shopping/lists/{item_id}/recipe/{recipe_id}`

Request body: `{"recipeIncrementQuantity": 1}`.

The expected profile policy is a controlled denial (403 or 404). The conclusion
does not depend on choosing between those codes: an internal server error is
the observed server robustness defect. Root cause and exploitability remain
unqualified; no server traceback has been collected in this archive.

## Reproduction and controls

Four complete Provengo runs contain 206 captured HTTP responses. Two runs use
two regular users within one group and household; both pass the declared policy.
Two runs use users in distinct groups and households. Each distinct-scope run
reproduces the same 500 in both directions, yielding four manifestations of one
candidate defect, not four independent bugs. The two runs use fresh namespaces,
users, recipes and shopping lists.

Authentication succeeds. Both tested users have admin, canManage,
canManageHousehold, canOrganize and canInvite set to false. The administrator is
used only for setup. Each user successfully adds their own recipe to their own
list with HTTP 200 before the foreign-reference probe. Foreign reads, copies,
updates, deletes and list reads return 404. Owner readbacks return 200.

Independent requalification checks actor/operation attribution, task order,
scope identities, declared status policy and protected state comparisons. Only
the two foreign-add status mismatches per distinct-scope run are reported.
Protected recipe/list identities, contents and references pass the configured
readback checks. This does not establish equality of every field, transaction
atomicity or absence of side effects outside the inspected resources.

## Why multiple identities matter

A single identity cannot express the tested boundary: the list is authorized
for actor A while the referenced recipe belongs to actor B in another group.
Multiple identities exposed this condition. Concurrent HTTP requests were not
required: Provengo generated dependency-respecting sequential interleavings.

This evidence establishes a repeated server error under a foreign-reference
condition. It does not establish that complex interleaving is necessary to
reproduce it, or that another tool cannot find it. A minimal reproduction and
missing-resource control are needed before making those research claims.

## Qualification limits and next experiments

1. Preserve the server exception corresponding to the four requests.
2. Compare own existing recipe, foreign existing recipe and nonexistent recipe
   through the same endpoint with otherwise equivalent request arguments.
3. Determine whether the fault is generic missing-reference handling or specific
   to cross-group lookup. Keep a minimal successful prefix and fresh-resource
   confirmation.
4. Extend the identity matrix to same group / different households. Cross-group
   and cross-household access are different policies and must not be conflated.
5. Probe reference removal/replacement and copy/import actions across scope
   boundaries, with explicit policy and owner readbacks for each operation.

No unauthorized data disclosure or unauthorized mutation has been demonstrated.
Full reset/replay has not been performed. Earlier quantity and internal-copy
reference defects are separate findings.

## Evidence provenance

Campaign source commit: `f1f29cf5dad0991faa677d0cc98481f56ef5de28`.
Pinned OpenAPI SHA256:
`90e19aa713ab4ba15352627aca7dc37290f868b213eb65a3e1564f3b7a7ff292`.

`campaign-original.zip` preserves the uploaded archive without rewriting it.
It contains four nested live archives with request/response observations,
generated interfaces/stories, samples, plans and acceptance records.
`execution-original.txt` preserves the uploaded console transcript.
`checksums.json` identifies the archived evidence and qualification files.
`verify_campaign.py` checks archive integrity, independently reruns the frozen
oracle and verifies that exactly the documented discrepancies remain.
Credentials are not added to this release; DPAPI credentials remain local.
Git publication is established only by the save script's remote SHA check.
