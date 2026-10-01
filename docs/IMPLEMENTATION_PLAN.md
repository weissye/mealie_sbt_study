# Implementation plan and acceptance gates

## Increment 1: implemented

The static compiler consumes the preserved OpenAPI document and an explicit Mealie profile. It emits three maps and a resource catalog. The catalog groups schema views, but does not merge runtime objects from similar names or UUID formats.

1. Data map: every schema and every explicit schema reference, with its field path.
2. Operation map: every HTTP operation, input/output schemas and candidate typed identifier bindings. A binding candidate is not yet a proven creation prerequisite.
3. Relationship map: reviewed relationship templates with provenance. Observed runtime instances and links start empty.

The RTV prototype records successful, explicitly sourced observations. A co-observed recipe ID and slug can identify one recipe. A User UUID and Food UUID remain different business identities even if their strings match. Scope, run and lifecycle are part of identity. Renaming an alias requires matching primary-ID evidence; deleting an instance makes related links stale until they are observed again.

## M1: accept the actual local environment

Run the preparation and read-only storage audit. Start the isolated pinned server or read the contract from an existing localhost server. Preserve the fetched contract and image digest. Review differences from the nightly reference; do not silently reuse incompatible profile bindings.

Next, accept intended actors, authentication, household/group scope and repeatable fixture setup. Keep credentials outside source control and evidence. Establish a documented cleanup/reset mechanism for this isolated project before repeated runs. The supplied scripts implement reachability and contract compilation only; authentication and reset acceptance are pending.

## M3: bounded payloads, actual RTV observations and individual stories

Implement operation-specific response extraction rules and payload adapters from the accepted contract. They must select valid union branches, respect required fields, and stop optional recursive expansion. Resolve input identifiers from the typed RTV instead of inventing IDs.

Create foods F1-F3, units Q1-Q2, categories C1-C2 and tags T1-T2 before creating recipes R1-R3. Attach ingredients and classifications through accepted API representations. Ingredient records are distinct occurrences: two recipes sharing F1 do not thereby share the same ingredient record. Then create lists L1-L2 and their item/recipe links. Associate units with concrete ingredient occurrences through the accepted payload adapter; the topology file currently lists units but does not prescribe this adapter.

| Recipe | Shared foods | Categories | Tags |
| --- | --- | --- | --- |
| R1 | F1, F3 | C1 | T1, T2 |
| R2 | F1, F2 | C1, C2 | T2 |
| R3 | F2, F3 | C2 | T1 |

L1 links R1 and R2; L2 links R2 and R3. R2 therefore has multiple list parents, and each list has multiple recipe children. Preserve list-level recipe links and item-level recipe provenance as separate relationship kinds.

Read each created resource back, register actual identifiers, and verify explicitly expected links. First accept each story alone: recipe read/edit/read; shopping-list link/read. Both initially use U1. Introduce U2 in the same household only after its scope and permissions have been accepted.

## Cycles and linear execution

Schema-reference cycles describe nested representations; they do not prove mandatory creation cycles. The reference contract has two recursive schema components, each involving recipe and ingredient views. Optional fields, explicit null alternatives and allowed empty arrays permit bounded payloads.

A cyclic resource graph can have a linear execution trace: create A; create B; attach A to B; attach B to A. This applies only when the API supports independent creation and those links. An indirect recipe cycle follows the same principle, with all endpoints created first. Begin with the acyclic reference R3 to R1; do not assume a complete cycle is supported. If the contract requires mutually unavailable parents and offers no accepted bootstrap operation, report a blocked dependency instead of guessing an identifier.

## M4: Provengo composition

After standalone acceptance, generate one behavior thread per story, plus scheduler constraints and a transport executor. Events carry actor, operation, typed arguments and symbolic references. The transport resolves symbols from the RTV immediately before dispatch. Responses update the RTV before the next request is selected.

Keep at most one HTTP request in flight initially. Provengo varies the interleaving of story steps while preserving each story's internal order and accepted prerequisites. Record the selected event sequence, fixture IDs, responses, contract hash and execution seed so an execution can be replayed. Explore a bounded set of schedules against a repeatable fixture state before increasing combinations. No Provengo CLI invocation is prescribed until the installed distribution and version are known; no executable behavior threads are included in this increment.

## M5: verdicts and completion

Separate transport/schema acceptance from documented business expectations. Do not assume that editing a recipe updates previously materialized shopping items. Establish expected outcomes for shared resources, link multiplicity and deletion effects before reporting semantic failures. A relationship that becomes stale after deletion requires a fresh observation; it is not automatically proof of cascading deletion.

Completion requires accepted fixtures, both standalone stories, reproducible schedules, actual relationship observations and a trace supporting every verdict. Static map compilation alone is not completion of a live pilot.
