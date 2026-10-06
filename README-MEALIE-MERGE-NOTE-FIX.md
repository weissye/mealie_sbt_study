# Native merge note multiplicity repair

This small code delta applies to the installed native distinct/merge release from commit `d3d5c752a40270d79f505f1fff3ba6682099c4f1`. Its size is mostly the unchanged original failed-merge evidence archive.

## Qualification

The archived merge run reached 40 HTTP calls and captured 39 business responses. Its addition response retained the item UUID and list/food/unit bindings and returned quantity 3 after adding 2 to 1. Both notes were present in the opposite order from the oracle's assumed concatenation. That order had not been established by OpenAPI. Independent post-merge GETs were never reached. This is a qualified note-order oracle false positive, not a confirmed new application bug.

## Repair

An additive wrapper around the existing `render_native_distinct_merge.render` transforms only the three merge note comparisons: addition response, independent item GET, and independent list GET. A pure JavaScript helper compares exact note components as a sorted multiset. It does not trim or deduplicate: missing, duplicated, extra or modified components fail. The separator and order-independent policy are explicit in the experiment profile; these semantics are not inferred from OpenAPI.

Quantity, identity, direct/embedded dependencies, collection cardinality and unrelated-item checks remain intact. No business requests move out of interfaces, no Python business workflow is introduced, and the existing native bthread scheduling/readback barriers remain unchanged. This does not introduce a simultaneous HTTP dispatcher.

## Installation, saving and replay

Extract over the existing study root. The save script verifies the delta and original evidence before patching. The installer checks the existing renderer/profile against their release checksums, preserves their original bytes under a timestamped `runs/merge-note-source-backup-*` directory, appends the wrapper, adds the explicit note policy, and updates the corresponding source checksums in the existing release manifest. Repeating installation is idempotent; incompatible files stop before patching.

The save script runs regression checks and the installed renderer/release checks, then commits only listed paths. `-Push` verifies that the named remote branch equals local HEAD. It includes this failed merge archive and qualification; it does not automatically archive the earlier successful distinct-control run or future live results.

```powershell
& .\scripts\Save-Mealie-Merge-Note-Fix.ps1 -Root $root -Push
& .\scripts\Test-Mealie-Merge-Note-Fix.ps1 -Root $root -Username 'changeme@example.com'
```

The replay wrapper requests `-Scenario Merge` only. It creates a fresh merge experiment with its necessary baseline resources; it does not rerun the separate accepted distinct-control experiment. It performs one native live schedule, asks for the password, retains all resources and stops on failure without retry or cleanup. Expected success is `NATIVE_DISTINCT_MERGE_PASS`; preserve the printed review archive for independent qualification.

## Local validation and limits

Six Python regression tests pass, including an optional Node test exercising eleven cases against the actual generated callbacks from the archived run. Local RTV/HTTP stubs supply response bodies: both note orders pass; missing, duplicate and extra notes fail; wrong quantity or food binding fail; incorrect persisted state, parent collection state and unrelated-item quantity fail. These are local callback tests, not native Provengo replay or live Mealie verification. The original native control flow is unchanged; the corrected live schedule still needs to run on the user's server.

Node is optional on the user's machine. When unavailable, the archived JavaScript regression test is explicitly skipped; the remaining Python tests and existing installed renderer/release tests still run. PowerShell itself was reviewed but could not be executed in the local Linux validation environment.

The exact component experiment uses generated markers without the separator inside either input note. General arbitrary-note delimiter semantics and exhaustive scheduling coverage are outside this bounded test.
