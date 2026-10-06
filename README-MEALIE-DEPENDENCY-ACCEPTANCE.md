# Native dependency acceptance

This delta requires the existing `generic-generator/generator_v56` and pinned `generic-generator/compatibility/contracts/mealie.json`. It does not replace the installed generator source. It adds a bounded generic renderer over its inferred Plan and updates the previous live-run helper to support four workers and exclude native internal products from evidence archives.

## Install and run

Extract into `C:\work\temp\mealie_sbt_study`. Run the offline renderer checks first:

```powershell
py -3 -B .\tools\test_mealie_dependency_renderer.py
```

Then run:

```powershell
& .\scripts\Test-Mealie-Generator-Dependencies.ps1 -Username 'changeme@example.com'
```

Mealie must already be available at `http://127.0.0.1:9925`. Authentication is interactive. The test creates two lists and two items in the authenticated account, updates their marker fields, independently reads them back and reads the containing lists to verify membership. All four resources are retained. No deletion, automatic retry, cross-account probe, or reset is performed.

Expected result: `NATIVE_DEPENDENCY_FUNCTIONAL_ACCEPTANCE_PASS`. Preserve the printed `review.zip`, including generated interfaces/stories, dependency evidence, native sample, redacted log and 18 response bodies. Internal native products are excluded because authentication responses may contain tokens. Do not automatically repeat a failed run.

The optional `-ProvengoJar` parameter selects a specific JAR and uses `-Xmx1g`; otherwise the existing Provengo launcher on PATH is used. Windows launcher acceptance remains to be checked by the user's run. No Chrome shutdown requirement is imposed.

## Scope

Four lifecycle bthreads, eight verifier bthreads, one startup barrier and one authentication bthread: 14 total. One native symbolic schedule is generated and then replayed. Nineteen HTTP calls are expected, including authentication. Parent CRUD completes before parent readiness is published; child actions can interleave thereafter. The two child workers accept any ready parent of the inferred family, not a hard-coded parent instance. Both may bind to the same list.

This is create/read/update/readback dependency acceptance. It is not full CRUD, exhaustive ordering coverage, true simultaneous HTTP concurrency, a complex bug-finding campaign, or reproduction of the five Mealie findings. Those milestones remain pending. The original parallel-CRUD renderer has not been fixed or accepted by this delta.

## Genericity and explicit assumptions

The runner selects one Mealie family pair as a bounded experiment. The renderer derives methods, paths, successful status codes, request fields and the dependency from the inferred OpenAPI Plan. No semantic runtime profile is supplied.

The implementation has explicit generic conventions: a schema-supported `id` is used when Plan identity inference is absent; marker selection prefers writable `name`, `note`, `title`, or `description`, then another unformatted string. Envelope extraction requires a unique marker-correlated identity. Required unsupported create fields, ambiguous dependencies and ambiguous containing-resource views stop generation. These conventions are not a proof that OpenAPI encodes all persistence or business semantics.

Update bodies preserve properties declared writable by the update schema using the verified GET snapshot, changing only the marker. Bodies of business responses are logged before validation; the authentication response is excluded from these receipts.

## Validation

Six offline architecture checks pass. Real native sampling and replay pass against a local synthetic HTTP fixture. A fixture that acknowledges but does not persist an item update is rejected by the generated verifier. This fixture is a renderer validation aid, not a Mealie bug or evidence of Mealie acceptance.
