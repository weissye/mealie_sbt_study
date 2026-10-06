# Native Context F01 contribution experiment

## Purpose and status

This opt-in extension continues the user-supplied generator_v56. It generates
new stories, a shared interface and a Context DAL from the pinned Mealie v3.28.0
OpenAPI. The preceding native Mealie run, seed 767471548, passed dependency-chain
acceptance with 29 HTTP requests. Its source is frozen separately from this change.
**F01 has not yet been reproduced against Mealie by this release.**

The local validation uses the actual Provengo 0.7.5-SNAPSHOT engine against an HTTP
fixture, with positive and deliberately corrupted results. It does not stand in
for a Mealie run. No Python tool selects or executes the live business sequence.

## Generated processes

1. Independent Food, Unit, Recipe and Shopping List lifecycle bthreads create,
   independently read, update and independently read each owned entity.
2. A separate linking bthread waits for source prerequisites, then installs two
   ingredients sharing the same food/unit, and verifies the linked recipe.
3. The contribution bthread waits for the recipe's verified linked revision 3 and
   the list's verified revision 2. It contributes the stored recipe once at scale
   1, then again at scale 0.5, waiting for verified observations between actions.
4. A separate Context-activated child/relationship verifier examines each response
   and requests item GET, list GET, recipe GET and a final list GET. Semantic
   mismatches are accumulated until these observations complete, then fail the run.
   Native transport/setup errors can still stop actuation earlier.

The item is produced by the contribution action, rather than by an unrelated
item POST. Each contribution updates a Context ledger from model inputs. All HTTP,
including authentication and observations, resides in the shared interface.
There is no simultaneous HTTP coordinator, cleanup, mutation retry or reset.

## Expected state and limits of inference

Ingredient fixture quantities 2 and 4 are schema-valid generated test inputs.
The DAL calculates sum(ingredient.quantity * contribution increment), accumulated
across selected contributions. It does not store a fixed expected final quantity,
learn expected quantities from responses, or overwrite expected state on reads.

The compiler discovers the action from its Add summary, array request body,
source foreign key, numeric increment field, container response and referenced
child schemas. Ambiguity is rejected. `generation_report.json` records pointers.
Numeric conventions also identify quantity and reference-scale fields.

The mathematical transition remains a **generic test hypothesis**, not a theorem
specified by OpenAPI. A valid JSON schema does not by itself establish merging or
quantity arithmetic. List source references are expected to accumulate increments;
item reference quantity multiplied by its scale is checked against the DAL quantity.
No particular normalization of those two item fields is imposed. Stable item and
reference identities, dependency keys, ownership and source preservation are checked.

A failing result is `F01_SEMANTIC_CANDIDATE`, requiring qualification against the
intended API semantics and historical F01 evidence. It is not automatically a new
confirmed defect, nor proof that the historical five findings were reconstructed.

## Installation and use

Extract Mealie_Context_F01_Delta.zip into a new folder. Run its
`Install-Mealie-Context-F01.ps1 -Root <existing isolated mealie-context-live package>`.
The installer accepts the frozen baseline or already-installed source, checks
checksums and backs up files. Do not point it at the main study repository root.

First archive and commit the verified baseline plus this source:

    .\scripts\Save-Mealie-Context-F01.ps1 -Root <package> -Repository <study checkout> -AcceptedProject <verified native project> -Push

The save tool regenerates the accepted JS using the frozen old generator, compares
its three JS files and reviewed snapshots, then archives a bounded source tree and
exact accepted spec/config under `research/native-context-f01-20261006`.
It commits only that path and verifies remote HEAD after push. No force push occurs.
It does not call the SUT. Credential-bearing original logs remain local; parsed
independent snapshots and the original log hash are archived.

Then run the new generator-produced experiment:

    .\scripts\Run-Mealie-Context-F01.ps1 -Root <package> -Username changeme@example.com

Use `-GenerateOnly` for source review without authentication or SUT requests.
Each execution generates a fresh project and fixture names. The native log remains
local. `qualification.json` and `review.zip` retain callback response bodies and
expected ledger state without auth request/token logs. Upload that review ZIP for
analysis. A nonzero native exit preserves evidence and stops without retry.

`F01Completed` is a symbolic event: native success and both qualified stages are
also required for acceptance, because Provengo can continue selecting events in
its fail mode without actuating subsequent HTTP.

## Reproduction and provenance

CLI: `python -B -m generator_v56 context-generate ... --contribution`.
Omitting this flag preserves the existing Context acceptance model.
The source contract SHA256 is
`90e19aa713ab4ba15352627aca7dc37290f868b213eb65a3e1564f3b7a7ff292`.
The preview uses seed 20261006; live runs choose new fixture seeds.
Native fixture validation is reproducible with
`tests/test_contribution_native.py --jar <Provengo jar> --output <new directory>`;
add `--fault quantity`, `reference`, `identity` or `duplicate` for corruption checks.
All fixture failures must retain four real observation GETs after the second POST.

The original historical five-bug report and minimal evidence are still needed to
claim exact equivalence between this experiment and the original F01 trigger.
