# Read-only collection of an existing native failure

Reviewed project: generic-mealie-df53618c20f0.

The food/foodId identity view passed native write and readback in task link:1:2. The run accepted 32 tasks and 101 callbacks before the next PUT returned HTTP 400. Task link:8:3 attempted recipeIngredient[].referencedRecipe from recipe 3 to recipes 1 and 2. Recipe 1 already referred to recipe 3 after accepted task link:8:1. The attempted update would close a runtime instance cycle. This is a hypothesis for the HTTP 400, not confirmation of its cause or proof of a Mealie defect. The supplied log does not include the failed response body.

This patch changes no generator, generated interfaces, stories, profile, samples or existing resources. It collects evidence from the existing run and Docker logs in the UTC interval 2026-10-01T13:32:40Z through 2026-10-01T13:33:30Z. The collector uses no API requests and does not replay any task. It extracts compact failure fields from native-result.json when its size is at most 32 MiB. Larger native result files are reported as skipped. Large serialized samples and the full native result are excluded from the new review ZIP.

Docker logging may omit application error detail. The collector reports unavailable or empty evidence; it does not establish a cause from missing logs. No status code is reclassified as success.

Apply generic_generator_failure_collection_delta.zip to the study root. Run:

```powershell
& .\scripts\Collect-Generic-Relationship-Failure.ps1 -Project 'C:\work\temp\mealie_sbt_study\provengo\generic-mealie-df53618c20f0'
```

Review ZIP: Downloads\generic_relationship_failure_review.zip.

Three targeted tests verify read-only collection, bounded Docker logs invocation, token redaction and removal of raw partial output after timeout. Existing compatibility results are from the uploaded Windows run: 34 tests and 466 transport comparison cases passed.

Next decision requires evidence: if the server deliberately disallows cycles, positive generation should use a configured acyclic instance graph and cycle attempts should become separate negative tests, with rejection and unchanged-state assertions. Recursive schema types alone do not establish whether runtime cycles are valid. Do not silently remove the cyclic relationship or simply accept HTTP 400.
