# Multi-identity scope campaign: engineering and research protocol

## Motivation

Earlier verified Mealie relationship campaigns used one authentication context. Multiple resource instances and logical actors did not establish multi-user coverage. The copied internal-reference defect remains one reproduced single-user defect. This campaign explores a distinct mechanism: context-sensitive ownership and authorization after nontrivial relationship construction.

## Design

Each fresh replay provisions two regular users and verifies their identities before creating recipes and shopping lists. The administrator participates only in fixture setup. A user's bearer token is selected explicitly at each generated HTTP site. Login contexts are not shared implicitly between actors.

The shared configuration constructs a valid cross-user recipe relationship, edits a source through the other user, copies it through that user, mutates source and copy independently, and adds the copy to the shared list. It checks copy ownership, stable identities, ingredient quantity/reference preservation, outgoing target preservation and both shopping-list recipe references. Non-owner recipe deletion must be rejected and the owner must still observe the protected source state.

The separate configuration constructs a recipe/list prefix for both users in distinct groups and households. Both users attempt foreign operations by known route/UUID. Every foreign copy, update and delete is followed by an owner GET; foreign recipe addition is followed by an own-list GET. Final owner reads protect identities, recipe content, ingredient UUIDs/quantities, list items and recipe references. These probes intentionally use known identifiers rather than relying on discovery lists hiding resources.

## Invariants and interpretation

1. Actor self identity and group/household mapping agree with the provisioned account; all elevated role flags are false.
2. Shared editing changes the intended description while preserving stable ownership and ingredient identities.
3. The duplicate belongs to its executing user, receives a new recipe UUID, and retains its outgoing recipe link.
4. Source and copy descriptions reflect their own intended writes, with protected ingredient fields unchanged.
5. Rejected operations preserve the owner-visible state, independently of the error code.
6. Foreign-scope operations do not expose or mutate the protected recipe/list.

A semantic mismatch yields a candidate, not an automatic bug count. Analysts must distinguish a permission-policy assumption error, a generator/oracle defect, an infrastructure failure and a server defect. The second native schedule supplies a fresh-resource reproduction attempt. The evidence identifies whether the same mechanism recurs; identical mechanisms under several orders count as one defect.

## Threats to validity

This is not full dependency-graph or permission-matrix coverage. In particular, same-user independent logins, different households within one group, locked recipes, invitation roles and public/share links are not covered. Data is not reset between replays; fresh names and IDs isolate each run. Browser consequences, upstream novelty and a corrected server implementation are not tested here. Independent mock tests validate generated transport and oracle sensitivity but cannot establish actual Mealie behavior.

## Preservation

The live ZIP contains model source, native samples, sampled task orders, model hashes, actor-attributed raw observations and per-run classifications. It contains no usable bearer tokens or passwords. Windows account-bound fixture credentials are retained locally outside the repository for follow-up reads. Preserve each completed campaign under `evidence/multi-identity-<timestamp>/` with a SHA256 before committing findings. Do not count confirmation of the existing copy internal-reference defect as a new defect.
