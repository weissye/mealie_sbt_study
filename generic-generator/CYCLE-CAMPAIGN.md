# Expanded generic relationship cycle campaign

## Scope

The original OpenAPI generator now has an additive `verify_cycle_members` boolean
in a qualified recursive relationship policy. Omit it or set it to false to retain
the source-only rejection check. Legacy generation without relationship compilation
retains its existing output and CLI behavior.

The new example profile `profiles/mealie-relational-cycle-expansion.json` selects
the same seven resource types with five instances each. The generated positive
recipe reference chain is R1 -> R2 -> R3 -> R4 -> R5. Separate rejected attempts
close cycles of lengths 5, 4, 3 and 2. No preexisting cycle is assumed.

Every negative task with member verification executes as one serial task:

1. Fresh GET of every non-source cycle member, retaining its entire JSON response.
2. Fresh GET of the source, validation of the observed positive path and request projection.
3. PUT attempting to close the cycle, retaining its actual status and error body.
4. GET of the source and complete JSON equality against its pre-update snapshot.
5. GET of every other cycle member and complete JSON equality against its own snapshot.
6. Acceptance only after all declared members were read and verified unchanged.

Object key order is ignored; array order is preserved. Full response equality is
intentionally strict. A changing timestamp or other field is a candidate for
investigation, not a proven application bug. The observable boundary is the recipe
GET responses, not every internal database table or all other resources.

All HTTP remains in interfaces. Stories coordinate serial tasks and allow different
orders among ready actors. There is no simultaneous HTTP execution. Recursive
creation prerequisites remain rejected rather than silently removed.

## Model size

Each expanded run has 35 owned resource instances, 93 tasks and 304 HTTP callbacks,
including 4 negative cycle tests and 20 additional member GET callbacks. Categories,
tags, foods, units and shopping associations continue to exercise shared resources
and many-to-many relationships. Existing native source-only acceptance remains
historical evidence; this new model requires its own native acceptance.

## Run on Windows

Download the delta ZIP into Downloads. Unpack it first:

```powershell
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\generic_generator_cycle_campaign_delta.zip" -DestinationPath 'C:\work\temp\mealie_sbt_study' -Force
Set-Location 'C:\work\temp\mealie_sbt_study'
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
Get-ChildItem '.\scripts' -Filter '*.ps1' -File | Unblock-File
& .\scripts\Run-Generic-Relationship-Cycle-Campaign.ps1 -Username 'changeme@example.com' -Runs 3
```

For a smaller first run, use `-Runs 1`. Single-run acceptance is explicitly labeled
`EXPANDED_SINGLE_RUN_PASS` and does not claim schedule variation.

The wrapper first runs compatibility checks once. For each run it generates a new
project from the original generic generator, samples one native random schedule and
executes SampleId 1. Generation seeds 201 onward vary generated request values;
they are not native scheduler seeds. The native sampler is not pinned to a seed.
Actual task orders are retained and compared. Multiple runs are accepted as a varied
campaign only if at least two distinct orders were observed. Repeated identical
orders produce `EXPANDED_CAMPAIGN_NO_SCHEDULE_VARIATION`, preserving individual
accepted run results without claiming additional scheduling coverage.

Each live run prompts for the password. A failing run stops the campaign and retains
its evidence. Previously completed runs remain recorded. There is no automatic retry,
rollback, deletion, reset or cleanup. Three complete runs create up to 105 owned
resources and send 912 scenario HTTP requests. The native serialized sample files can
be large; each run samples only one and those files are excluded from review ZIPs.

## Evidence

Upload `Downloads\generic_relationship_cycle_campaign_review.zip` after execution.
It contains `campaign-acceptance.json`, the campaign manifest and small review ZIPs
for every started project. The collector sends no server requests. It independently
checks model hashes against sampling evidence, task prerequisites, native exit status,
complete runtime counts and exact unchanged-state evidence for every cycle member.
A duplicate project cannot count twice as an independent run.

A successful bounded campaign does not prove general correctness. Rejected cycles
with unchanged members are correct behavior for the qualified policy, not bugs.
Accepted invalid cycles, server errors and partial writes are recorded as failures
requiring independent diagnosis. Removal/relink scenarios and full reset/replay are
not implemented by this increment.

## Local validation

Python regression and Node stub checks cover source and target partial writes,
unexpected acceptance and 500 responses, unique member receipts, fresh GET ordering,
three different simulated task orders, missing native evidence, modified models,
duplicate projects and review packaging. These are local tests; native Provengo and
PowerShell execution must be validated on the Windows machine.
