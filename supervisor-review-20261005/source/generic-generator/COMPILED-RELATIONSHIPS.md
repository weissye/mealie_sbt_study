# Compiled relationships: additive generator increment

## What changes

The optional relationship compiler now consumes the resource catalog, operation
map and relationship blueprint and emits executable Provengo actors. The
previous review-only blueprint is replaced only when `--compile-relationships`
is explicitly selected. Without that flag, existing interfaces, stories,
reports and CLI profiles retain their previous behavior.

All HTTP calls, body projections, authentication, response checks and runtime
identity bindings are generated in `interfaces.*.js`. `stories.*.js` contains
bootstrap, logical actors and scheduling constraints, and calls interface
functions. It has no direct HTTP calls. No handwritten Mealie story is used.

The compiler itself uses contract operations, typed resources, response schemas
and an external scope/runtime configuration. Application names and exceptional
API knowledge belong in the profiles, not in the generic algorithm. OpenAPI
cannot establish every business effect: observed action effects and otherwise
undocumented creation responses require explicit evidence configuration.
The Mealie runtime profile pins the exact previously accepted local contract
SHA-256 and cites the successful uploaded fixture review ZIP SHA-256.

## Current pilot

Seven resource types have three owned instances each: foods, units, recipes,
categories, tags, shopping lists and shopping items. There are 54 tasks: 21
creates, 27 relationship writes and six qualified recipe-to-list actions.
Two recipes share ingredient foods/units and category/tag targets; each of
three lists is linked to two recipes, with overlapping recipe membership.
Shopping items retain their own creation parent list.

Each task has three sequential HTTP requests: prepare, write/create, read back.
Authentication, three bootstrap reads and final completion validation bring
the complete schedule to 167 responses. Twenty-one logical actors can be
interleaved subject to prerequisites. Only one task is admitted at a time;
this pilot does not seek requests overlapping in wall-clock time.

Recipe slug routing and recipe UUID links are separate views of the same
coobserved instance. Captured values are scoped by resource/instance, not
merged merely because identifiers have the same UUID shape. Scope checks
compare the user, group and household bootstrap identities.

Recursive recipe relationships are attached after their endpoint resources
exist. This gives a linear execution even when the resulting resource graph
contains cycles. A genuine required creation/execution dependency cycle is
rejected rather than guessed away.

## Evidence boundaries

Local checks cover legacy generation, transport equivalence, deterministic
compilation, two distinct generated schedule orders, and callback rejection
of identity drift, ambiguous creation, inconsistent scope and failed link
readback. The Node scheduler and REST server are test doubles. They do not
constitute native Provengo or real Mealie acceptance.

Native sampling uses three random schedules rather than enumerating the huge
interleaving space. The sample auditor requires all task prerequisites,
matching task ownership and a final complete event in every sampled schedule.
Samples are offline; none of their HTTP requests are executed.

Live replay runs one sampled native schedule. A zero process exit code alone
cannot pass acceptance. The runner also requires the runtime receipt proving
all 54 task readbacks, all 167 responses and all 21 owned creations completed.
If native output does not expose that receipt, the result is explicitly
inconclusive. Review archives contain the generated files and sanitized
execution evidence. Password input uses the process environment and is cleared
by the wrapper when it returns.

There is no automatic deletion, retry, rollback or full server reset/replay.
Each live replay creates new owned resources. On partial failure the review
report is retained; do not replay repeatedly as a substitute for diagnosis.
The callback projector implements common request schema constraints, not a
complete JSON Schema validator. Relationship readbacks check the written
memberships at their task boundary; global persistence after every later
mutation, delete semantics and exhaustive schedule coverage remain future work.

## Windows workflow

Extract the delta into the existing study folder. Run compatibility checks,
then generate with both scope and runtime profiles:

```powershell
& .\scripts\Test-Generic-Generator-Compatibility.ps1
& .\scripts\Prepare-Generic-Provengo-Model.ps1 `
    -OpenApi '.\generic-generator\compatibility\contracts\mealie.json' `
    -Name 'mealie' -BaseUrl 'http://127.0.0.1:9925' `
    -ResourceMaps -CompileRelationships `
    -RelationshipProfile '.\generic-generator\profiles\mealie-relational-map-pilot.json' `
    -RelationshipRuntime '.\generic-generator\profiles\mealie-relational-runtime.json'
```

The combined `Run-Generic-Relationship-Pilot.ps1 -Username
'changeme@example.com'` performs compatibility checks, generation, sampling and
one live replay, stopping on failure. Add `-SampleOnly` to stop after offline
sampling. It identifies the newly generated project rather than selecting an
older directory. Separate steps remain available below.

Use the exact generated project path printed by generation:

```powershell
$project = 'C:\work\temp\mealie_sbt_study\provengo\generic-mealie-REPLACE_WITH_PRINTED_ID'
& .\scripts\Sample-Generic-Relationship-Model.ps1 -Project $project -Size 3
& .\scripts\Invoke-Generic-Relationship-Scenario.ps1 `
    -Project $project -Username 'changeme@example.com' -SampleId 1
```

Sampling review: `Downloads\generic_relationship_sampling_review.zip`.
Live review: `Downloads\generic_relationship_live_review.zip`.
If sampling is rejected, inspect its report before live replay; live replay
requires matching accepted native samples. Provengo and Docker/Mealie must be
available on the Windows computer. The scripts are supplied for Windows;
native Provengo and PowerShell execution have not been performed in this build.

## Next increments

1. Validate native sampling and the first native live replay on the existing
   local server; correct protocol/projection details based on captured evidence.
2. Add a final whole-graph readback to verify preservation of earlier links,
   including ingredient pairings and both memberships for every shopping list.
3. Add interface-driven mutations/deletes and explicit expected effects, with
   typed binding invalidation and restoration requirements.
4. Establish owned-fixture cleanup and deterministic reset/replay acceptance.
5. Expand generic contract/profile coverage beyond this pilot without changing
   the default legacy generation path.
