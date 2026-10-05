# Mealie copy: broken internal ingredient references

## Engineering finding

One distinct API reference-integrity defect was reproduced twice in Mealie
v3.28.0 with fresh resources. POST /api/recipes/{slug}/duplicate returned 201,
created new ingredient referenceId values, but retained an instruction reference
to the original recipe's ingredient. The returned copy and its subsequent GET
both contain the dangling reference. This differs from the earlier shopping-list
quantity defect; no source/copy content leakage was demonstrated here.

Reproduction 1: the source instruction references
b25645d8-a1f1-40da-a9fd-eca60a652600. Copied ingredient IDs are
1801656f-7d4f-4f91-9394-2b7a3ccc8f6f and
92537ab4-fbb3-4c1a-ace0-c3288d88ca26. The copied instruction still references
b25645d8-a1f1-40da-a9fd-eca60a652600, which is absent from the copy.

Reproduction 2: the source reference is
780e2798-a533-4d95-8d95-c21cf63cc6f7. Copied ingredient IDs are
0ea8398c-6b0d-49ff-8a49-3cc5d6b35db3 and
3ab3f68b-4938-44a5-9920-0337752a9a1f. The copied instruction retains the
source reference again.

The expected invariant is: every instruction ingredientReferences.referenceId
resolves within that recipe's recipeIngredient.referenceId set. Copying must
rewrite each internal reference using the old-to-new ingredient ID mapping,
while retaining external food/unit/recipe UUIDs. The minimal-reproductions.json
file preserves the actual duplicate request, raw response, source before-copy
read, first copy read, resource UUIDs and routes for both instances.

## Source corroboration and impact

The pinned duplicate_one implementation assigns fresh ingredient reference IDs
and instruction IDs without an explicit old-to-new ingredient-reference mapping
in that method. The API evidence independently proves the resulting broken
state; source inspection supports the likely cause, not a verified patch.

Pinned frontend RecipePageInstructions.vue lines 419 and 461 resolve references
against the current recipe's ingredient IDs. Lines 804-807 build that lookup.
Consequently the broken reference is expected to omit its associated ingredient
from the relevant instruction view. This UI consequence is inferred from pinned
code; the browser UI was not exercised in this campaign. Source URLs and file
hashes are recorded in provenance.json. Upstream issue novelty is unassessed.

## Oracle correction

Four original COPY_CANDIDATE results were false positives in the independent
validator. Its declared exclusion for recipeIngredient[].display did not run:
the root-membership check used recipeIngredient[] instead of recipeIngredient.
Updating a note legitimately changes its derived display string. The correction
removes [] from the root segment before applying the explicitly declared
exclusion. UUIDs, quantities, notes, instructions and references remain protected.

Requalification of the original raw responses yields six PASS runs and two
internal-reference candidates. Source-first and copy-first mutation runs showed
no extra protected-content change after the oracle correction. Original archives,
original classifications and original acceptance flags remain intact; corrected
classification is recorded separately. No live requests or reruns were needed
for this analysis. The regression test must also inject quantity and counterpart
note changes to ensure display exclusions do not hide actual faults.

## Research interpretation

The experiment used the generic OpenAPI compiler with explicit semantic profiles,
generated Provengo stories and interfaces, fresh owned bindings, long construction
prefixes, and two sampled schedules per profile. Copy semantics and internal
reference invariants were supplied as explicit policies, including a hypothesis
motivated by source inspection. This is not evidence that OpenAPI alone inferred
the business invariant, nor a comparison establishing superiority over other tools.

Two description controls and four nested-mutation runs qualify successfully.
The internal-reference profile reproduces one mechanism twice with distinct
source/copy/ingredient UUIDs. Count it as one defect with two reproductions.
Eight review checksums and 104 distinct owned identities were verified. The
independent validator defect illustrates why raw responses, matched controls,
and reviewer requalification are essential alongside a test oracle.

Limits: no exhaustive dependency-graph coverage, reset/replay, UI reproduction,
upstream novelty assessment, production deployment, or server patch verification.
All observations concern the pinned local server and configured protected fields.

## Next work

Freeze the original evidence, source correction and this report in Git. The
next targeted confirmation should create the smallest valid instruction-linked
recipe and copy it, plus a matched copy without internal references. This checks
whether complex external links are necessary for the defect. A subsequent
independent copy-of-copy or note-reference campaign can probe the related mapping
mechanism. Those are follow-up experiments, not additional discovered bugs.
