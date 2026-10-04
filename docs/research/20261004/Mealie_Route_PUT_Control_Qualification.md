# Route control qualification and partial route writes

## Observation

Only control sample 1 ran (seed 542023); rename and alias-reuse cases did not run. The description PUT succeeded, but subsequent raw GET changed recipeInstructions[0].id from ed81141b-9586-484a-8e25-45dc1bc0b78d to 4a04eeb1-eeda-4c5e-9cab-6c89bb4726c4. The PUT had included the old instruction ID. The recipe UUID fca4c488-9ecb-4684-8998-921d7d8f8768, slug, name, ingredient quantities and instruction text stayed unchanged. Update timestamps also changed. The strict full-object preservation oracle stopped the campaign.

## Pinned-source explanation and limits

Archived upstream v3.28.0 source bytes are hashed with exact download URLs. repository_recipes.py update calls entry.update. RecipeModel initialization reconstructs RecipeInstruction instances whenever recipe_instructions is supplied. RecipeInstruction model_config explicitly excludes id; its database column defaults to GUID.generate. This explains the observed replacement. Explicit code exclusion is evidence of implementation behavior, not a documented API promise or proof that all downstream references are safe. No new Mealie defect is confirmed. No invariant is relaxed to ignore arbitrary instruction ID changes.

## PATCH investigation

repository_generic.py patch loads the stored complete resource, merges new_data, and calls update with the result. Therefore a minimal PATCH is not an isolated remedy for instruction reconstruction in this version; that proposed change was withdrawn before delivery.

## Explicit nested identity policy

An optional generic recreated_identity_paths policy declares a specific child-array UUID leaf as replaceable. The three route profiles configure only recipeInstructions[].id. The default is an empty list: no identifier replacements are implicitly tolerated. Stable recipe UUID, slug rules, all instruction text/metadata/reference IDs, cardinality and ordering, ingredient quantities and referrer associations remain protected. New IDs must be valid and unique UUIDs. Each replacement is retained verbatim in per-phase recreated_identities receipts; the independent Python verifier reconstructs and verifies that exact list. These observations are not counted as defects. Any other field change still fails.

PUT remains the selected operation and prior full-body behavior is retained. This is a deliberate, explicit semantic policy justified by archived pinned-source behavior; OpenAPI alone does not prove this policy. It does not establish compatibility for external clients caching instruction IDs. A downstream stale-instruction-reference defect would require a separate reproducible invariant.

## Research qualification

This isolates route alias migration from replacement semantics of nested rows. No repeat of the old quantity bug is claimed. The live campaign still needs to complete the description control, two renames, and old-alias reuse on fresh resources. Expectations about old-route 404 and alias reuse remain explicit hypotheses requiring qualification on failure. Full reset/replay is pending. Windows execution and actual Mealie route outcomes cannot be certified by the local mock tests.

For embedded views of the changed recipe only, expected child IDs are refreshed from the latest validated target GET; the other embedded fields remain protected. Independent receipt validation applies the same ownership-scoped transformation. This prevents treating a freshly hydrated replacement ID as a stale view while retaining quantity and reference checks.

## Validation

117 discovered compatibility tests passed (13 native tests skipped), and 466 lifted transport cases retained identical HTTP arguments and callback effects. A separate native route suite passed three test methods: six complete healthy schedules and nine rejected injected-fault schedules, including instruction text corruption. Forged receipts that hide identity replacements or alter quantities are rejected. Removing the explicit policy also rejects the replacement receipts. The mock now reconstructs supplied instruction IDs on writes, reflecting the relevant observed mechanism. Live rename/reuse outcomes remain pending.
