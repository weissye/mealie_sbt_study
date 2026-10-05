# Copy isolation: engineering and research protocol

## Motivation and scope

The completed name-driven routing campaign passed six independently qualified
native executions (776 HTTP responses, 72 owned resource UUIDs, 108 raw write/read
observations). It found no new routing defect in that coverage. Repeating it is
less informative than probing a distinct operation with its own state semantics.

This protocol exercises POST /api/recipes/{slug}/duplicate from the pinned Mealie
v3.28.0 OpenAPI contract. Its documented success is 201 with a complete recipe.
The reusable compiler accepts an explicit copy policy; it contains no Mealie URL
or field names. The resource names and semantics belong to opt-in profiles.

## Testable hypotheses

H1: copying assigns a new recipe identity and fresh internal ingredient/step
identities while preserving external food, unit and recipe targets.

H2: incoming recipe/shopping associations remain attached to the original UUID.

H3: editing either recipe's description, instruction text or ingredient notes
does not mutate its counterpart; unrelated referrers keep quantities and targets.

H4: instruction-to-ingredient references in the copy resolve to copied ingredient
identities, not to old ingredient identities that no longer exist in that recipe.

H4 is motivated by inspection of the pinned duplicate_one implementation, which
assigns fresh ingredient reference IDs and step IDs. This alone does not establish
a defect: preprocessing, persistence or serializers could repair the references.
The scenario therefore first creates and reads a valid source reference, then
compares actual duplicate and GET responses against an independently computed
old-to-new ingredient mapping.

Source inspected: https://raw.githubusercontent.com/mealie-recipes/mealie/v3.28.0/mealie/services/recipe/recipe_service.py
Function: duplicate_one, lines 436-490 in the retrieved file. The copy response
schema and operation, rather than an undocumented lookup assumption, bind the
new runtime identity.

## Experimental design

Four profiles each execute two sampled native schedules on new owned fixtures.
The first matched control changes descriptions; the next two vary nested mutation
order; the final profile introduces a valid internal reference. Each fixture
contains three initial recipes, three foods, three units and three shopping lists.
Copying creates a thirteenth owned resource. No HTTP requests overlap.

The fixed mutation suffixes are prefixed by the fresh runtime namespace. The
duplicate is bound from the returned response, then read through its returned
route. Observations include request bodies, raw response bodies/codes and all
protected resource reads after each phase. The independent verifier rejects
missing or duplicate observations, wrong operations, unsupported mutations,
unowned identities and incomplete evidence before claiming PASS.

Evidence integrity is checked through per-review SHA256 and an offline campaign
verifier that accepts slash/backslash archive names but rejects ambiguity. A
candidate is preserved with its first discrepant phase and replicated on new
resources. Multiple schedules reproducing the same mechanism are one bug, not
multiple discoveries. Authentication or missing evidence remains BLOCKED.

## Threats and limits

Tests use configured content fields and reference paths rather than every graph
edge. Derived display strings are excluded only where explicitly declared;
quantities, notes, UUIDs and references remain protected. Image/assets, multi-user
authorization, true HTTP concurrency and full reset/replay are not in this scope.
Native HTTP-fixture tests validate the harness; they cannot establish live Mealie
behavior. This release contains a protocol, not a confirmed copy defect.

## Handoff

Archive the new Downloads campaign.zip after review. Run verify_copy_campaign.py
on it before committing findings. The source-save script also freezes the original
successful routing campaign, its verifier and its known source commit. The earlier
home direct-slug campaign remains open because work-server resources were absent.
