# Reference deletion qualification and continued use

This is a new mechanism, not another quantity/merge permutation. It is an
opt-in extension of the original generic OpenAPI generator. HTTP stays in
`interfaces`; `stories` schedules contract-bound symbolic tasks. Calls are
sequential. No simultaneous HTTP dispatch is introduced.

## Campaign

| Case | Samples | Complete HTTP requests per sample |
|---|---:|---:|
| Food: matched control without deletion | 2 | 100 |
| Unit: matched control without deletion | 2 | 100 |
| Food: delete while referenced | 2 | 101 |
| Unit: delete while referenced | 2 | 101 |

Eight complete runs total 804 requests, including authentication, bootstrap,
creation and readbacks. Each run creates twelve owned resources: three foods,
three units, three recipes, three shopping lists. There are no merges, no
fractional recipe multipliers, and no quantity-conservation oracle in this
campaign. Existing quantity evidence is untouched.

Two recipes share target #1 and another live target #2. Recipe #3 uses target
#3 and is an unrelated control. An explicit, generic
`target_indices_by_source` binding table expresses these occurrence choices.
The structural recipe relationships are complete before the probe. One
recipe/list association is built before it, while two further associations
are deferred until after it. This is mutation during shopping-association
construction, not arbitrary mutation at every possible construction point.

For the selected target, the generated program:

1. GETs the target, all three recipes and list association controls.
2. Attempts DELETE in the delete case; the matched control omits that request.
3. GETs the target and all recipe/control views again.
4. Updates the first surviving recipe's description through GET/PUT/GET,
   asserting that its protected ingredient state remains intact.
5. Rebinds precisely the original target's ingredient occurrences to live,
   independently read target #2, through GET/PUT/GET.
6. GETs the old target again to detect disappearance or resurrection.
7. Continues the remaining recipe/list association construction and readbacks.

## Explicit qualification, not an invented API guarantee

OpenAPI identifies the operations, response identities, nullable nested paths
and writable schemas. It does not establish deletion semantics. The profile
therefore declares a **qualification hypothesis**:

- On documented DELETE success: the target's GET returns configured 404/410,
  and its nullable references become null. Other ingredient data and the
  unrelated recipe stay unchanged.
- On configured 400/409/422 rejection: the target and protected referring
  state remain unchanged.

These are separately recorded outcomes. A rejection alone is not a bug.
A mismatch is a candidate requiring policy/source review and fresh-resource
confirmation. Success with another intentional API policy, such as deleting
an entire ingredient occurrence, may invalidate this hypothesis rather than
prove a server defect. No source-code confirmation of the Mealie-specific
policy is claimed by this package. An observed 5xx on a selected non-authentication REST operation is retained
as a server-error candidate for fresh-resource confirmation. Other unknown
HTTP failures, authentication and transport failures stop the campaign.

The protected recipe view is its writable `recipeIngredient` projection,
including quantities, the companion food/unit relationship and occurrence
structure. Read-only fields are not compared. List controls protect recipe
associations, not every hydrated shopping-item food/unit view. Quantity
conservation, stale-ID insertion, full server reset/replay and cleanup remain
outside this campaign.

## Running on Windows

Extract the delta into the existing study root, then run:

```powershell
& .\scripts\Run-Generic-Reference-Lifecycle.ps1 -Username 'changeme@example.com'
```

The runner checks server version, at least 1 GiB free RAM and 1 GiB disk,
executes the existing compatibility suite, and asks for the password once.
Java is limited to 512 MiB heap. Chrome does not need to be closed if the memory
check passes. Native samples are guarded at 128 MiB; local two-sample tests
stay below 4 MiB. This does not guarantee a fixed total resident memory.

Both controls run first and must pass. Each candidate's first review is
retained unchanged, and the second sample creates fresh resources. The two
samples may choose the same task ordering; inspect sampling audits before
claiming order diversity. Two reproductions do not automatically mean two
bugs. The generated seed is recorded for reproduction. To specify one, pass
`-Seed`, using a new seed if an identical generated project already exists.

Each run has its own review ZIP and read-only classification. Finally, the
runner creates:

`Downloads\mealie-reference-lifecycle-<timestamp>\campaign.zip`

Upload that campaign ZIP. It includes generation, sampling, per-run review,
classification and campaign metadata. Existing review bundling deliberately
omits large serialized samples; original samples remain in the generated
project, and the sampling audit retains their hashes. No automatic retry,
rollback, deletion of pre-existing resources, Git push or database reset is
performed. The explicit DELETE probes operate on this run's owned targets.

## Validation and compatibility

Legacy profiles omit the new option and retain their generated JS/report
bytes. The release includes a pre-extension compiler snapshot for a direct
comparison, the established cross-profile regression suite and 466 transport
argument/callback equivalence checks. New checks execute serialized callbacks
under native Provengo against a local test HTTP fixture, covering healthy
success, healthy rejection, dangling references, unrelated mutations,
partial writes after rejection, ignored description updates and ignored
rebinds. Fixture results are not live Mealie acceptance.

New complete receipts are independently checked against their protected
baselines, branch outcomes, owned replacement identities and followup slot
transformations. A zero native exit alone is insufficient for acceptance.

## Derived display qualification fix

The first live no-delete control changed only `recipeIngredient[].display`
after replacing its food. That display correctly reflected the new food name.
The previous oracle incorrectly expected the old rendered text. Profiles now
explicitly omit this derived display path from protected equality. The generic
compiler does not hard-code Mealie fields. Identity, quantity, note, occurrence
structure and companion relationships remain checked. No deletion request was
sent by the stopped campaign and no new server bug is established.
