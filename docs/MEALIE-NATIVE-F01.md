# Newly compiled native lifecycle model for F01

This delivery constructs new JavaScript from a declarative profile and a local
OpenAPI document. No historical story is copied, patched or replayed. It is the
first finding model in the rebuild, not a delivery of all five finding groups.

The existing installed `generator_v56` CLI generates an archived core baseline.
An optional generic lifecycle compiler then binds the supplied policy to that
contract and emits new native stories and interfaces. The core is not modified.
The compiler does not yet consume the core dependency plan to infer this policy:
actor assignment, dependency edges and arithmetic are explicit profile inputs.
This is a profile-driven generic extension, not a demonstration that an OpenAPI
contract alone discovers the reproduction or its business invariant.

## Behavioral architecture

Five lifecycle threads: food, unit, recipe, shopping list, quantity process.
Two independent dependency-collection threads remember readiness events without
requiring food-before-unit or list-before-recipe order. Eight verifier threads
perform independent GETs after their corresponding actions. Authentication,
a narrow action/readback guard and completion make three supporting threads
in total: 18 bthreads overall. Startup registration is part of the authentication
thread.

The guard blocks other modeled action-begin events between an action and its
verifier; it does not select the next entity. Native Provengo selects events.
All application HTTP is inside `interfaces.mealie.js` via RESTSession. Python
performs generation, CLI invocation and archive processing only. No simultaneous
HTTP dispatcher, external business-step bridge or coordinator is supplied.

This is a bounded creation/read/update composition. DELETE is intentionally absent
and all resources are retained. Do not describe the model as full CRUD coverage.

## Reproduction policy

Create one food and unit and two separate ingredient rows in one new recipe, each
quantity 2 and sharing those references. Create a new list. Add a manual quantity
13 using the same key. Add one whole recipe and verify total 17. Add half a recipe
and verify expected total 19 and recipe association quantity 1.5. The historical
F01 anchor was observed total 20. The arithmetic verifier aggregates every row
with the selected canonical food/unit identity; it does not assume row order.

The narrowed duplicate-key trigger is based on the research report's controls;
the earlier food merges and decrement prefix are not asserted to be necessary.
This model does not claim to reproduce the complete original discovery order.

Before every contribution, the preceding verifier stores freshly read recipe and
list states. The action guard and dependencies prevent another modeled mutation
from intervening. After each contribution, read the recipe and the list again.
A mismatch is a semantic candidate until the archived bodies are independently
qualified. Three observations are required for a nonreproduction pass.

Endpoint paths, success codes, the increment-field alias and writable recipe
fields are bound to the local contract before sampling. The deprecated single
recipe contribution endpoint is explicitly selected by the profile to keep the
scale binding unambiguous; absence stops compilation. This is not inferred API
selection. Other deployment versions require reviewed profile changes.

## Installation and execution

Extract this delta into the existing Mealie study root. It introduces new names
and does not replace the accepted distinct/merge extension or pinned core.

```
.\scripts\Run-Mealie-Native-F01.ps1 -GenerateOnly
.\scripts\Run-Mealie-Native-F01.ps1 -Username 'changeme@example.com'
```

The first command invokes the installed core and produces new JS with actual
local contract bindings, without authentication, sampling or live HTTP. The
second repeats generation into a fresh run, samples one native schedule, requires
symbolic completion and all verifier events, then replays once. Native CLI option
compatibility is checked through its installed help before sampling. No automatic
retry, database reset or cleanup occurs. Supply `-Jar` if required by the local
installation. Credentials are prompted, URL encoded and temporarily held in
environment variables, restored by the wrapper; selected log secrets are redacted
before archival. Inspect outputs before external publication.

`runs/native-f01-.../review.zip` includes the new model, selected schedule, local
OpenAPI and profile, native output, receipts and generation/acceptance reports.
The Save script preserves source only; newly produced live evidence must be
qualified and archived separately. Git synchronization does not restore Docker
state.

## Validation and limitations

The supplied tests exercise callbacks with a localhost HTTP fixture, two distinct
prerequisite orders, an injected fractional overcount and an injected association
error. Missing operations and ambiguous/missing scale fields stop generation.
These tests are not native Provengo execution or live Mealie reproduction.
Windows PowerShell and the user's actual pinned contract have not been executed
in the packaging environment. Only the synthetic schema supports the shipped
example JS. The example is visibly labeled and must not be used as a live model;
GenerateOnly creates the actual contract-bound files.

Native runtime serialization, installed CLI behavior, deployed schema compatibility
and F01 recurrence remain operator validation gates. F02/F03 compilation and the
recorded F04/F05 qualification are not delivered in this first delta.
