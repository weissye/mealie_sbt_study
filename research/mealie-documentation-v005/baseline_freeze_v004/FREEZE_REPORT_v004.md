# Mealie research baseline freeze v004

Stage 1 completed as a read-only source and input freeze on 9 October 2026. Current package baseline is v016, replacing the provisional v015 baseline. This freeze does not change the original source archive, regenerate boundary cases or perform another live run.

## Frozen source identity

Source archive: Mealie_F04_F05_Evidence_Package (1).zip.

SHA256: 924e363fdf399bd261e12cb89a4c8319c2f393ffd2849ba52a6548b0ffb4c378.

The package contains 416 actual files: 415 indexed files and the master manifest itself. All 415 master entries and all ten per-version evidence manifests verify. The v016 evidence manifest has 59 entries. The 416-file inventory records every original file's layer, size and byte hash. This sidecar records immutable source membership; the original ZIP remains the source store and is not rewritten or included a second time.

No Git commit identifying v016 was supplied. Its source ZIP hash and compiler/input hashes are the authoritative version identifiers for this freeze. A future Git commit may link these identical bytes; it must not be invented or substituted for the current pin. Earlier Git source snapshots are separate historical lineages, not the current v016 compiler source.

## Separation of responsibilities

| Layer | Authoritative source | Responsibility |
| --- | --- | --- |
| Package entrypoint | generator/generate_package_v016.py | Loads contract and declared plan, invokes the package writer |
| Compiler | generator/delta/generator_v56/boundary_plan_v016.py | Contract binding and model/package construction |
| Structural input | generator/contract/mealie-openapi.v3.28.0.live-v007.json | Recorded operation and schema contract |
| Semantic input | generator/plan_v016.py | Explicit test intent, actors and ordered steps |
| Package templates | generator/delta/generator_v56/package_templates_v016.json | Authored setup, orchestration, fixtures, checks, launcher and documentation |
| Outputs and evidence | Remaining generator outputs and evidence/v007 through evidence/v016 | Generated products, fixture results and existing live records |

The separation is documented without relocating or editing the compiler. An actual code refactor would change the baseline and require a new version. The source inventory deliberately distinguishes compiler files from authored inputs and templates, rather than treating every file under generator/ as generic engine logic.

v016 is a package-producing compiler for a declared Mealie plan. Freezing it does not prove that the earlier generic engine and this compiler are one unchanged engine, or that the compiler transfers unchanged to another service. The next phase must record reuse, adapter changes and engine changes independently.

## Integrated generation audit

The entrypoint calls write_full_package, which invokes model compilation and uses a compiler-owned template file for the surrounding package. All ten template-derived output files match the retained templates after the documented version-token substitution, byte for byte. The wrapper change is therefore integrated into the package writer, rather than being only an external post-generation edit in the supplied artifact.

This is a source and output correspondence check. Full regeneration of the active boundary package was not executed by this audit. The original statement that Claude regenerated it is a supplied report, not a newly reproduced result here. All ten Python files in the current generator directory passed AST syntax parsing without import or execution.

## Supplied semantic information ledger

The entrypoint itself identifies plan_v016.py as hand-authored test intent. The generated report identifies its semantics source as a curated plan, not inference from OpenAPI. The input ledger records hashes, ownership categories, named plan functions and the ten template-output names. Human modeling time and full authorship history remain unmeasured.

OpenAPI supplies structural bindings and documented request/response shapes. Actor selection, intended state comparisons and classification assumptions are declared semantic inputs. Templates supply orchestration behavior. Generating all deliverable files from these inputs establishes complete packaging integration, not autonomous invention of those inputs.

The proposed adapter input schema defines how future service bindings and invariants should declare provenance. It is a research input contract, not a claim that v016 already validates or consumes that schema.

## What authored semantic input means for the research

An authored test program can discover an unknown failure automatically. Supplying expected behavior before a run does not mean the observed bug was known. The current package integrates compilation and wrapper production; that is an engineering improvement even though its intent remains explicit input.

Retain this model when the claim is profile-driven automated detection. For a stronger scenario-generation claim, future authorized consistency workflows should be selected through frozen generic rules over contract structure and declared relationship/invariant metadata. For example, an update/readback rule can bind writable fields and the corresponding read operation while a documented invariant supplies the expected preserved fields. Record which parts are inferred and which are supplied, and evaluate on held-out workflows.

OpenAPI generally does not specify all arithmetic, copy, ownership or permission semantics. A complete contract-only semantic discovery claim cannot be established by moving a hard-coded plan into compiler source. Generic rule reuse, frozen inputs and an independent transfer evaluation are the relevant evidence. No compiler change is made as part of this freeze.

## Existing execution evidence acceptance

The v016 receipt reports V016_LIVE_BOUNDARY_RUN_COMPLETE, native exit zero, 15 generated steps and 15 markers. The archived compiler hash matches the supplied compiler. The report's contract hash matches the exact canonical-JSON serialization used by that compiler.

The contract file hash is 571cd5fe0220c8f15c081b6b8c1ac491de0dc1154fcf4864655bc11e28bf0e46. Its canonical JSON hash is 9aad8c0a7d9bdbff2b8dbe1675044a86ba8d674c145cb60351654452aa142286. Both are correct identifiers for different byte representations; they must not be compared as if they were the same representation.

The audit found zero raw JWT-pattern matches across the source files, including binary members. This limited scan does not prove absence of every possible password, personal identifier or secret format. No new server response or live acceptance is claimed.

## Documentation drift preserved as an issue

The top-level README still says 345 files in one paragraph and v015 in part of its layout description, while the manifest indexes 415 and the compiler is v016. START_HERE still says historical primary evidence is unavailable, although our separate prior v002 identity audits already recovered and correlated historical logs. These are documentation discrepancies. Original text is preserved; the current freeze metadata takes precedence for version and counts, and historical/new-run identity analysis remains in the earlier supervisor artifact.

No v016 server traceback matching the historical signatures was established in this freeze. Prior identity correlation of v014/v015 must not be silently transferred to v016 without checking its own corresponding logs.

## Stage 2 handoff and change control

Use this source identity, source-layer inventory and explicit semantic ledger as the starting point. Before moving to Vikunja, freeze one owned-resource workflow and document each operation/reference binding and invariant source through the proposed adapter schema. Record the unchanged compiler components, target adapter and every changed engine file separately. Validate authorized positive semantics and independent oracle fixtures before accepting a transfer result.

Do not hand-edit generated outputs to repair a model. A changed compiler, plan, template, contract or oracle creates a new source version and a new freeze; preserve old archive bytes and old results. A new source ZIP should fail this freeze's source-hash gate until it receives its own declared baseline. Publication to GitHub has not been performed by this stage.
