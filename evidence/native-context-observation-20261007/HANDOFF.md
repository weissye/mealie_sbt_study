# Native Context observation acceptance — 7 October 2026

Three isolated fixture runs used installed native Provengo and generated Context programs. Each run executed creation, initial readback, update, second readback, an observed action and a final readback. The control ended SUCCESS. Both injected HTTP 500 cases ended FAIL only after independent readback: one unchanged, one with a stored change. Expected state stayed request-derived and separate from actual observations.

This package preserves original receipts and generated sources, the corrected experimental renderer, fixture contract, runner and offline regeneration verifier. Regeneration compares all twelve generated JS/report files with the executed archive after LF/CRLF normalization. Original archive bytes are protected by SHA256. No native rerun is required to archive.

This is infrastructure acceptance, not a new Mealie F04/F05 reproduction. Operation roles are selected by fixture summaries; the experimental module has not replaced the central Mealie generator. Source snapshots reproduce the generated files; their byte identity with every source file on the user's computer has not been established. The runner is preserved with the two reviewed fixes.

## Remaining integration gates

1. Add observation state transitions to the central generator through its existing CLI/pipeline, not an additional scenario-only entry point.
2. In shared interfaces separate declared response codes from transport collection codes; capture response.code and raw body without parsing an undeclared text response as JSON.
3. Let dedicated Context verifier bthreads finish all identity-bound readbacks before final failure. Keep expected model independent from server receipts. A failed or absent readback is incomplete, not evidence of unchanged state.
4. Regression-test multiple independent action instances, absent responses, malformed JSON, wrong identities, and conflicting writes before production adoption. The present native acceptance covers one resource and one observed action per run.
5. Preserve existing F01–F03 behavior through unchanged regeneration checks. Evidence from F04/F05 must retain its original classification until new integrations are verified.
6. Do not infer domain-specific action effects or atomicity promises from schemas alone. Unsupported semantics remain explicit limitations; receipt data cannot become expected-state data.

The central interface helper `requestRest` in context_model.py currently gives REST only its expected codes. An undeclared response can therefore prevent the verifier callback and subsequent actuated GET. This is the verified integration point. Merely copying this renderer into that tree is not sufficient.
