# Generic recursive relationship probes

The preserved Mealie container log records "Recursive Recipe Link Error on recipe controller action" immediately before the failed recipe PUT returned HTTP 400. The rejection is observed protection, not a confirmed server defect. Whether it left partial state has not yet been verified for that original run.

## Generated pilot

The optional recursive_relationships profile policy identifies the canonical resource type, writable field path, qualified rejection codes, source evidence SHA256 and cycle_lengths. The generator has no Mealie-specific branch. The Mealie profile selects recipeIngredient[].referencedRecipe and cycle lengths 2 and 3 based on the observed recursive-link guard.

Positive recipe links form the chain R1 -> R2 -> R3. The generated actors then probe R3 -> R1 (length 3) and R3 -> R2 (length 2). There is no R1 -> R3 shortcut, so the length-3 probe does not also close a length-2 cycle. Other food, category, tag and shopping-list relationships retain shared instances and many-to-many coverage.

Each probe requires successful positive-link tasks and verifies the stored readback snapshots forming its prerequisite path before issuing the update. Its interface snapshots the full source response, prepares a schema-projected body and issues PUT. Probe response codes 200-599 are captured so an unexpected success or server error can still be followed by GET. This transport capture is not an acceptance rule: only the configured rejection code plus structurally identical before/after source responses passes the negative task. Missing GET, unobserved cycle path, unexpected status or changed source prevents the runtime completion receipt.

The last cycle-probe evidence includes task ID, cycle length, status, source_unchanged and the server response body. The final runtime receipt includes separate negative_tests entries. The Python acceptance runner independently requires a matching receipt for every negative task, with qualified status and unchanged source.

HTTP remains in interfaces; stories coordinate actors. All HTTP requests remain serial. Existing generation without the optional policy retains its legacy behavior; no automatic deletion, retry, rollback or reset was added.

Pilot totals: 21 creations, 26 positive relationship updates, 6 relationship actions and 2 cycle probes = 55 tasks, 170 HTTP callbacks, 21 actors. Counts describe a complete future run, not already observed native success.

## Validation and limitations

40 Python tests passed, including generic planning of cycle lengths 2, 3 and 5 and fail-closed rejection of missing qualification. All 466 original transport comparisons passed. The Node scheduler validates distinct interleavings, one active HTTP request, observed path prerequisites, both cycle rejections and unchanged readbacks. Injected cycle acceptance, rejection with partial mutation and HTTP 500 fail after readback. Native Provengo sampling and Mealie execution of this update are pending.

The unchanged-state oracle compares the full source GET response with canonical object-key ordering; array ordering is retained. A mismatch is evidence requiring investigation, not automatic proof of a persistent business-state defect. Target resource state is not independently compared in this pilot. Rollback/replay, longer live cycles and multiple readback resources remain future extensions. OpenAPI alone does not establish the business rule forbidding instance cycles; that rule remains qualified external profile configuration.

## Windows execution

Apply the delta ZIP to the existing study root, then regenerate a new project:

```powershell
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\generic_generator_cycle_probes_delta.zip" -DestinationPath 'C:\work\temp\mealie_sbt_study' -Force
Set-Location 'C:\work\temp\mealie_sbt_study'
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
Get-ChildItem '.\scripts' -Filter '*.ps1' -File | Unblock-File
& .\scripts\Run-Generic-Relationship-Pilot.ps1 -Username 'changeme@example.com' -SampleSize 1
```

This creates new owned fixtures. It does not alter old generated projects or remove earlier fixtures. Upload Downloads\generic_relationship_live_review.zip after execution.
