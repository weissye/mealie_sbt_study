# Mealie Context generator — review build

Status: **generated and unit-tested; no native Provengo or Mealie execution**.
This is an isolated extension of the uploaded generator_v56 archive, version
0.26.19-parallel-crud.3. It adds the `context-generate` command; it does not
replace the existing rendering profiles or install over an existing study.

## Inputs and reproduction

- Uploaded generator archive: generator_v56(1).zip.
- Uploaded reference: spec(6).zip, Library model's stories/interfaces/DAL.
- Uploaded local contract: Mealie v3.28.0, SHA256
  `90e19aa713ab4ba15352627aca7dc37290f868b213eb65a3e1564f3b7a7ff292`.
- The contract is copied byte-for-byte under model/.
- Endpoint scope is a test-selection input. It contains no quantity rules.
- The renderer has no branches keyed to Mealie or to its resource names.

The delivered archive's cli.py/pipeline.py baseline hashes differ from the
hashes previously printed from the work PC. The uploaded archive is the
explicit baseline for this build. Never overlay this entire package onto the
installed generator; reconcile source versions before integrating its two-file
extension (cli.py and render/context_model.py).

## Generated structure

| File | Responsibility |
|---|---|
| generated/spec/js/stories.mealie.js | One lifecycle bthread per entity instance, separate embedded-linking process, Context-triggered verifiers and resource guards |
| generated/spec/js/interfaces.mealie.js | Named action functions, native REST events, EventSets, transport metadata extraction, closure-free runtime callbacks, RTV identity mapping |
| generated/spec/js/dal.js | Context entities, expected projections, effects, queries and dependency-readiness helpers |
| generated/spec/js/generation_report.json | Contract hash, endpoint/schema derivations, identity hypotheses, coverage limits and execution status |

The default generated model contains five entity instances: food, unit, recipe,
shopping list and shopping item. A separate process attaches two ingredient
objects to the recipe, sharing its selected food and unit. The shopping item
waits for all inferred dependencies (including the selected recipe). Their
creation order is not predetermined. Its optional reference is exercised as a
request/read preservation hypothesis, not as a proven business policy.

Each producer requests creation, waits for its separate readback verifier,
requests a scalar update and waits for independent readback. Verification is
activated through Context queries. The embedded linking process performs a
separate write and readback. Two instances per entity can also be generated;
merge/collision semantics are deliberately not classified by this build.

No synthetic HTTP execution dispatcher or simultaneous-request coordinator is
used. The interface helper constructs native REST events, like the provided
reference's buildRestEvent/requestOneOfDirect. Provengo chooses event order.
ModelWriteBegin and ModelVerified are synchronization facts, not HTTP actions.

## Expected state and runtime observations

The DAL records values derived from selected requests. It does not learn an
expected quantity by copying a server response. Runtime callbacks retain real
IDs/route locators separately. Independent GET callbacks compare the expected
projection against the actual state and check stable identity.

For PUT, a pre-write GET supplies documented writable fields, including required
owner fields, that the test is not changing. A resource-specific guard protects
preparation, write and independent readback from another modeled mutation that
affects that resource. Unrelated resources can still interleave. This prevents
a stale test PUT from erasing a newly created child. These snapshots are input
carry data, not the expected value of the changed field.

The string returned by recipe creation is treated as a route-locator hypothesis
and checked by a detail GET. A wrapped item-create response must contain exactly
one candidate across schema-compatible arrays. Ambiguity stops execution;
coalesced identities are not silently treated as independent new resources.

## Important limits

This is a first Context implementation, **not the five-bug reproduction suite**.

- The generated lifecycles currently cover create/read/update/readback. DELETE
  is not emitted: this contract does not explicitly specify an absent-detail
  response, and linked-delete semantics need a supported oracle.
- Contribution, merge and copy actions require transition semantics. OpenAPI
  request/response types do not determine their quantity algebra or isolation
  rules. Updating a DAL requires a transition function; introducing a DAL does
  not supply that function automatically. This build does not claim otherwise.
- No fixed expected result such as 19 is embedded. Quantity checks here compare
  explicitly written ingredient quantities with readback quantities only.
- Nested arrays are currently compared positionally. Reordering may create an
  oracle candidate that needs qualification, not a confirmed application bug.
- Schema/title/key conventions are generic inferences, not logical consequences
  of OpenAPI. They are documented, and route/identity ambiguity fails generation.
- This is a bounded scope, not coverage of the entire dependency graph.
- Authentication uses an existing bearer-token RTV `SBT_AUTH_TOKEN`. No password,
  credential file or multi-account provisioning is bundled.
- The sample ZIP did not include Context bootstrap/config or lib/utils.js.
  This implementation supplies its own boundary helpers, but **does not emulate
  the ctx runtime**. A genuine Context-enabled Provengo project is required.

## Local generation (Windows PowerShell)

Extract into a new review folder. In that folder run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& .\scripts\Test-Mealie-Context-Offline.ps1
& .\scripts\Generate-Mealie-Context.ps1
```

Requirements: Python 3 with the existing generator's parsing dependencies
(including PyYAML if used) and Node.js for local callback tests. Generation does
not contact Mealie. The generation script uses a new folder and a fresh seed;
all resulting JS paths are printed. The pinned contract is byte-verified;
line-ending differences are not silently accepted.

`-Instances 2` expands entity instances. It does not confirm merge correctness.

## Native acceptance required before SUT testing

Use the real Context bootstrap and loading configuration from the working
reference project. Check loading of interfaces, DAL and stories, actual Context
query activation after effects, completion of every lifecycle, and a sampled
trace showing each item POST after every required parent readback. No Node
scheduler audit is native evidence. Before live replay initialize the token RTV
through a supported authentication action or existing runtime setup, and use
fresh generation inputs and owned fixtures.

The current script intentionally performs generation only. A native launcher
will be added once the working reference's Context/configuration files are
available; no unverified launcher is presented as ready for SUT replay.

## Validation performed

Five Python regression tests passed, covering the real contract's four item
dependencies, byte-reproducible generation for one and two instances, JS syntax,
ambiguous route rejection, another resource vocabulary, and overwrite refusal.

The Node callback/DAL unit audit passed 35 checks, including 24 parent-readiness
orders, expected/observed separation, injected identity/value/nested quantity
faults, nested RTV resolution and affected-parent write guards. It is an
explicit unit harness, not a replacement for Provengo and not shipped as a
scenario runner.

No SUT requests, native sampling, cleanup, Git commit or push were performed.
