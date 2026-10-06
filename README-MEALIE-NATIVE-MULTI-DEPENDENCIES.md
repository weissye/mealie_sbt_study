# Native multi-dependency composition from OpenAPI

## Purpose

This bounded acceptance extends the verified native parent/child model to a child simultaneously linked to three independently created resources. It is a functional same-account experiment. It does not reproduce historical authorization defects, claim a new application bug, or implement an autonomous search campaign.

The release also preserves the original real Mealie child-deletion review from generator-child-lifecycle-20261006-052852-481153, its execution transcript, SHA256 and qualification. The transcript records source push 6b8dcf9768dbe69d5081378466b64de37b669c8b; the new review was created afterwards and is archived by this release.

## Contract-derived links and inference boundary

The installed generator plan identifies the child's required shopping-list dependency. It does not currently infer the two optional food/unit dependencies. The generic extension matches input and output schema references using the documented Input/Output suffix convention, finds each companion identity field, and checks its scalar type and format against the target GET schema. Ambiguous or mismatched associations stop generation before live requests.

For the pinned contract this yields shoppingListId, foodId and unitId. The optional links have provenance in dependency-manifest.json: source input references, target GET references and the convention applied. Entity-family scope is explicitly chosen in the runner. Field names, identities, marker properties, success codes and linked resource shapes come from the contract/plan. The renderer contains no application field-name table.

This is a generic renderer extension over generator_v56, not proof that every dependency in arbitrary OpenAPI contracts is inferable. Companion identity naming and marker-update preservation are explicit generic conventions. OpenAPI alone does not fully specify business rules, merge equivalence or PUT side effects. Installed generator source remains unchanged and must be pinned. Its dormant simultaneous-HTTP modules are not invoked or removed.

## Model and deliberate construction prefix

The model contains six lifecycle workers: two lists, one food, one unit and two items. Each family has independent verifier bthreads. A readiness collector starts with the model and remembers the first verified ready instance from each prerequisite family. Children wait for the collected three-family bindings; they do not wait in a fixed list/food/unit sequence or require all instances of the parent family.

A separate native constraint builds the experimental context:

1. Create and independently verify the first linked child.
2. Update the selected parent, food and unit, in any allowed order.
3. Create the second child with the same three bindings.

The first child may update within that prefix as permitted by native scheduling. Prerequisite creation order and the first child chosen are not fixed. This constraint intentionally ensures mutations happen between link construction operations. It is not exhaustive unconstrained schedule coverage. The selected sample must contain actual HTTP child POSTs on either side of the selected parent's PUT, and both prerequisite PUTs between those POSTs.

All HTTP runs through RESTSession interfaces under native Provengo. There is no Python business-step bridge, simultaneous request dispatcher or overlapping-HTTP coordinator. The native action reservation prevents other modeled mutations from interleaving inside a snapshot refresh/PUT/readback interval; it does not protect against external clients. Fresh isolated resources are necessary.

## Verification and evidence

Every create captures identity and independently reads it back. Child creation and subsequent reads check all three foreign-key bindings. If the response includes embedded food/unit objects, their identities must match their companion IDs. Numeric/boolean child state is checked against the initial baseline.

Parent update compares its submitted child membership, markers, scalar values and all three dependency IDs with the response readback. Child updates refresh their current representation inside the reservation before constructing the full PUT. Food/unit updates independently verify their own identity, marker and scalar state, then re-read any child whose creation was already verified. These observations compare the child's last verified marker, bindings and original scalar baseline.

Final child and parent membership reads occur after all six lifecycle workers finish. The food and unit are also independently read in their final updated state. Resources are retained: no DELETE, automatic retry or cleanup is included in this extension. Earlier deletion coverage remains separately archived.

There are 26 bthreads. A complete selected schedule has a base 37 HTTP calls, plus observations of existing children after prerequisite updates; this deliberate prefix produces two such observations, normally 39 calls including login. The exact expected count is derived from the selected native sample and recorded in the report. Six update bodies and all business response bodies are preserved.

Four native samples are generated with no server requests. Only one complete audited schedule satisfying the actual HTTP witness is replayed. Samples are bounded to 64 MiB; the runner releases parsed samples before starting live Java execution. The JAR route uses a 1 GiB heap. Large serialized callbacks remain a known cost, and memory usage is not guaranteed for every machine.

## Release validation and limits

Tests verify reference-backed link inference, renamed fields, ambiguity rejection and identity-format mismatch rejection. Native sampling/replay against a local synthetic HTTP fixture validates the complete model and checks injected wrong-binding errors at creation and update. Synthetic validation does not establish live Mealie correctness. Windows and live Mealie execution of this release remain pending at delivery.

Save-Mealie-Native-Multi-Dependencies.ps1 independently checks the archived real deletion acceptance and inference tests, commits only explicit release paths, optionally pushes, and verifies remote branch equality with local HEAD. Other working files are not included. No push has been performed from this workspace.

Test-Mealie-Generator-Multi-Dependencies.ps1 supports Root, Username, BaseUrl and ProvengoJar. Keep the printed review.zip. Its authentication products are excluded and credentials in logs are redacted. A failure remains a candidate requiring evidence qualification; a reported PASS is bounded to this selected model and sample.

## Classification caution

The bounded create oracle expects two marker-correlated child identities. Schema-valid requests do not by themselves prove that the application promises distinct items for every create: a server may apply domain merge rules not encoded in OpenAPI. If identity capture or binding checks fail, retain the complete request/response and readbacks, and qualify that behavior before declaring a defect. No domain merge policy is silently inferred by this extension.
