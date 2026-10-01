# Generated-event standalone backend: increment 1.8

This increment adds live functional execution while preserving the accepted generator and its separated stories/interfaces. The backend consumes the operation/scenario IR and exact events from the accepted Provengo sample. It projects each story into its own ordered standalone trace, executes it once, and checks restoration before the next story.

It is a replay bridge for standalone acceptance. It does not execute all 70 interleavings, run a REST executor inside the Provengo engine, or establish a full fixture reset protocol. The original sampled JavaScript stays symbolic and preserves its source meaning.

## Boundaries

| File | Responsibility |
| --- | --- |
| `src/sbt_generator/runtime.py` | Validate sampled source/IR and exhaustive coverage; resolve fresh typed bindings; dispatch through an exact owned-operation allowlist |
| `src/sbt_generator/json_payload.py` | Resolve local schema references and project existing values into accepted JSON request schemas |
| `src/mealie_runtime_adapters.py` | Reviewed Mealie payload choices, baseline preconditions, business oracles, relationship observation refresh |
| `src/run_mealie_standalone.py` | Select each generated story's sampled events, orchestrate execution and restoration checks, collect evidence |
| `scripts/Accept-Mealie-Standalone-Stories.ps1` | Interactive Windows launch and review ZIP packaging |

Scheduling does not contain raw endpoint calls. The selected event supplies an operation identity; the interface reads its method/path from operation IR and substitutes identifiers from current RTV observations. The Mealie adapter explicitly owns fixture-specific business expectations and request value choices. Adding another application requires an accepted adapter/profile; this increment does not claim automatic business-oracle inference.

## Execution

1. Validate the most recently sampled `provengo/offline-*` project against current contract, profile, emitted JavaScript and IR. Validate all 70 unique complete eight-event samples and the referenced accepted fixture evidence.
2. Read `/openapi.json` without credentials and require the pinned reviewed SHA256. Authenticate with hidden password input, then confirm user/group/household against accepted identity evidence. No credentials or tokens are persisted.
3. Read all fourteen owned base resources. Construct fresh typed RTV observations and accept the expected recipe/classification/list topology and one-copy quantities. Reject edited shopping-item fields that the selected remove/re-add protocol cannot preserve.
4. Replay A1-A4: read R2, update its description with a run marker, independently read/verify, restore its captured description. Read all fourteen resources again and compare selected semantic state with the baseline.
5. Replay B1-B4: remove R2 from L1, independently verify absence at list and item provenance levels, confirm other recipe contributions remain and L2 is unchanged, re-add one copy, independently verify L1. Read all fourteen resources again and compare selected semantic state with the baseline.
6. Refresh nested ingredient/item/link observations from current GET responses. Retain superseded observations as stale rather than merging regenerated identifiers or claiming global deletion.

Successful execution uses 51 fixture requests: 47 GETs, two recipe PUTs, and two owned link POSTs. Together with one public contract GET and four authentication/identity requests, the total is 56 HTTP requests. There is one request in flight, no automatic retry, and no automatic rollback after failure. The existing fixture transport enforces a 64-fixture-request cap; the adapter further restricts exact methods/paths.

## Request and response limits

The request projector supports local references, nullable unions, object properties, arrays, required fields, enums, selected numeric/string/array bounds and UUID formats. It rejects unsupported allOf request projection and limits recursive depth. It preserves documented unconstrained extras but removes output-only or undocumented named fields during object projection. It is not a complete JSON Schema validator; pattern/date formats and the full constraint vocabulary are not accepted as validated by this increment.

Response acceptance includes the reviewed HTTP 200 status, bounded JSON size and the explicit resource/scope/business checks. Complete response-schema validation remains pending and is recorded as false.

Restoration covers projected editable recipe content, non-time resource content, shopping quantities, food/unit IDs, selected item fields, and recipe provenance. Timestamps and generated shopping-item/link IDs are excluded. Position must be zero and item annotations/default fields unchanged at baseline for the current restoration protocol. This is semantic restoration of the selected pilot state, not an exact database snapshot or a full reset/replay guarantee.

If an HTTP or oracle check fails, the program stops and writes the completed/partial trace and checkpoints. State may be partially changed. Inspect that review ZIP before retrying; do not assume the failure path restored the baseline.

## Run and evidence

Extract the delta into the existing project; do not recreate the fixture or re-sample the accepted 1.7 model. Run `scripts/Accept-Mealie-Standalone-Stories.ps1 -Username 'changeme@example.com'`. Optional `-Project` selects an explicit existing `provengo/offline-*` directory.

The review ZIP is `Downloads/mealie_standalone_review.zip`. It contains `acceptance.json`, `trace.json`, `executed-events.json`, `checkpoints.json`, and refreshed `rtv.json`. The expected successful result is `M4_STANDALONE_RESTORATION_ACCEPTANCE_PASS`. This remains a prospective result until the user's local server run passes.

After live acceptance, the next gate is an accepted reset protocol and fresh binding handoff before composed replay. Existing static sampled bindings must not be treated as current identifiers for recreated shopping items or links.
