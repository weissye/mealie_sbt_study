# Mealie: Cross-Household List Mutation Persisting After an Error

Engineering and research record — 2026-10-05

## Finding and qualification

In the preserved local Mealie v3.28.0 campaign, a regular user changed a shopping list belonging to another household in the same group. The corresponding operation returned HTTP 500. An owner-authenticated read subsequently confirmed one additional item. This is evidence of a household isolation violation and a partial state change following failure. It is a new finding in this study; global novelty and affected versions beyond the tested version have not been established.

The campaign contains four complete native Provengo runs and 186 recorded responses. Two reference-control runs contain 47 responses each; two household-control runs contain 46 each. Separate regular actors, fresh resource namespaces and both directions provide four manifestations of one household-list finding, rather than four different bugs.

## Environment and provenance

The supplied campaign used the owned local server at 127.0.0.1:9925, Mealie v3.28.0 and contract SHA256 90e19aa713ab4ba15352627aca7dc37290f868b213eb65a3e1564f3b7a7ff292. Campaign source was pushed as 81d332221c3f567044c9a15f85297cb064b08f69. The original campaign archive is preserved byte-for-byte in the accompanying evidence directory. Its checksum, nested archive hashes, generated plans, interfaces, stories, runtime receipts and captured server logs form the provenance record. Tool versions and configuration retained in the original archives remain authoritative; absent metadata must not be inferred.

Provisioning used an administrator; resource observations used regular users. Recorded admin, canManage, canManageHousehold, canOrganize and canInvite flags were all false. Household-control actors shared a group and had distinct household identifiers. Provengo coordinated sequential operation order; this experiment does not establish a simultaneous-request concurrency defect.

## Evidence of the state change

For each of four observations, the other household's list read returned 404 and the write returned 500. The owner read returned 200. The same list UUID grew from two items to three, with exactly one new item UUID and quantity 2. The added item retained the victim household ID and referred to the acting user's recipe. All pre-existing item objects were unchanged. Top-level recipeReferences were unchanged, indicating an incomplete operation rather than a complete normal update.

The independent verifier resolves target-list bindings and inspects the recorded operation interval. Exactly one recorded mutation targeted that victim list between the baseline and owner read. An intervening operation on a different list cannot explain the delta. This rules out intervening recorded campaign writes; it cannot rule out arbitrary external activity absent from the capture.

Permitted sharing controls succeeded: reading another household's recipe in the same group and adding it to an owned list returned 200. Own-resource controls also succeeded. Thus recipe sharing within a group must not be classified as the isolation defect.

## Distinction from the earlier server-error finding

| Family | Observed result | State evidence | Classification |
| --- | --- | --- | --- |
| Unavailable recipe | Foreign-group and confirmed absent recipe identities returned 500 | Selected protected readbacks passed | Existing missing-reference error family; eight manifestations in this campaign |
| Other household's list | 500 followed by an owner-visible new list item | Four fresh directional observations | Separate household isolation and failure-atomicity finding |

Captured logs contain UnexpectedNone: Recipe not found for the reference family and AttributeError involving NoneType and list_items for the household-list family. Distinct exceptions and state effects justify separate tracking. They do not alone prove completely independent root causes. Duplicate log renderings are not additional reproductions.

## Engineering interpretation and remediation requirements

The observed behavior is consistent with a mutation occurring before complete ownership validation and with an error in later list processing. This is a hypothesis supported by the traces, not a demonstrated transaction-level explanation. Review authorization and list resolution before any item mutation. Ensure failed operations do not leave partial item/reference updates. Apply the same household boundary to list items and parent lists. Regression checks should include both permitted sharing and denied operations, and compare owner-visible state after an error.

## Research interpretation

Actor-bound identities and explicit scope policies expose an effect that status-code-only testing would miss. The counterexample combines a negative access observation with an independent owner's state observation. OpenAPI supplies operation and schema structure; authorization expectations come from an explicit reviewed policy and cannot generally be inferred from schemas alone.

The current experiment supports detection capability for this controlled case. It does not show full dependency-graph coverage, superiority to other tools, prevalence in deployments or global novelty. Different orders and fresh IDs strengthen reproducibility but must remain grouped under one finding.

## Remaining qualification and next decision

Preserve the current evidence before further work. Complete environment identification, assess persistent state through authorized owner reads, and have the responsible maintainer validate the authorization boundary and failure atomicity in an isolated regression environment. Record clean-state acceptance separately; no reset/replay or minimal reproduction is claimed here. A successful owner read establishes persistence after the request, not persistence through a server restart.

Once this finding has a stable classification and remediation regression, move to a different mechanism: ownership and reference preservation across copying, or explicit permission-policy transitions with regular users. Avoid repeating the entire reference campaign merely to obtain another manifestation of the same error.

## Archive contents and integrity

campaign-original.zip is immutable original evidence; qualification.json is derived qualification; qualification_oracle.py and verify_campaign.py are frozen offline evaluators. checksums.json validates binary bytes exactly and text with LF normalization for Windows portability. HANDOFF.md records pending work. The save script verifies evidence before staging only the listed files and verifies the remote commit after an optional push. It sends no API requests.
