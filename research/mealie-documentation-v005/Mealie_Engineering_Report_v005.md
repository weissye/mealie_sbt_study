# Mealie Generator and Evidence Engineering Report

Independent review and authorized positive control execution version v003

Live evidence cutoff 8 October 2026 and provenance review 9 October 2026

## 1 Research questions thesis and engineering findings

The engineering questions are whether a retained contract and explicit plan can be compiled into executable native Provengo JavaScript, whether dynamic identities and state verification survive actual runtime execution, and whether the evidence can be independently linked to observed server failures. The implemented pipeline answers these questions positively within the tested workflows.

The engineering thesis is reproducible compilation and qualified execution with explicit provenance. OpenAPI describes operations and shapes; semantic profiles or plans supply invariants and scheduling intent; the compiler emits interfaces and stories; Provengo issues business operations; callbacks capture runtime identities and verify state; archived records allow independent review.

The finding groups are F01 quantity addition, F02 quantity removal after merges, F03 internal copy references, F04 unhandled unavailable lookup, and F05 retained list change after failed boundary sensitive execution. F01 and F02 may be manifestations of one cause. The latest log correlation supports matching historical and new failure paths for F04 and F05. The later reconstruction scenarios were curated. The original discovery automation is separately supported by the historical review: an explicit identity profile was compiled against OpenAPI and executed by native Provengo. This supports profile driven automated detection, not OpenAPI-only inference of all semantic intent.

This delivery includes an offline evidence audit and a self contained positive control compiler and execution package. It does not redistribute an active F04/F05 boundary replay runner. The read only historical evidence and exception correlations remain available for examination. Accordingly, it is an evidence and positive control artifact, not a complete executable reproduction artifact for all five findings.

## 2 Architecture and responsibilities

The contract reader supplies paths, methods, operation identifiers, request and response shapes and candidate references. A profile or plan supplies resource roles, actor relationships, selected tasks, prerequisites and state invariants. A compiler resolves task operation bindings and emits a native model. These inputs have different provenance and should be recorded independently.

Interfaces contain the REST definitions and callbacks. Stories issue task events or execute prerequisite constrained actions. Runtime returned IDs replace symbolic bindings; a static placeholder is not evidence that the correct UUID was sent. Native logs and successful readback are the evidence for actual bindings.

The generic historical relationship system used multiple logical tasks with coordinated admission. The positive v007 model uses one sequential explicit plan. Neither means overlapping HTTP calls. Counts of actors, stories or logical workers must not be interpreted as true concurrency without measured request intervals.

The package contains the additive authorized_plan_v007.py compiler and the v007 plan and runner needed for its positive control. It does not require the entire historical generic engine for that path: the runner dynamically loads the additive module. A separate historical snapshot is referenced in Git for provenance. Installing the isolated compiler folder below reproduces this additive path only, not every historical generator mode.

## 3 Package layout and integrity

| Path | Purpose | Execution status |
| --- | --- | --- |
| reports | Research and engineering Word reports and their Markdown sources | Documents |
| positive/package | Published v007 source and launcher extracted unchanged | Authorized positive control |
| positive/Mealie_Generator_Provengo_v007.zip | Original numbered positive delivery | Preserved package |
| model/openapi_v007.json | Contract captured in the successful home run | Static compiler input |
| scripts/Verify-Artifact-v003.py | Checks hashes and evidence summary expectations | Offline only |
| scripts/Fixture-Positive-v001.py | Portable native compiler and oracle fixture validation | Local simulated API |
| scripts/Generate-Positive-v001.py | Produces static positive JS from frozen inputs | Offline generation |
| evidence/historical and evidence/primary | Qualified older records and read only primary outputs | Evidence |
| evidence/new | Read only completed native execution records | Evidence |
| evidence/server | Historical and current access and exception streams | Evidence |
| defensive | Proposed v006 guard patch | Not installed automatically |
| MANIFEST_v003.json and inherited PROVENANCE_v001.json | Export hashes and source membership | Integrity metadata |

Run offline verification before any execution. A manifest mismatch means the exported bytes differ; it is not a reason to regenerate the expected checksum. Preserve the failing files and determine whether transfer, line endings or an intentional change caused it. The manifest omits itself and later mutable runs.

An export may redact credentials or normalize text. Source archive hashes and export hashes therefore have distinct meanings. Original mutation evidence is not silently corrected when an oracle is revised. Old and corrected qualification records stay separate. The artifact is intended for private supervisory review and includes fixture identifiers; it is not an anonymized public dataset.

## 4 Environment and version control

The live target used in the accepted home positive run is http://127.0.0.1:9925. The container name is mealie-sbt-study-mealie-1. The recorded target release is v3.28.0, buildId 0552eaa4a80031b8572849cca0ed95d07f1be001 and SQLite. Provengo reports 0.7.5-SNAPSHOT. Preserve the exact deployed image and CLI fingerprints when collecting a new result; release tags alone are not immutable binary identities.

The work study directory is C:\work\temp\mealie_sbt_study. The work generator payload is C:\work\temp\central-process-binding-20261007-133307-073\payload. At home, temporary work is under D:\Yeshayahu\Temp. The accepted home checkpoint workspace is mealie-home-v002-20261008-193929-554 with generator-current as its generator root.

The uploaded checkpoint is repository https://github.com/weissye/mealie_sbt_study.git, branch research/mealie-20261008-v001-20261008-190930-752, commit 93435c31389a77524d5c18af040ba9cfc8448061. That checkpoint contains generator-source-v001.zip but omitted v007 at upload time. It must not be treated as a complete copy of this supervisor artifact or of subsequent evidence.

Each modified script and package receives a new numbered name, banner and output identity. Published v007 bytes are preserved here. The unchanged generation and fixture helpers retain v001 and the underlying compiler retains v007. The updated verifier and reports are v003; original discovery audit records retain v002. The artifact does not relabel inherited source or observations as newly executed results. Git checkout attributes should preserve exact bytes. Never force push, overwrite unrelated staged changes or use a destructive reset as a transfer method. Git transports files, not live Docker databases.

## 5 Installation and offline verification

Requirements are Python 3, Java and native Provengo for execution, and Docker Desktop only for the real server control. Evidence verification and static compilation use the Python standard library and do not contact a server. No Java or Provengo binary is bundled. For local fixture validation, specify the installed Provengo uber JAR explicitly.

Download Mealie_Supervisor_Artifact_v003.zip to Downloads. The independent PowerShell entry sequence is:

```powershell
$ErrorActionPreference = 'Stop'
$downloads = Join-Path $env:USERPROFILE 'Downloads'
$zip = Get-ChildItem $downloads -Filter 'Mealie_Supervisor_Artifact_v003*.zip' |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $zip) { throw 'Supervisor artifact v003 ZIP missing.' }
$artifact = Join-Path $downloads `
    ('mealie-supervisor-v003-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
Unblock-File -LiteralPath $zip.FullName
Expand-Archive -LiteralPath $zip.FullName -DestinationPath $artifact
Get-ChildItem $artifact -Recurse -File | Unblock-File
py -3 (Join-Path $artifact 'scripts\Verify-Artifact-v003.py')
if ($LASTEXITCODE -ne 0) { throw 'Offline artifact verification failed.' }
```

If py is unavailable but python is configured, use python in place of py -3. Keep the printed verification result with the review. The helper verifies artifact hashes and retained summary totals; it does not independently prove every historical oracle assumption. The primary output records and audit mappings are included for deeper inspection.

## 6 Independent positive JavaScript generation

Generate an inspectable native model from the frozen contract and published explicit plan:

```powershell
py -3 (Join-Path $artifact 'scripts\Generate-Positive-v001.py')
if ($LASTEXITCODE -ne 0) { throw 'Positive model generation failed.' }
```

The helper dynamically imports the additive v007 compiler and make_plan function. It uses the frozen model/openapi_v007.json and writes runs/generated-positive-v001 with config, interfaces, stories, generation report and plan. It preserves the source packages. Runtime IDs remain symbolic until live callback execution.

Inspect project/spec/js/interfaces.v007.js and stories.v007.js, the generated operation report, and the explicit plan together. The output has 27 steps. Compilation verifies the supplied operation bindings and expected positive response codes. It does not prove every request schema property, all API semantics, or absence of runtime faults.

The generated model requires actor token environment variables at runtime. For real execution use the published launcher below so that authentication, actor setup, export redaction and acceptance checks are performed consistently. Do not place tokens into a saved PowerShell command, Git commit or static JS file. Static generation is not a live acceptance result.

## 7 Native fixture validation and oracle control

The portable fixture helper simulates only the authorized shared resource operations used by v007. It creates an in process local HTTP server, compiles native JavaScript and runs the specified Provengo JAR. It is a compiler and callback integration check rather than a Mealie implementation.

```powershell
$jar = 'YOUR_ACTUAL_PATH\Provengo.uber.jar'
py -3 (Join-Path $artifact 'scripts\Fixture-Positive-v001.py') --jar $jar
if ($LASTEXITCODE -ne 0) { throw 'Positive fixture validation failed.' }
py -3 (Join-Path $artifact 'scripts\Fixture-Positive-v001.py') `
    --jar $jar --corrupt
if ($LASTEXITCODE -ne 0) { throw 'Oracle corruption control failed.' }
```

In normal mode the expected result is native exit zero with 27 requested operations and 27 step passes. Corruption mode adds a synthetic wrong quantity in the fixture response. Its expected native result is a nonzero exit caused by the oracle. The helper itself returns success when that intentional corruption is detected. Distinguish helper acceptance from native application test status.

Outputs are local validation results and logs under runs/fixture-results-v001, and generated fixture projects under runs. These mutable outputs are not part of the immutable artifact manifest. The fixture helper does not create accounts in the user's actual Mealie instance. The JAR path is an operator supplied dependency; a missing JAR or unsupported Java is infrastructure failure.

## 8 Authorized live control execution

Start Docker Desktop and confirm the existing server responds. The following does not reset state or deploy a patch:

```powershell
Invoke-RestMethod 'http://127.0.0.1:9925/api/app/about' -TimeoutSec 10
```

For a self contained additive compiler installation, create an isolated generator folder. This folder provides the module namespace needed by the v007 runner; it is not represented as a complete historical generator restoration.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
$generator = Join-Path $artifact 'runs\isolated-positive-generator-v001'
New-Item -ItemType Directory -Path `
    (Join-Path $generator 'generator_v56') -Force | Out-Null
& (Join-Path $artifact 'positive\package\Run-Generator-Provengo-v007.ps1') `
    -GeneratorRoot $generator `
    -BaseUrl 'http://127.0.0.1:9925'
```

If the CLI is not on PATH, append -ProvengoJar $jar using the actual installed JAR path. If the administrator email is different, append -AdminEmail with its configured email. The runner prompts for the hidden admin password and obtains tokens automatically. The administrator provisions two ordinary users in the same group and household; it does not perform the business checks as an elevated actor.

Provengo performs recipe and list construction and the P1 to P5 business operations. Python performs setup, compilation, invocation and evidence packaging. The acceptance requires native exit zero and all 27 callback markers. The real home run supplied in evidence/review_v007.zip already met those conditions. A later pass is another positive control result, not confirmation of all five historic findings.

The test creates users and resources and does not automatically delete them. Runtime internal products may retain credentials locally even when the exported review excludes them. Preserve the sanitized review; do not upload raw products indiscriminately. Inspect new evidence before external sharing.

## 9 Positive control semantics and interpretation

P1 adds a permitted recipe contribution and both users read the resulting list. P2 adds valid recipe contributions together and checks normalized totals and associations. P3 adds a manual item. P4 updates its checked state. P5 reduces a valid recipe contribution. All resources are permitted to both ordinary users under the shared fixture.

Each state expectation originates in the explicit positive plan. The compiler records operation binding provenance, and callbacks compare quantities, references, checked state and reader agreement. This demonstrates that the runtime preserves dynamic bindings and the chosen state invariants. It does not establish automatically inferred arithmetic or permission policy.

The number 27 counts generated steps and callback completions, not 27 independent semantic properties or 27 bug findings. The setup contains additional Python requests not included in that count. Sample coverage, response policy acceptance and application correctness remain separate metrics.

## 10 Historical F01 to F03 evidence review

The quantity freeze verification record contains 24 entries, with 18 semantic discrepancies and six successes. For each retained discrepancy inspect the signed amount, aggregated before state, fresh recipe state, expected state and observed state. Verify canonical keys across rows. A nonzero execution alone is not sufficient.

F01's numerical anchor is 17 plus half of four: expected 19, observed 20. Correct recipe association bookkeeping alongside an incorrect ingredient aggregate supports the discrepancy. F02's food anchor is 15 minus four: expected 11, observed nine. The unit anchor is 13 minus six: expected seven, observed 11. The engineering interpretation requires fresh reads rather than assuming cached quantities survive a merge unchanged.

The copy requalification record contains eight runs: six pass and two retain dangling internal references. Compare ingredient reference identifiers inside the copied recipe with instruction references in that same object. Ignore derived display changes excluded by the corrected oracle. The source based remapping explanation and the numerical discrepancy explanations remain distinct from accepted repair proof.

Historical frozen functional models were symbolically sampled: the F01 and F02 examples have 51 tasks; the F03 example has 25. Packaging validation sent no live requests and reported Windows scripts not executed. Do not turn symbolic sample acceptance into a live reproduction claim. This artifact provides read only evidence rather than those active replay projects.

## 11 F04 and F05 server correlation

Audit v001 matched the 16 historical request paths to historical HTTP 500 access records: twelve unavailable reference observations and four retained list mutation observations. The separate Oct1 disk I/O error is excluded. The historical export ends with a Docker invalid null log error and does not cover the new October 8 executions.

Audit v002 uses the newly supplied server stdout and stderr streams. Every selected probe resource path from the two completed native runs matches one access record. An exception is correlated after that record, bounded by the next 500 timestamp and a maximum one second window. Bounding by the next request avoids assigning a later exception to an earlier probe when multiple probes occur within one second.

F04 matches UnexpectedNone with Recipe not found and relevant service frames at lines 445 and 342. F05 matches AttributeError for list_items and relevant service frames at lines 449, 219 and 134. These signatures match historical traces. The new JSON audit records exact native filenames and line numbers, access lines, exception lines and service frames.

There is no global request ID in the evidence, so this remains path and timing correlation. The recorded collection completed flag is true but its Docker exit code is null. The actual relevant records are present; do not claim that the exporter verified a zero Docker process exit. Do not reverse this distinction into a claim that the logs were empty or unusable.

The client evidence and owner readback support the F05 state consequence. The matched stack supports the corresponding code path. Complete causal attribution, exact effective write policy, restart durability and live patched behavior remain separate qualifications.

## 12 Defensive patch and regression evidence

The proposed guard patch validates missing references and rejected writes earlier in the service and translates selected failures into controlled responses. It is retained for source review. Applying it to the user's running container is not part of this delivery. An isolated checkout and deployed patch fingerprint would be needed for a controlled live patched result.

The archived regression summary reports nine failed baseline rejection tests and three passing controls, then 84 passing patched tests. Inspect JUnit records and version metadata rather than relying solely on a human summary. Some baseline tests terminate at an exception before checking final state, so they cannot replace live state evidence for F05.

The patch does not establish fixes for quantity or copied graph findings. The published positive control guards against selected behavioral regressions, but a passing positive result does not test every rejected operation. Do not label a simulated fixture pass as a patched Mealie pass.

## 13 Failure diagnosis and acceptance criteria

| Symptom | Classification | Required evidence |
| --- | --- | --- |
| Missing Python Java or JAR | Dependency failure | Actual tool invocation and version |
| Authentication 401 | Fixture or credential problem | Setup result without credential disclosure |
| Connection refused or Docker timeout | Infrastructure failure | Captured partial logs and target URL |
| Compiler binding absent | Contract or input mismatch | Frozen contract and exact plan |
| Missing callbacks | Incomplete native execution | Native log and generated step list |
| Native SUCCESS with semantic classification | Model completed | Classification and state evidence remain decisive |
| Hash mismatch | Integrity failure | Original and exported bytes preserved |
| Log export with null exit code | Export metadata limitation | Actual stdout and stderr content |

Accept offline review only when immutable hashes pass and claimed evidence entries are available. Accept static compilation when the compiler completes and outputs the expected model and provenance. Accept fixture validation only when both its normal and intentional oracle failure controls meet their separate expectations. Accept live positive execution only with the actual target fingerprint, complete callbacks, native result and sanitized review.

A complete fresh reproduction of every finding is not an acceptance claim of this package. Its executable scope is authorized positive consistency; its all finding scope is historical and new evidence assessment. This limitation should accompany any distribution of the artifact.

## 14 Artifact maintenance and supervisory handoff

The research and engineering reports share one finding inventory and evidence cutoff. They should be updated together after any new qualification. A new patch, oracle change, regenerated plan or reordered scenario receives a new version and its own provenance. Never change old result files to make a later narrative consistent.

A supervisory reviewer can reproduce the offline integrity checks, regenerate the positive JS without credentials, validate it with a local fixture and run the authorized control independently. They can inspect the preserved F01 to F05 records and exact F04/F05 exception correlation without sending new boundary requests. The broader generic source and prior active projects remain separate historical items rather than implied contents of this ZIP.

Before public release, remove personal fixture metadata, review permission assumptions, establish code licenses for distributed dependencies and confirm maintainer disclosure status. These are future publication checks, not assertions that public issue equivalence or novelty has already been established.

## 15 Original discovery lineage and executable scope

The original source compiler identity_program.py accepts a contract and explicit runtime profile. It validates selected operation bindings, attaches request schemas, derives response-dependent prerequisites and actor ordering, and emits native interfaces and stories. The original campaign tools perform sampling, preserve model and schedule hashes, execute sampled schedules, capture complete callbacks and qualify candidates. The eight accepted historical run receipts contradict the assertion that those completed discovery runs used invalid JS.

The retained input profiles and generated plans preserve the same ordered step identities and check declarations in all eight comparisons. Twelve reviewed source files match named historical Git objects after line-ending normalization. Body and schema additions are documented rather than treated as byte-identical source regeneration. The exact installed source at each historical Windows execution is not attested.

The artifact contains this audit as read-only metadata in evidence/discovery. It does not add a live F04/F05 replay generator. The original source references, historical native execution and later replication results remain separate provenance chains. Combining their files is not sufficient to prove that the latest model was produced by the original compiler.

## 16 Portable system adapter contract

A future adapter should name its API version and contract SHA256, allowed owned-resource workflows, operation bindings, writable fields, response identity selectors, relationship declarations and documented invariants. Each field should carry its source pointer or reviewed semantic provenance. Credentials and fixture identifiers are runtime inputs, not literals committed to the adapter.

The generic compiler should own contract validation, response-dependent binding, prerequisite construction, schedule generation and evidence emission. Target-specific branches in that compiler count as engine changes and must be reported; an unchanged file name is not proof that the engine transferred unchanged. Preserve the previous engine and adapter revisions when moving from the pilot to evaluation.

A minimal transfer bundle contains contract.json, adapter.json, invariant declarations, generated JS, compilation report, selected schedules, tool fingerprints and receipts. These are a proposed interface and output set, not newly implemented files in this release. Begin with one owned-resource workflow in Vikunja, validate compilation and a local independent fixture, then freeze three pilot seeds and ten separate evaluation seeds. Add Gitea as a second transfer workflow after the first gate passes.

## 17 Campaign records and comparison controls

Each run needs run_id, system/image/version, database/configuration fingerprint, engine/profile revisions, contract/model/schedule hashes, seed, start-state record, request intervals, actor/binding provenance, readback observations, native result and qualification status. Separate setup, sampling, execution and analysis durations. Capture server stdout and stderr and mark incomplete exports explicitly.

No trial should silently repair its own model after a failure and continue under the same accepted run identity. A changed adapter, oracle or compiler creates a new version and a new pilot. Fresh resource names isolate objects but are not database resets. Provisioning, application calls and oracle GET requests should be counted separately and included in an explicitly defined total budget.

The comparison evaluator must use sequence-local evidence. Native tool findings and evaluator findings are distinct fields. The same resource and invariant scopes apply to all tools; record absent readback evidence as unevaluable. Contract-only and declared-semantics tracks require separate input manifests. A baseline with the known Mealie failure trace is a diagnostic replay baseline, not a discovery baseline.

## 18 Version v003 acceptance and next implementation

This release updates both reports and adds the original discovery audit and the transfer/comparison protocol. It retains the existing positive-control compiler and evidence. The v003 verifier checks the current immutable file hashes and inherited quantity/copy summaries, then validates eight original native receipts and eight profile-to-plan comparisons. Static positive generation is tested from a freshly extracted archive. These offline checks are not a new live run and do not establish fresh replay of every group.

The next implementation is a frozen adapter and authorized sequential consistency pilot for Vikunja. Its deliverable should include a provenance-complete input manifest, newly generated JS, native acceptance and independent oracle controls before any research finding is claimed. True concurrency and authorization-boundary generation are not introduced by this report update.


## Automation lineage clarification — v005, 9 October 2026

The original 5 October discovery was automated through declared profiles, contract-bound generation and native Provengo execution. Explicit semantic inputs do not imply prior knowledge of the defects. The current reconstruction must not be substituted for the original discovery when describing automation provenance.

| Link | Evidence | Acceptance and limitation |
| --- | --- | --- |
| Original inputs to generated plan | Discovery_Audit_v002.json; retained profiles and plans | Four configurations have matching ordered step identifiers and checks. Generated plans add schema data and contain recorded body differences. This is correspondence, not byte-identical recompilation. |
| Original compiler source | Source commits f1f29cf5dad0991faa677d0cc98481f56ef5de28 and 81d332221c3f567044c9a15f85297cb064b08f69 | Twelve retained source comparisons match after newline normalization. Review snapshots do not attest the exact installed source. |
| Generated JS to original execution | multi-identity-20261005-065704, seed 844524; scope-controls-20261005-073218, seed 264758 | Eight native runs completed with exit zero and LIVE_CALLBACKS_COMPLETE. Earlier callback failures must not be generalized to these accepted discovery runs. |
| Execution to findings | Historical state evidence and server traceback audit | Twelve F04 and four F05 observations are supported by the historical audit; a separate disk I/O error is excluded. |
| Current integrated package generation | v016 source ZIP and freeze v004 | All 415 master hashes, ten version manifests and ten template-output comparisons accepted; ten Python files parse. Source inspection confirms integrated package production. No fresh full regeneration was performed in this audit. |
| Current execution receipt | Archived v016 result | Native exit zero and 15/15 markers are retained. This is audited archived evidence, not a new live execution. |
| Original plan to current plan | Historical and v016 inputs are retained in their respective archives | Complete task, actor, prerequisite and oracle equivalence has not been established. Similar observations and integrated packaging alone do not close this link. |
| v016 failure to original root cause | Corresponding v016 server traces | Not established in the current audit. Prior v014/v015 traceback correlation cannot be silently attributed to v016. |

**Supported statement for the thesis.** F04 and F05 were discovered during an automated, profile-driven OpenAPI compilation and native Provengo testing process. Subsequent runs provide separate replication evidence. The v016 revision integrates production of the model and its surrounding execution package into the generator. Original discovery provenance, current execution acceptance and cross-version semantic equivalence are distinct evidence claims.

**Meaning of explicit input in v016.** plan_v016.py is declared test intent in the supplied reconstruction package. Its explicit form neither invalidates original automated discovery nor demonstrates that it was automatically re-derived by the original discovery pipeline. The supplied compiler report states that semantics come from a curated plan. This observation concerns the current source interface; it is not a claim that the original bugs were manually inserted after discovery.

OpenAPI-only inference of all semantic intent remains unproved. A predeclared expected outcome does not imply a pre-known defect. Moving intent into compiler code would not, by itself, strengthen the automation claim.

**What is complete.** The documentation now separates original discovery, later replication, integrated package production and remaining equivalence checks. It preserves original source bytes and existing results. It does not label five finding groups as five independent proven causes or a complete fresh replay.

**Remaining provenance work.** Record correspondence of original versus current task semantics, actor roles, dependency edges, state projections and oracle assumptions, with differences explained and linked to exact source hashes. Audit the server traces for the v016 time window independently. A completed mapping should receive its own version and distinguish exact equality from justified equivalence. No new vulnerability execution is needed to perform these read-only checks.

Source archive SHA256: 924e363fdf399bd261e12cb89a4c8319c2f393ffd2849ba52a6548b0ffb4c378. No v016 Git revision has been supplied; do not invent one. No Git publication occurred during this documentation update.
