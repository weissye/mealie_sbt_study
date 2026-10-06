# Native dependency interleaving: protected snapshot updates

## Why this correction is necessary

The previous live run refreshed an empty parent collection, created a child, and then submitted the stale empty collection in a full PUT. The PUT response was empty and the subsequent child GET returned 404. This is consistent with submitted collection replacement. The run does not by itself establish a Mealie defect. The previous synthetic fixture incorrectly ignored collection replacement, so its passing result did not validate this ordering.

This release corrects the acceptance model and synthetic fixture. It does not change Mealie or the installed generator_v56 source. It remains a bounded renderer consuming the generator's contract-derived plan, not full acceptance of every generator operation.

## Explicit scheduling policy

A generic `dependency:action-transaction` bthread grants one mutation action at a time using native Begin/End events. A parent update holds this scheduling reservation from its fresh GET through PUT and independent verification. A child create or update holds it through its independent verification. This prevents modeled mutations from invalidating a snapshot used for a marker-only update.

This is a scheduling constraint, not a server transaction or a claim that PUT is atomic. It cannot prevent external clients from editing the same resources. Run against isolated fresh fixtures. A child mutation inside the parent's GET/PUT window is deliberately excluded from this acceptance. Testing lost updates requires a separate, explicitly specified oracle and policy.

The four lifecycle workers remain interleaved: children may be created and updated before the parent's rename. No all-parent-updates-complete barrier is introduced. A selected schedule must contain an actual child POST between its parent's readiness and PUT. All business HTTP is executed through generated RESTSession interfaces by native Provengo. There is no simultaneous HTTP dispatcher or Python business-step bridge. Dormant concurrency modules in installed generator_v56 have not been removed by this delta.

## Verification

Eighteen bthreads: four lifecycle workers, eight action verifiers, two final verifiers, startup and completion collectors, authentication, and the action transaction bthread. Complete runs contain 25 HTTP calls including login, 24 captured business response bodies, and four update request bodies.

The parent verifier checks that the submitted child collection remains represented exactly once by each identity, with marker, parent binding and numeric/boolean state preserved. Child verifiers check identity, marker, binding and scalar state. Final reads occur after all four lifecycle workers finish. HTTP failures or semantic differences require qualification; no error is automatically declared an application bug.

Four native symbolic schedules are sampled; only one complete schedule satisfying the interleaving witness is replayed. If no qualifying sample exists, execution stops before live requests. No live retry, deletion, or cleanup is performed. Two lists and two items created in the authenticated account are retained.

## Local validation and limits

Native Provengo against a local synthetic HTTP server passed with real collection replacement enabled. Three injected faults were detected: nonpersisted child update, unintended scalar change, and loss of a submitted child during parent PUT. A separate regression proves that a stale empty PUT deletes an existing fixture child; the server no longer masks the original harness error. Four witness tests also passed.

These are synthetic results, not a new Mealie run. Windows and live Mealie acceptance of this correction remain pending. The model does not implement deletion, full CRUD coverage, or reproduction of the five historical findings. OpenAPI supplies operation/schema structure; the reservation and preservation policy are explicit generic test policies, not inferred application semantics.

## Install and run

Extract this delta into the existing study root, run the two offline regression files, then Test-Mealie-Generator-Interleaving.ps1. The wrapper accepts Root, Username, BaseUrl and optional ProvengoJar. Credentials are prompted; the JAR route uses a 1 GiB heap.

Preserve the printed review.zip. It contains generated interfaces/stories, selected symbolic sample, response and write receipts, logs and provenance. Native authentication products are excluded. No commit or push to the user's Git repository has been performed.
