# Mealie discovery and reconstruction provenance v005

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
