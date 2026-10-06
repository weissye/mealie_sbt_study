# Native Provengo: distinct dependencies and explicit merge qualification

## Purpose and scope

This delta follows source commit `4ed9abd607ccca385e44aa696bd436ce4b325940`. It preserves the original multi-dependency stop and replaces its distinct-identity assumption with two separate experiments. The installed generator core and pinned OpenAPI remain unchanged.

The preserved run performed 28 HTTP calls before the first failure, including authentication, and captured 27 business responses. The second same-binding item POST returned no `createdItems` and one `updatedItems` entry retaining the first item's UUID, with quantity increasing from 1 to 2 and joined notes. Its marker-based create capture failed. No independent post-merge GET was reached. This observation alone does not confirm a new application defect or prove persisted merge state.

## Experiments

| Scenario | Fresh fixtures | Intent | Native structure |
| --- | --- | --- | --- |
| `distinct` | Two lists, one food, one unit, two items | Each item binds a different verified-ready list; food and unit are shared. Verify stable identity, quantities, direct/embedded bindings and memberships through interleaved updates. | Six entity workers; 26 bthreads including verifiers, readiness, mutation reservation and authentication; 39 HTTP calls in locally validated schedules. |
| `merge` | A separate fresh set of the same fixtures, plus one contribution POST | After the distinct baseline and both final verifiers, add quantity 2 to the first item's same list/food/unit combination. Check retained item UUID, expected quantity 1+2=3, joined notes, bindings, independent item/list GETs, unchanged other item and prerequisites. | Six entity workers plus a contribution actor and two merge verifiers; 29 bthreads including authentication; 46 HTTP calls in locally validated schedules. |

Initial parent readiness order is not fixed. A collector waits for two verified parents and the reference-derived optional food/unit families. Children bind different parents by observed readiness order. The prefix deliberately places one linked item before both parent updates and food/unit updates, then the second item afterwards. Update order within that boundary and first-child choice remain native scheduling decisions. This is bounded prefix coverage, not exhaustive ordering coverage.

## Genuine native SBT execution

`stories.mealie.js` contains lifecycle bthreads, `waitFor` dependencies, verification events and action reservations. All business HTTP is in generated `interfaces.mealie.js`, using RESTSession callbacks. Runtime identities are captured/read inside those callbacks. Python renders, samples, audits and launches the native CLI; it does not execute business steps. No simultaneous HTTP dispatcher is introduced.

A native mutation reservation protects snapshot refresh, write and readback from other modeled mutations. This prevents a stale collection replacement from being misclassified as a server defect. It does not test simultaneous HTTP races.

## OpenAPI versus explicit semantics

Endpoints, supported status codes, identity fields, writable fields and optional schema-reference-backed dependencies come from the pinned contract and generator plan. The experiment selects list/item/food/unit families explicitly; the optional dependency resolver uses documented generic schema conventions. It is an extension around the pinned generator core, not a claim of unrestricted automatic coverage.

`profiles/mealie-native-merge-policy.json` explicitly supplies quantity addition, retained identity, response-envelope names and the note separator. These business semantics cannot be inferred from OpenAPI alone. The renderer cross-checks the quantity and envelope fields against the contract. A policy mismatch or verifier failure remains a candidate requiring qualification; no automatic bug classification is made.

This stage covers create/read/update/readback, not DELETE or complete CRUD. Existing dormant concurrency modules in the installed generator have not been removed; these scripts do not use them. None of the five previously reported findings is claimed reproduced by this infrastructure acceptance.

## Installation and execution

Extract the delta over the existing study root. It does not include Docker data, credentials, the full generator, OpenAPI or the native JAR; those are existing prerequisites. Mealie must be reachable at the selected loopback URL. The Python launcher `py -3`, native Provengo CLI on PATH (or an explicit JAR), and Git for saving are required.

```powershell
$root = 'C:\work\temp\mealie_sbt_study'
Set-Location $root
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& .\scripts\Save-Mealie-Native-Distinct-Merge.ps1 -Root $root -Push
& .\scripts\Test-Mealie-Native-Distinct-Merge.ps1 -Root $root -Username 'changeme@example.com'
```

Default `-Scenario Both` runs distinct first, then a fresh merge experiment only if distinct passes. Each experiment asks for the password separately and makes one live replay. Four bounded symbolic candidates are sampled without server requests; only a complete audited schedule with the intended prefix is replayed. No live retry, deletion or cleanup is performed. All created resources are retained. If a run fails, preserve its printed `review.zip` and inspect it before further runs.

To run just one experiment after qualification, use `-Scenario Distinct` or `-Scenario Merge`. This always creates fresh resources; it does not resume old fixtures. Optional `-Jar 'C:\path\Provengo.uber.jar'` chooses a supplied native JAR. Home root is `D:\Yeshayahu\Temp\mealie_sbt_study`.

Expected success is `NATIVE_DISTINCT_MERGE_PASS` for each requested experiment. The final wrapper message is `REQUESTED_NATIVE_SCENARIOS_COMPLETED`. Reports record actual receipts, planned request counts, independent-readback presence, explicit policy, seed and symbolic witness. A successful bounded run is not proof of whole-system correctness.

## Evidence and Git

The save script verifies original archive bytes, schema inference, renderer checks and release checksums, then commits only the explicit release paths. `-Push` checks that the named remote branch equals local HEAD. It includes the original failed run and its qualification. It does not commit live results that will only be created after installation. Preserve the two new printed review archives for subsequent qualification and evidence archival.

Text checksums normalize CRLF to LF to tolerate Windows checkouts; binary ZIP checksums use exact bytes. Original evidence is retained unchanged.

## Validation and limits

Local verification uses a synthetic HTTP fixture with the native Provengo JAR. Both success scenarios complete; injected wrong merged quantity, success-response-without-persistence, and alteration of the other item are detected by different verifiers. Fixture artifacts are clearly labeled as synthetic and are not application findings. Offline renderer tests additionally reject a policy field absent from the contract and verify HTTP separation, readiness bindings and final-verifier barriers.

The prior fixture always created a new item and therefore missed the application's observed merge behavior. This fixture includes merge-by-list/food/unit behavior, but the real server's policy and persisted result still require the requested live run. Exact note concatenation is an explicit experiment expectation, not a universal API rule.
