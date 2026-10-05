# Engineering and Reproduction of the Mealie Provengo Study

Engineering report for installation evidence review and functional reproduction

Package freeze 5 October 2026

## Executive overview

This package preserves five finding groups, the original evidence, a snapshot of the generic generator, the pinned OpenAPI contract and dedicated Provengo stories using one shared interface file. It is a review and reproduction freeze, not an assertion that every finding has an independently proven root cause or a minimized test. The research report contains classification and public related work; this report specifies the implementation, installation, verification and operational limits.

The functional cases F01, F02 food, F02 unit and F03 have been transformed from retained generated models, syntax checked and sampled successfully by native Provengo without server requests. Live execution of these newly packaged models on Windows remains to be validated. Their original executions are preserved and independently checked. F04 and F05 have offline archive verification and illustrative recorded evidence stories only; no new live reproduction of the scope sensitive behavior is supplied. The recorded stories do not recreate the original server state and do not replace archive verification.

The package intentionally uses a separate local review service on port 9928. The original study service on port 9925 and its data remain separate. The package does not transfer Docker runtime state, perform automatic deletion, or claim a full reset replay. It can be committed as one versioned directory and opened at either work or home without absolute source paths.

## 1 Package structure and evidence provenance

| Directory or file | Purpose |
| --- | --- |
| reports | English research and engineering reports in Word and editable Markdown |
| evidence | Original archives and original independent qualification tools |
| historical-documents | Earlier finding reports retained for provenance |
| source/generic-generator | Generic generator snapshot including profiles and contract |
| reproductions/interfaces.shared.js | Shared HTTP transport and case specific generated functions |
| reproductions/F01-addition | Dedicated quantity addition story and original plan |
| reproductions/F02-food-removal | Dedicated food merge removal story and original plan |
| reproductions/F02-unit-removal | Dedicated unit merge removal story and original plan |
| reproductions/F03-copy-reference | Dedicated copy consistency story and original plan |
| reproductions/F04-recorded and F05-recorded | Recorded assertion stories with no live HTTP |
| scripts | Preparation, evidence verification, functional execution and Git archival |
| validation | Package validation records; later local verification outputs |
| compose.review.yaml | Separate local Mealie review service |
| PACKAGE-SHA256.json | File level byte integrity manifest |

The quantity archive preserves 24 main native runs, the excluded authentication attempt, supporting campaigns and historical generator snapshots. The copy archive preserves all eight original runs, including the original false positive classifications and corrected qualification. The two identity archives retain original observations, server log excerpts, policies and independent receipt validators. Nested live review archives retain the original generated interfaces, stories, plans, accepted samples, runtime receipts and native output where collected.

The preserved original interface files are historical evidence. They are not replaced by the new shared interface. The reproduction provenance file records the original native review hash and, where applicable, the exact nested archive entry used. Slash normalization is required when reading ZIP members because some original entries use Windows backslashes. Ambiguous normalized names must be rejected rather than choosing an arbitrary member.

The last operator verified scope findings push is c89f412a35492a03a231d9d189caa3714afb7864. Relevant preceding checkpoints include 7976e8d0f350adcbe09e8555707292836a001a9a for copy qualification and 68d3766348382bad60feb2076ffb50d39f3d66ed for unavailable reference findings. These recorded commits are provenance anchors. The new package has not been pushed by this environment; its Save script performs and verifies that operation on the operator's authenticated machine.

## 2 Architecture and engineering responsibilities

### Contract parsing and resource analysis

The existing generator_v56 package parses OpenAPI operations and schema references. Resource and operation maps distinguish resource families, identifiers, response views and candidate relationships. Identical UUID shape or a similar field name is insufficient to merge unrelated resource families. Optional profiles promote reviewed relationships into executable tasks. Recursive views are not flattened automatically into unconditional creation prerequisites.

OpenAPI is preserved as input, not treated as a complete behavioral specification. It does not determine arithmetic contribution rules, valid household sharing, effective roles, merge equivalence, or protected copy semantics. Those are explicit profile assumptions, recorded so that they can be reviewed and changed without embedding Mealie rules in generic inference.

### Plan and story compilation

The plan describes instances, tasks, prerequisites and operation bindings. Compiled stories contain behavioral threads for bootstrap, admission, actors and completion. Stories request logical task events and call interface functions. The coordinator enforces prerequisites and admits one active task; requests are serialized. Logical workers and actors are not evidence of overlapping network calls.

### HTTP and runtime binding

All live HTTP in the supplied functional models resides in interfaces.shared.js. A shared RESTSession targets localhost port 9928. Case specific function identifiers are prefixed so that functions from different archived models do not collide. Only one story is loaded into each prepared project.

Returned identities, dynamic route parameters, request bodies and snapshots are held in Provengo runtime variables. An event containing a symbolic placeholder is not proof that the corresponding UUID was sent on the wire; runtime execution and response evidence are required. The callbacks retain original generated contexts and validation logic. Their isolated callback construction limits scope serialization, which was a source of oversized samples in earlier work.

### Independent qualification

Native process exit code, full task completion, accepted receipt and semantic correctness are separate conditions. An authentication failure, missing service or memory failure is not a semantic bug. A known discrepancy may stop a run before completion; the completed prefix and first mismatch are retained. Independent Python validators recompute the quantity expectations, copy reference consistency and identity observations from originals.

## 3 Version pinning and environment

| Component | Operator reported study environment |
| --- | --- |
| Mealie | v3.28.0 |
| Git | 2.43.0.windows.1 |
| Python | 3.12.10 |
| Java | 21.0.8 LTS |
| Provengo | 0.7.5 SNAPSHOT |
| Docker engine | 24.0.7 |
| Generic generator base version | 0.26.19 parallel CRUD revision 3 |

The operator reported local Mealie image ID is sha256:dc61bc0635ee37b6a1b83fa0021b776c9e11b6bd1b06cfe4c45a8007a3944766. This is a Docker image configuration identifier, not a registry manifest digest; do not insert it after an image name using the registry digest syntax. The compose file pins the v3.28.0 tag. Compare the actual image ID and contract before claiming an exact binary reproduction. A rebuilt image with the same version may differ.

The retained contract at source/generic-generator/compatibility/contracts/mealie.json has SHA256 90e19aa713ab4ba15352627aca7dc37290f868b213eb65a3e1564f3b7a7ff292. Confirm this value with PACKAGE-SHA256.json. Environment metadata collected later cannot retroactively prove the binary used by every historic run. The manifest, campaign receipts and pinned source establish the evidence that is actually available.

The new shared models were sampled in Linux using OpenJDK 17.0.20 and the available Provengo JAR. This is a portability and symbolic validation check, not a substitute for execution using the operator's Windows installation. PowerShell execution is not available in the packaging environment, so Windows scripts have not been run here.

## 4 Installation on work and home machines

Install Git, Python 3.9 or later, a supported Java runtime, Provengo CLI and Docker Desktop with Linux containers. The retained operator versions above are the preferred baseline for an exact environment comparison. Verify that git, python or py, java, provengo and docker are available from the same PowerShell session. No Provengo binary is redistributed in this package. The Python evidence checks use the standard library; generator dependencies are represented by the frozen source rather than an invented installation lockfile.

At work use C:\work\temp\mealie_sbt_study. At home use D:\Yeshayahu\Temp\mealie_sbt_study. Extract the package into that existing repository root. The extracted directory is supervisor-review-20261005. The scripts derive their package root from their own location. Do not restore an earlier encrypted transfer snapshot merely to install this package, and do not overwrite the working repository with an older source tree.

Run offline evidence verification first:

```powershell
$project = 'C:\work\temp\mealie_sbt_study'
$review = Join-Path $project 'supervisor-review-20261005'
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
Get-ChildItem (Join-Path $review 'scripts') -Filter '*.ps1' | Unblock-File
& (Join-Path $review 'scripts\Verify-Evidence.ps1')
```

At home change only $project to D:\Yeshayahu\Temp\mealie_sbt_study. The verifier checks package hashes and then the quantity, copy, unavailable reference and household campaign validators. It sends no HTTP requests. A failure must be investigated before overwriting archives or publishing results. Text files in the package use a local .gitattributes rule to preserve exact bytes across Git checkouts; this matters for original checksum verification.

### Dedicated review service

Start the separate fixture:

```powershell
Set-Location $review
docker compose -p mealie-supervisor-review -f compose.review.yaml up -d
if ($LASTEXITCODE -ne 0) { throw 'Review service startup failed.' }
docker compose -p mealie-supervisor-review -f compose.review.yaml ps
Invoke-WebRequest 'http://127.0.0.1:9928/openapi.json' -UseBasicParsing
```

Complete the application's initial account setup on this dedicated fixture and retain the chosen username and password outside Git. Do not infer the fixture password from the username used in the original campaigns. The execution wrapper prompts for the password and restores prior environment variables afterward. It does not provision multiple identities or create a new boundary sensitive campaign.

Record the dedicated container image identifier using docker inspect, the returned contract, its SHA256, runtime versions and setup decisions with each new live run. The fixture uses its own named volume. Starting it is not evidence that it is empty if a review volume already exists. This package does not automatically remove volumes, reset a database, or delete the original service.

## 5 Dedicated stories and the shared interface

The four functional reproductions derive from the original archived generated models. Preparation removes unused legacy operation wrappers, prefixes sbtRel identifiers, uses one localhost transport and copies the original story, compilation and dependency plan into a fresh project. Request definitions and callback contexts are preserved; the original transport destination changes to the dedicated fixture.

This makes the models suitable for inspection and repeatable sampling while retaining their long scenario context. It is not a new minimal handwritten test. Original archived stories remain the authoritative account of discovery. Regeneration from the frozen source and exact profiles is separate from replaying an archived model.

| Case | Live workflow supplied | Verification basis |
| --- | --- | --- |
| F01 addition | Generated functional story | Signed contribution arithmetic and readback |
| F02 food removal | Generated functional story | Fresh recipe total and remaining list aggregate |
| F02 unit removal | Generated functional story | Fresh recipe total and association removal |
| F03 copy reference | Generated functional story | Internal reference membership in the copy |
| F04 unavailable reference | No new live reproducer | Original archive qualification |
| F05 household state | No new live reproducer | Original archive and owner read qualification |

F04-recorded and F05-recorded use the same shared interface file to emit recorded assertion events without HTTP. Their small literal summaries are explanatory examples, not cryptographic or independent evidence verification. Use Verify-Evidence.ps1 for the authoritative original data checks. A recorded assertion pass must never be labeled a new successful live reproduction.

## 6 Functional execution and expected outcomes

Prepare and sample one functional case, then replay it against the dedicated fixture:

```powershell
& (Join-Path $review 'scripts\Run-Functional-Reproduction.ps1') `
    -Case 'F01-addition' `
    -Username 'YOUR_DEDICATED_FIXTURE_USERNAME'
```

Other case values are F02-food-removal, F02-unit-removal and F03-copy-reference. Run one at a time and inspect its outcome before launching another. Each invocation creates a new local project under runs, samples one complete dependency valid schedule, records a sample audit, then prompts for credentials. The existing runtime execution tool audits model and sample hashes before replay. No automatic retry or resource cleanup is performed.

The wrapper limits Java heap to 1 GiB for this attempt. Successful symbolic sampling does not guarantee sufficient memory for live execution; Java, Python, Docker, browsers and the operating system all consume memory. The new F01 sample measured approximately 2.54 MiB, compared with earlier gigabyte scale serialized samples. This is an observed symbolic sample size, not a guarantee for every regenerated scenario or live run. The wrapper replaces JAVA_TOOL_OPTIONS temporarily and restores the previous value, avoiding accumulated duplicate heap arguments.

A defect reproduction is established by matching response bodies and invariant failure, not by a nonzero exit code. The wrapper deliberately stops and points to the evidence on failure. Authentication 401, connection failure, a missing sample, disk exhaustion or incomplete receipt must be classified as infrastructure or fixture problems. If a full run passes, report a nonreproduction under that recorded environment rather than claiming the historic evidence was false.

### Finding specific interpretation

For F01, compare aggregated list and recipe quantities at the first failed contribution. The original anchor is 17 + 0.5 × 4 = 19, observed 20. Newly sampled schedules may expose the same family at another quantity; compare the equation, not just a hardcoded scalar.

For F02 food, the original anchor is 15 − 4 = 11, observed 9. For F02 unit, it is 13 − 6 = 7, observed 11. Inspect all equivalent rows and recipe associations. A row layout change alone is not an arithmetic defect.

For F03, examine the duplicate response and later GET. Identify ingredient referenceId values in the copied object, then test membership of each instruction ingredient reference. A changed display string alone is not the defect, and the original display oracle correction must remain applied.

Archive the first failing review before any further attempt. Preserve the plan, actual selected order, first mismatch, original outputs, accepted sample hashes, environment and fresh identities. Later runs are confirmations of the same group until evidence demonstrates a different cause. Do not count two schedules as two bugs.

## 7 Generator preservation and regeneration

The full available generic source snapshot is included, together with the pinned Mealie contract, compatibility contracts, optional profiles, renderers, validators and historical validation records. It is not a claim that the snapshot exactly matches every historical working directory. Archived native review models and earlier source snapshots in the quantity freeze retain campaign provenance independently.

From the frozen generator directory, inspect available arguments and generate a static baseline:

```powershell
Push-Location (Join-Path $review 'source\generic-generator')
try {
    python -m generator_v56 generate --help
    python -m generator_v56 generate `
        --openapi .\compatibility\contracts\mealie.json `
        --output ..\..\validation\static-baseline\spec\js `
        --name mealie `
        --base-url http://127.0.0.1:9928 `
        --seed 2 `
        --story-profile parallel-crud
    if ($LASTEXITCODE -ne 0) { throw 'Generation failed.' }
} finally { Pop-Location }
```

For relationship compilation, use the --resource-maps, --relationship-profile, --compile-relationships and --relationship-runtime options with the exact retained profile pair for the intended case. Consult each archived generation_report and plan rather than inventing a profile from the finding label. Profiles define semantics and seeds; the contract alone will not reconstruct investigator choices. Do not replace source with the historic package version merely because the base version string is unchanged.

Backward compatibility evidence in the frozen tree compares earlier and separated transport generation on existing profiles, including 466 lifted request sites in a Node stub. Those records support preservation of request arguments and callback effects within their test scope. They do not establish full compatibility with every service version, live runtime or profile added afterward. This freeze did not rerun every historical regression suite.

## 8 Integrity archival and Git workflow

The byte manifest covers shipped files except itself and mutable validation outputs. Original archives are never rewritten to repair classification. Corrections belong in separate qualification files. Local credentials, runtime secrets and new unreviewed run outputs must not be staged automatically.

The package Save script verifies evidence, stages only supervisor-review-20261005, excludes mutable validation outputs, commits only the package directory and verifies the remote SHA after pushing. It checks tracked changes already staged outside that directory and refuses to mix them into the archive. It does not delete other untracked work, rewrite history or force push.

```powershell
& (Join-Path $review 'scripts\Save-Supervisor-Review.ps1') -Push
```

On the other machine, preserve any local edits, then pull with --ff-only, install Git LFS if the repository requires it, and run Verify-Evidence.ps1 again. Matching Git commits synchronize tracked package bytes; they do not synchronize live Docker data or recreate fixture state. If pull reports divergence, retain both histories and resolve it deliberately rather than running a destructive reset.

## 9 Failure diagnosis and operational limits

| Symptom | Interpretation and response |
| --- | --- |
| Authentication 401 | Verify dedicated fixture account and input; do not count a semantic finding |
| Cannot connect | Check Docker and the dedicated port; preserve output |
| Native sample absent despite process exit zero | Sampling was not accepted; no live execution |
| Checksum mismatch | Preserve files and inspect transport or line endings; do not rewrite originals |
| Nonzero native run exit | Read the first actual failure and response evidence |
| Owner read missing or fixture differs | Qualification incomplete; do not infer a boundary defect |
| Disk or memory exhaustion | Infrastructure failure; preserve partial evidence and resource metadata |
| Recorded story passes | Recorded summary accepted only; no new live result |

The shared interface preparation has passed JavaScript syntax checks and native symbolic sampling. The four original evidence validators passed during packaging. No new live request was sent by package validation. Windows PowerShell startup, fresh fixture setup and live defect replay remain operator checks. Original reset replay, minimality and restart persistence are not retroactively established by this package.

## 10 Acceptance criteria and outstanding work

A supervisory evidence review can proceed when the manifest and independent validators pass, the finding table matches the original observations, and cause hypotheses and novelty qualifications remain explicit. A fresh functional reproduction additionally requires captured environment identifiers, validated contract, successful authentication, complete dependency audit and the same semantic invariant failure with new owned identities.

Outstanding items include effective runtime household policy for F05; exact source to deployed binary linkage for historic runs; candidate fixes and matched regression controls; minimized sequences; clean isolated reset replay; process restart durability; licenses for any external binary distribution; and anonymization before public dataset release. These items were added because they affect reproducibility and research credibility even though they were not all requested initially.

The current delivery closes documentation and evidence packaging. It does not certify all pending live qualification work as complete. Before publication, obtain maintainer feedback on exact issue equivalence and route security relevant disclosures through the project's appropriate channel. No issue or message has been sent by the packaging process.
