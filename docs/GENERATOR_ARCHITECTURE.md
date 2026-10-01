# OpenAPI-driven generator: increment 1.7

The pilot uses the same boundaries intended for the final generator. This increment replaces hand-authored step sequences inside the Python preparation script with a contract parser, operation/schema IR, reusable scenario templates, a declarative pilot profile, and separate JavaScript renderers.

## Sources and outputs

| Layer | Source | Responsibility |
| --- | --- | --- |
| Contract parser | `src/sbt_generator/parsing/` | Resolve references, preserve cycles, normalize operations and schemas |
| Scenario compiler | `src/sbt_generator/pipeline.py` | Select documented operation identities, expand templates, validate path bindings |
| Pilot policy | `profiles/mealie-pilot.json` | Select operation roles, actors, owned symbols, business types and oracle intent |
| Operation IR | `operations-ir.json` | All 266 operations: parameters, bodies, response schemas/codes, security and source pointers |
| Schema IR | `schemas-ir.json` | All 255 normalized schemas, including bounded recursive reference markers |
| Scenario IR | `scenario-ir.json` | Generated ordered steps, typed symbolic bindings and oracle intent |
| Interfaces | `spec/js/00_interfaces.js` | Selected operation metadata and the symbolic invocation backend |
| Stories | `spec/js/10_stories.js` | Behavior threads calling operation interfaces; no URLs or HTTP methods |
| Model preparation | `src/prepare_provengo_model.py` | Validate the accepted contract and observed RTV identities, generate an isolated project |

The parser files are reused unchanged from the previous local tree: `review56/keycloak-pilot-v56/generator_v56/parsing/{loader,normalize,model}.py`. The earlier entity-inference and live execution layers have not been imported or accepted for Mealie by this increment.

## What is generated and what must be supplied

HTTP methods, URL templates, parameter schemas, request variants, responses and security come from OpenAPI. The profile refers to operation IDs, not duplicated HTTP paths. Reusable templates produce the step order; neither the preparation script nor the emitted story file hard-codes that order as Mealie endpoint calls.

The contract alone does not specify which owned recipe to use, whether two field names refer to one business identity, desired business effects, or reset semantics. Those remain explicit reviewed policy and observed RTV evidence. The profile records oracle intent; this backend does not execute those oracles yet. Automatic operation-role discovery and dependency-based fixture generation remain separate future work.

The two current templates are `read_update_verify_restore` and `remove_verify_add_verify`. Another owned recipe can use the same template by adding a profile entry with new symbols and a unique step prefix. New behavior patterns require a new reusable template, with its preconditions and oracle acceptance, rather than ad hoc HTTP calls in stories.

## Transport and runtime boundary

The interface backend emits symbolic `SBT:Step` events. It performs no network requests and does not claim live request/response validation. Its catalog contains only the five selected operation interfaces; the full contract remains available in operation IR. Files use a `00_` / `10_` naming convention and interfaces expose a global loaded before behavior-thread invocation. Actual compatibility with the installed Provengo distribution must be confirmed by the supplied sampling command.

The future live backend must consume the same operation/scenario IR, resolve symbols from fresh typed RTV observations just before dispatch, use accepted payload adapters, capture responses, refresh identifiers and relationship observations, and publish completion outcomes to story logic. Payload generation, transport, oracle evaluation and reset/replay must stay separate. Adding a REST summon directive alone is not a live implementation.

## Acceptance and next gates

1. Contract normalization and profile validation, including missing operations and unmatched path parameters.
2. Generated JavaScript syntax and interface/story event wiring.
3. Installed Provengo sampling of the newly generated separated model.
4. Implementation and isolated acceptance of each functional story, its payload adapter and its restoration oracle.
5. Accepted fixture reset plus RTV refresh and replay, then bounded composition through the live backend.

The uploaded previous model has 70 unique complete eight-event schedules preserving both four-step story orders. That confirms its symbolic coverage, not the new file layout's installed-CLI compatibility or live restoration. Exhaustive order enumeration is capped at 10,000 schedules; larger profiles require bounded sampling and explicit coverage accounting.

## Usage

Run `scripts/Prepare-Mealie-Provengo-Model.ps1 -Sample` after extracting this delta. It generates a new `provengo/offline-*` directory and packages its source, IR, bindings, sample output and readiness report into `Downloads/mealie_provengo_model_review.zip`. Existing fixture data is reused without server requests. Existing generated projects are preserved for comparison.
