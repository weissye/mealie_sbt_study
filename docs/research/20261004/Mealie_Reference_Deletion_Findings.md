# Mealie reference deletion qualification: engineering and research record

Date: 2026-10-04. Mealie: v3.28.0. Generator seed: 526803.

## Result

Eight native Provengo replays passed the generated callbacks and independent
receipt validation. The campaign observed 804 HTTP responses and 96 disjoint
owned resource identities. Each of the four pairs completed distinct task
orders. No new server defect was established in this tested scope.

| Case | Accepted replays | Requests per replay | Outcome |
|---|---:|---:|---|
| Food control | 2/2 | 100 | No deletion; update and rebind passed |
| Unit control | 2/2 | 100 | No deletion; update and rebind passed |
| Referenced food deletion | 2/2 | 101 | DELETE 200; target GET 404 twice |
| Referenced unit deletion | 2/2 | 101 | DELETE 200; target GET 404 twice |

For successful deletion, referring nullable food/unit fields became null.
Protected ingredient data, companion relationships, an unrelated recipe,
and existing shopping-list recipe associations matched their expected views.
The first surviving recipe was subsequently updated and rebound to another
live target; deferred recipe/list associations then completed successfully.
These observations qualify the configured null-reference deletion policy in
these contexts. They do not prove all deletion paths correct.

## Earlier control stop and engineering corrections

The first campaign stopped in its no-delete food control. Its sole mismatch
was `recipeIngredient[0].display`: the server correctly rendered the newly
bound food name, while the oracle expected the previous display text. No
DELETE request was selected in that campaign. It is an oracle false positive,
not another server bug. The original review is retained separately.

The generic profile now explicitly declares the derived display path excluded
from protected equality. Identity, quantity, note and relationship structure
remain checked. A regression reproduces the old failure against a healthy
fixture. Native tests preserve detection of dangling references, unrelated
mutation, partial writes on rejection, ignored updates and ignored rebinds.

The Windows runner now uses a 512 MiB Java heap, with a 1024 MiB free-memory
preflight. This setting completed the uploaded live campaign. Compatibility
checks and 466 transport argument/callback comparisons passed on the user's
machine. Ten native-only tests were skipped by that compatibility invocation;
separate development-side native reference tests were executed.

## Provenance and limits

Original accepted campaign SHA-256:
`d4cf480c916bc04b35e6eddbfac2a3da1892451af767f4984cc027d8389cab0d`.

Original stopped control campaign SHA-256:
`e23ef16382df8694fdbd7c4b4bf025521a3ea608dc6d11f54815f364c453f2d2`.

Review files retain generated models, sampling audits, redacted native logs,
and callback receipts as supplied. Large serialized samples are omitted by
review bundling; their original project files and audited hashes remain on
the workstation. No packet capture, database snapshot, full reset/replay or
internal-source root-cause analysis is claimed. No simultaneous HTTP calls
were introduced. These are sequential schedules of composed stories.

The previous quantity-consistency discrepancy family remains a separate
finding. These successful deletion controls neither refute nor reproduce it.

## Next mechanism

Use a snapshot captured before a shared target deletion as the basis of a
later write to a surviving recipe. Change an independent field in that stale
snapshot and interleave reads and later associations. Qualify whether the API
rejects the stale identity or intentionally reconstructs a target. On rejection,
verify unchanged source and unrelated controls. On success, verify referential
integrity and the resulting live target identity; do not treat documented
inline creation as a bug. Investigate partial writes, persistent dangling
references and 5xx responses with fresh-resource confirmation.

This next stale-snapshot mechanism has not yet been implemented or executed.
