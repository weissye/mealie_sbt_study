# Preserved interleaving acceptance and bounded child lifecycle

## Scope and provenance

This delta preserves the verified real Mealie run generator-interleaved-dependencies-20261006-051538-638348, its original review archive, SHA256 and handoff. The independent verifier checks receipts and selected live requests, not only the reported PASS. It sends no API requests.

It also adds a bounded native lifecycle acceptance. Installed generator_v56 and the pinned OpenAPI remain required and are not replaced. The bounded renderer consumes the generator plan; entity paths are selected by the runner, while identities, dependency fields, membership arrays and DELETE success codes are resolved from the plan/schema. This is not complete acceptance of generator_v56's original parallel CRUD renderer. Dormant simultaneous-HTTP code remains in installed source but is not invoked.

## Experiment

Two parent lists and two child items are created in the authenticated account. Both children wait for a verified ready parent; the selected symbolic schedule must show a child POST before that parent's update. Creation, independent reads, marker updates, scalar-state checks and parent membership checks run through native Provengo interfaces and verifier bthreads.

After all create/update workers and both final child readbacks have completed, child1 continues its lifecycle with DELETE. A separate verifier checks:

1. A GET of the deleted child's exact identity returns 404.
2. Its parent still exists with the same identity; the deleted identity is absent from the membership collection and the surviving sibling occurs exactly once.
3. The sibling still has its exact identity, parent binding, updated marker and numeric/boolean baseline.

Only child1 created by this schedule is deleted. The two parents, child2 and all prior fixtures are retained. Deleting parents or the other child is outside this acceptance. Consequently one child completes CRUD; the sibling and parent lifecycles intentionally remain retained. The report keeps full_crud=false at whole-model scope.

Twenty bthreads execute one selected complete native schedule. A complete live run contains 29 HTTP calls including authentication, 28 business response receipts and four update request bodies. Four candidate schedules are sampled without server requests. There is no automatic live retry or cleanup.

## Explicit generic policies and limits

GET returning 404 after a successful DELETE is a generic acceptance convention, explicitly recorded in the manifest; it is not inferred from a declared OpenAPI 404 response. PUT preservation checks compare the refreshed representation with the submitted collection and subsequent reads. A native action reservation excludes other modeled mutations from a refresh/write/readback interval. This is not a server transaction and does not prevent external client changes.

Deletion deliberately occurs after parent updates to prevent an old snapshot from recreating a deleted child. This release therefore tests completed lifecycle integrity rather than deletion during parent writes. Broader lifecycle interleavings, multiple prerequisite families, historical Mealie finding reproduction, reset/replay and multi-user boundaries are not covered here.

## Installation, saving and execution

Extract into the existing study root. Save-Mealie-Native-Lifecycle.ps1 verifies the archived real run, stages only explicit release paths, commits those paths, and optionally pushes. Other local files are not included. With -Push it verifies that the remote branch SHA equals local HEAD. It stops on Git failure and does not resolve or discard unrelated changes.

Run Test-Mealie-Generator-Lifecycle.ps1 with the normal test-account username. It prompts for credentials and runs one selected schedule. The wrapper supports Root, BaseUrl and ProvengoJar. The JAR route uses a 1 GiB heap. Preserve the printed review.zip; this new live evidence is not automatically committed by the source-saving script.

## Release verification

Native Provengo sampling and replay passed against the local synthetic HTTP fixture with collection replacement implemented. The fixture's acknowledged-but-ignored DELETE and accidental sibling deletion were detected after reaching the DELETE operation. Validation archives contain model, receipts and logs; large serialized callback sample files and private authentication products are omitted from the packaged synthetic archives.

The prior real Mealie acceptance is independently verified and retained. Live Mealie execution of this new deletion extension and Windows PowerShell execution remain pending at delivery. No push to the user's repository has been performed from this workspace.
