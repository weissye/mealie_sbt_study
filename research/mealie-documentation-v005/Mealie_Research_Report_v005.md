# Mealie Stateful API Testing Research Report

Supervisor review version v005

Live evidence cutoff 8 October 2026 and provenance review 9 October 2026

Prepared for Yeshayahu Weiss and his research supervisor

## 1 Research questions thesis and findings

**RQ1 State dependent correctness.** Can dependency constrained, stateful API scenarios expose inconsistencies that are not visible from individual response codes or request schema validation?

**RQ2 Relationships and identity.** What additional observable failures appear when scenarios preserve resource relationships, change canonical identities through merges or copies, and distinguish actor, group and household scope?

**RQ3 Automation provenance.** Which stages are generated from OpenAPI, which depend on explicit semantic profiles or curated plans, and what evidence would justify a claim of automatic scenario discovery?

**RQ4 Evidence and repeatability.** Can generated JavaScript, native Provengo execution, returned state, independent archive analysis and server exceptions jointly support a defensible finding classification?

**RQ5 Comparative value.** Does the method improve detection or efficiency relative to another method under matched budgets? This question is proposed for future evaluation; the Mealie data do not answer it.

**Thesis supported by this case study.** Contract based extraction, explicit relationship and semantic modeling, dependency constrained scheduling, runtime identity binding and state based verification form an effective implemented workflow for exposing and qualifying stateful API failures. The current evidence supports this combined workflow. It does not establish that OpenAPI alone supplies the semantics, that Provengo is necessary for every finding, or that the method outperforms another tool.

The evidence contains five finding groups, F01 through F05. F01 and F02 concern inconsistent quantity accounting; they may share an implementation cause. F03 concerns broken internal references after copying. F04 concerns an unhandled unavailable recipe lookup. F05 concerns a list change observed after a failed cross household operation. Five groups therefore must not be reported as five independently established root causes.

| Group | Observable result | Research support | Current qualification |
| --- | --- | --- | --- |
| F01 | Scaled addition produces an excessive ingredient total | RQ1 and RQ2 | Repeated quantity inconsistency; internal cause remains a hypothesis |
| F02 | Removal after merges produces an incorrect remaining total | RQ1 and RQ2 | Repeated lifecycle inconsistency; may share F01 cause |
| F03 | Copied instructions refer to identifiers absent from copied ingredients | RQ1 and RQ2 | Two retained findings after correction of display related false positives |
| F04 | Unavailable references cause HTTP 500 and UnexpectedNone | RQ2 and RQ4 | Twelve historical observations; corresponding new failures have matching service frames |
| F05 | HTTP 500 is followed by an owner observed list change | RQ1 RQ2 and RQ4 | Four historical observations; corresponding new failures have matching service frames |

The strongest current claim is automated detection of previously unknown deviations through profile driven contract compilation and native execution, followed by independent qualification. The original F04/F05 automation is now corroborated by a historical source and receipt audit. Five finding groups are retained; a closed fresh replay package for five independent root causes is not established. Automatic unguided discovery from OpenAPI remains unproved.

## 2 Study design and units of analysis

Mealie v3.28.0 is the system under study. The recorded October 8 live server reports buildId 0552eaa4a80031b8572849cca0ed95d07f1be001 and SQLite. Historical reports identify the same release, but later metadata cannot retroactively establish the binary of every older execution. Server traces link the historical and new failures to corresponding installed Python service code.

The study proceeded adaptively: construction, observed discrepancies, narrower controls, copy qualification, identity campaigns, guard patch regression, and explicit generated model confirmation. This is an exploratory case study with targeted confirmation. It is not a preregistered random sample of all endpoints or a controlled tool comparison. Discovery runs and later controls have different purposes and should retain those labels.

A finding group is the primary unit of analysis. A run is an execution under recorded inputs and state. An observation is a particular mismatch or response. An independent root cause requires a causal distinction in code or repair behavior. These units are not interchangeable. Multiple sampled schedules can reproduce one group; multiple HTTP errors can have one cause; one run may stop before its planned suffix.

Logical interleaving means selecting an eligible task order among prerequisite constrained tasks. True concurrency means overlapping HTTP operations, with measured request intervals and a suitable oracle. The Mealie executions analyzed here are sequential. They support claims about stateful composition and schedule order, not concurrent race detection or linearizability.

Fresh UUIDs and namespaces provide separation from earlier resources and directional checks reduce reliance on one actor. They do not recreate an empty database. Effective configuration, shared database effects and surviving fixtures remain validity threats. No clean reset or restart durability experiment is inferred from fresh resource names.

## 3 Method and automation boundary

The generic contract stage extracts operation shapes, schemas, identifiers and candidate relationships. These outputs help produce syntactically valid calls and bind resources. They do not reliably specify contribution arithmetic, household write permission, canonical merge equivalence or how internal references should be remapped when an object is copied.

An explicit profile or plan supplies those semantic assumptions. The compiler maps tasks to contract operations and emits stories and REST interfaces. Provengo schedules and executes the model. Callbacks retain returned identities and compare state. Independent analysis qualifies archived receipts and contrasts findings with controls. This division of responsibility is central to the interpretation of results.

The current v016 reconstruction accepts explicit semantic intent and integrates model generation with production of the complete surrounding package. This establishes packaging integration and retained native execution acceptance. It does not invalidate the automated original discovery on 5 October. The historical discovery lineage and the current reconstruction lineage are evaluated separately; their full semantic correspondence is not yet established.

An OpenAPI-only autonomous scenario-inference claim would require a frozen generator revision, a declared input boundary, a complete record of supplied semantic rules and a held out evaluation showing that the target scenario was not manually inserted. A general rule may legitimately use additional relationship or permission metadata, but then the claim must say OpenAPI plus those declared inputs. The research contribution can remain meaningful without claiming a stronger input boundary than was implemented.

## 3A Original discovery automation established by historical review

The 9 October provenance audit distinguishes original discovery from later reconstruction. Original campaign multi-identity-20261005-065704 used seed 844524 and source commit f1f29cf5dad0991faa677d0cc98481f56ef5de28. Its four native runs completed: two shared configuration controls passed and two separate configuration runs produced identity candidates. The follow-up scope-controls-20261005-073218 used seed 264758 and source commit 81d332221c3f567044c9a15f85297cb064b08f69. Four additional native runs completed and supplied reference qualification and the F05 state observations.

All eight receipts have native exit zero and LIVE_CALLBACKS_COMPLETE; response counts equal task counts. Twelve source comparisons between the retained review snapshot and named Git objects match after line-ending normalization. A referenced source commit and matching review snapshot do not attest to the exact source installed during every historical Windows execution.

The original runtime profiles contain actors, bootstrap_actor, steps and checks. Across the four configurations and both samples, ordered step IDs and check declarations match the retained input profile. Compiled plans attach request schemas and contain two body differences per configuration; they are not byte-identical input copies. The compiler validates contract membership and bindings, constructs dependencies from response references and actor order, emits JS, and the runner samples and executes native schedules. These are substantive automatic stages.

The original detection was automated within an explicit semantic model. The unknown outcome was the server deviation, even though the intended test operations and expected behavior were declared before execution. This is a legitimate discovery claim with declared inputs. It is distinct from claiming that OpenAPI alone inferred the permission and state invariants. The later v014/v015/v016 reconstruction lineage neither establishes nor negates original automation. v016 integrates package production; cross-lineage equivalence requires separate evidence.

Earlier callback serialization and scope probes failed on 4 October. Their failure must not be transferred to the successful 5 October discovery runs. The retained original JS demonstrably executed in those accepted runs. Replacing historical JS with newer JS would create a new lineage; equivalence needs correspondence of tasks, bindings, prerequisites and oracle semantics, not simply a combined ZIP. No such replacement is performed in this update.

The evidence package is closed for the enumerated offline audit inputs and includes a runnable authorized positive control. It is not closed for every claim about all five findings: F01/F02 causal independence, complete fresh replay, patched live acceptance, and fully automatic semantic inference remain separate open questions.

## 4 Oracles and evidence logic

The quantity oracle aggregates all list rows with the same canonical food and unit key. It compares the observed total with a fresh recipe read and the signed contribution. In compact notation, expected after quantity equals before quantity plus signed contribution times current recipe quantity. The retained tolerance is 1e-8. Row splitting or consolidation alone is not a quantity failure.

Recipe association quantities are checked separately from ingredient totals. A correct association with an incorrect total is a consistency mismatch between two representations. An HTTP 200 or 201 is insufficient to establish semantic correctness. Conversely, a failed process is insufficient to establish a bug: authentication, transport, sampling and infrastructure failures must be classified independently.

The copy oracle checks local referential closure. Every instruction ingredient reference in the copy should resolve within the copied ingredient identifiers. This invariant is narrower and more defensible than requiring every derived display field to remain byte identical. An early display exclusion error caused four false positives, later corrected while preserving original evidence.

The boundary state oracle uses actual actor scope, positive sharing controls, response policies, snapshots and an owner authorized read. State equality is equality of selected normalized fields, not proof that every server table is unchanged. A retained change means observed in a later GET; persistence across a server restart was not tested. A 500 by itself proves neither rejection before mutation nor rollback.

Hashes establish integrity of supplied bytes, not observation truth or capture completeness. Server access paths and exception timestamps provide corroboration. They do not substitute for globally unique request IDs or a database transaction trace. The audit uses exact resource paths and bounded timestamp correlation, with the limitations recorded.

## 5 F01 Quantity addition inconsistency

The historical anchor contains repeated ingredient keys whose recipe aggregate is four. Before the disputed addition the list aggregate is 17. Adding half a recipe should produce 19; the observed aggregate is 20. The recipe association quantity changes as expected from one to 1.5. The inconsistency is thus within quantity accounting, not merely a missing association or row presentation difference.

Fresh executions with different eligible semantic orders retained the discrepancy. Narrower controls reproduced the issue with duplicate canonical keys without a prior merge and without an earlier decrement. Single ingredient controls passed. These comparisons narrow the hypothesis: merge is useful for creating a complex context but is not established as a necessary trigger for F01.

The current cause hypothesis is asymmetric scaling or aggregation of repeated contributions. The data support an arithmetic inconsistency, but they do not identify the exact faulty statement. No accepted F01 repair experiment is present. The engineering evidence must preserve the before quantity, fresh recipe quantities, contribution amount, observed aggregate and association state together.

F01 supports RQ1 because individually successful operations can leave mutually inconsistent representations. It supports RQ2 because canonical identity and aggregation affect the oracle. It does not show that a handwritten test could not reproduce the same behavior or that OpenAPI alone encodes the expected arithmetic.

## 6 F02 Quantity removal after merges

The food lifecycle anchor has list total 15 and fresh recipe total four. Removing one contribution should leave 11, but the observed total is nine. The unit lifecycle anchor has list total 13 and fresh recipe total six. The expected remaining total is seven, whereas the observed result is 11. In the latter case no recipe associations remain, yet an excessive quantity remains in list content.

Four no merge integer schedules completed their add and remove lifecycle with the expected manual total seven. Four single merge controls retained discrepancies. Their histories are not perfectly matched, so this is a supporting contrast rather than an isolated one factor causal experiment. Failed lifecycle runs stop at the first semantic mismatch; planned later operations do not count as executed coverage.

The evidence suggests inconsistent accounting across the current canonical recipe representation and list contribution history. A fresh read is important because a cached pre merge recipe could produce an incorrect expectation. F01 and F02 remain separate observable groups while their potential common cause is explicitly acknowledged.

The combined quantity freeze records 24 runs, 18 semantic discrepancies and six successful runs. These are adaptively selected executions and controls across the quantity family; 18 out of 24 is not a prevalence estimate. Authentication exclusions and earlier construction campaigns are outside this denominator. The artifact package includes the archived summaries and primary read only execution records for supervisory inspection.

## 7 F03 Internal reference corruption after copying

The copied recipe is returned successfully, but copied ingredient reference identifiers are newly assigned while an instruction reference retains a source identifier absent from the copy. The copy response and subsequent object read support the mismatch. Two fresh executions retain this internal reference finding.

The eight run copy campaign was requalified: six pass and two retain the internal reference candidate. Four earlier display related candidates became passes after an exclusion bug in the oracle was corrected. Reporting the original candidate count as confirmed bugs would be incorrect. The corrected classification is part of the evidence, not an inconvenient history to remove.

Historical source inspection supports an identifier remapping explanation: when child identifiers change, all internal references need a corresponding mapping. That explanation remains source supported rather than fix validated. The current audit does not establish a new live repair result for F03. A user interface consequence is plausible but was not measured through a browser.

F03 supports RQ1 by showing why a successful creation code cannot validate a returned object graph. It supports RQ2 through copy semantics and nested identity consistency. It also supports RQ4 negatively: candidate detection needs independent qualification, and oracle errors can create misleading findings.

## 8 F04 Unhandled unavailable lookup

The historical multi identity campaign records four error observations. The subsequent reference control campaign records eight more. Their request resource paths match 12 HTTP 500 records in the historical server export. Timestamp associated exceptions identify UnexpectedNone with Recipe not found. Foreign and absent references are grouped as one unavailable lookup error handling family.

The current server export closes an earlier evidence gap. Four corresponding observations from two native generated model executions match exact resource paths in the new access log. The exceptions match the historical class and message. Relevant service frames match shopping_lists.py lines 445 and 342, with the corresponding controller frames. The new behavior therefore corresponds to the documented failing code path, not merely a similar response code.

These are new transactions and new resources, not the identical historical incidents. The correlation is supported by request paths and exception timing rather than request IDs. This strengthens defect correspondence but is not a complete causal proof of every contributing condition. Positive controls and selected state checks do not establish absence of all possible side effects elsewhere.

F04 supports RQ2 and RQ4 by showing scope dependent failure handling and corroborated execution evidence. It is not evidence of accepted foreign content, sustained denial of service or confidentiality exposure. The exact intended replacement status needs a documented response policy rather than an assumption that one specific 4xx is mandatory.

## 9 F05 Retained change after a failed operation

The historical scope campaign contains two fresh samples in both directions. The actors are ordinary users in the same group and different households. A target list read returns 404, a mutation returns 500, and a subsequent successful owner read shows the list increasing from two items to three. Each comparison includes one new item identifier. The corresponding historical exceptions are AttributeError while accessing list_items.

The current export matches two corresponding generated model observations. Their exceptions have the same class and message as the historical finding. The installed service frames match lines 449, 219 and 134 in shopping_lists.py, ending in remove_unused_recipe_references. The client evidence reports an owner observed state change after the error. Taken together, these records establish correspondence with the earlier state and failure path finding.

The state change is directly supported; comprehensive authorization classification still needs the intended policy and effective runtime preferences. A denied read and different household IDs are strong context but do not, by themselves, prove every write permission rule. The report uses boundary discrepancy and retained change after failure as the unconditional observation. It does not claim persistence across restart or a proven database commit chronology.

F05 supports RQ1 because response status alone misses a retained mutation, RQ2 because separate identities and ownership aware readback reveal it, and RQ4 because client state and server exceptions corroborate the same event. This is sequential behavior, not a concurrent race.

## 10 Regression and positive control results

The v006 regression archive records nine baseline rejection test failures and three passing controls; the patched run records 84 passing tests. The historical interpretation notes that some baseline tests terminate at the server exception before comparing final state. Those failures support the exception path; they cannot independently establish the partial write measured in F05. A patched unit or integration result is not a live deployment acceptance result.

The proposed guard patch is preserved as defensive source. It is not claimed to fix F01 through F03. The present delivery neither installs it on the user's running server nor establishes a live patched server result. Build fingerprints and patch application status must be recorded separately whenever such a result is collected.

The v007 home positive control has 27 generated steps and 27 distinct callback passes, native exit zero and Test Result SUCCESS. It creates permitted shared resources and checks authorized quantity, reference and checked state transitions. This is a live pipeline acceptance control rather than a reproduction of F01 through F05. Its explicit semantic plan and additive compiler are retained unchanged.

The later two boundary executions each have 15 markers and native SUCCESS. Success here means the classified test model completed; it does not mean application correctness. The classification outcome and underlying HTTP results must be reported separately from transport acceptance or process status.

## 11 Contribution and threats to validity

The implemented contribution is a traceable pipeline joining contract extraction, explicit semantic assumptions, runtime binding, behavioral execution and independent evidence qualification. The case study shows three types of state reasoning: aggregate arithmetic, object graph closure and identity sensitive failure consequences. This gives concrete support for a stateful testing thesis without proving a broad discovery theorem.

Internal validity is threatened by adaptive selection, partial snapshots, carryover state and incomplete deployment fingerprints. Construct validity depends on justified semantic and permission expectations. External validity is limited to one application release and selected workflows. No comparative tool budgets, investigator time measurements or independent novelty confirmation are available.

Control results and fresh executions reduce some alternative explanations, but cannot remove these threats. F01 and F02 may share a cause. F03 demonstrates oracle correction. F04 includes a separate Oct1 disk I/O error that must not be counted in its 12 observations. Historical log corruption limits coverage after Oct5, whereas the new stdout and stderr export independently supplies the October 8 traces.

No claim is made about global novelty, maintainer acceptance, exhaustive endpoint coverage, true concurrency, minimal sequences or automatic unguided discovery. These restrictions are research qualifications, not reasons to discard the supported observations.

## 12 Next research phase and transfer evaluation

The next phase should test transfer of the method, rather than add more demonstrations of already known Mealie outcomes. Freeze the generic compiler, its input language and the current evidence before inspecting a new system. Separate a system adapter that maps operations, writable fields, authentication and references from generic rules that construct prerequisites, bind returned identities, explore eligible schedules and apply state invariants. Record every human supplied field and rule.

**Primary transfer question.** Can the unchanged generic engine produce accepted native models for a held out service with a bounded adapter effort, and expose qualified state discrepancies without inserting a known bug sequence? The existing Vikunja and Gitea installations reduce setup work, but prior experiments mean they are not wholly unseen systems. Hold out workflows and document prior investigator knowledge; later include a service not previously used to strengthen external validity.

Use Vikunja first for the sequential relationship track. Limit the first adapter to projects, tasks and labels in a namespace owned by the test account. Candidate invariant families are update/readback agreement, preservation of fields not selected for update, and referential closure of declared task-label relationships. Bind only capabilities actually present in the deployed contract and documented semantics. The previous true-concurrency work is a separate study and should not be mixed into this sequential evaluation.

Use Gitea second, starting with owned repositories, issues and labels. Keep initial coverage small and relationship based, expanding only after native transport and the independent oracle pass. NetBox is a later structural transfer case, but its earlier use also prevents calling it an unseen system. System choice is an investigator recommendation, not a claim that a future campaign will find a new defect.

| Phase | Concrete output | Acceptance gate |
| --- | --- | --- |
| Freeze | Engine commit, input-language schema, profiles and current evidence hashes | All supplied inputs are named and prior target knowledge recorded |
| Map one workflow | Contract fingerprint, catalogue, references and reviewed adapter | Every selected binding has contract or documented provenance |
| Validate compilation | Generated interfaces, stories and model report | Native model runs through complete authorized callbacks |
| Validate oracles | Local fixtures with correct state and deliberately inconsistent state | Correct fixtures pass; known injected inconsistencies are detected |
| Transfer pilot | Small sequential campaign with retained schedules and state reads | Setup, infrastructure failures and semantic candidates are separated |
| Frozen evaluation | Multiple independent seeds and documented start state | No post-outcome rule edits inside the accepted evaluation set |
| Comparison | Same boundary, budgets, state criteria and independent qualification | Native detections and common-oracle detections reported separately |

Begin with three pilot seeds to check model acceptance, then freeze again and use ten evaluation seeds per service and configuration. Suggested initial limits are 60 minutes and 10,000 HTTP requests per run, stopping at the first bound. These are proposed planning values, not executed results or power estimates. Record compilation, sampling and setup time separately from live test time, including requests used for provisioning and readback. Report distributions and uncertainty; do not turn ten seeds into a claim about service-wide bug prevalence.

## 13 Generalization evidence and ablations

The minimum transfer record is an immutable input manifest, API version and image fingerprint, engine commit, adapter/profile revision, generated model hashes, selected schedule hash, seed, execution receipt and independently qualified state observations. A contract pointer establishes where an operation came from; it does not establish that a semantic rule was inferred from that pointer.

Measure adapter authoring time, number of system-specific declarations, fraction of bindings resolved, accepted complete schedules, prerequisite and relationship coverage, achieved prefix length, readback completion, qualified finding groups and false positive rate. Record the first successful context and first qualified discrepancy in both requests and elapsed time. Early stop failures censor later task coverage.

Three ablations can test mechanisms without changing the observable correctness criteria: the full method, the same method with minimal prerequisite construction and no context-extension stage, and the same selected workflows with one fixed eligible order instead of schedule exploration. All arms should retain the same authorized resource namespace and external evaluation oracle. Where an ablation cannot create the target context, record unreachable context rather than treating it as a successful correctness result.

Ablations estimate the effect of the removed feature under the selected design. They do not prove that long prefixes or Provengo are necessary for each historical Mealie group. Actor count alone is not concurrency evidence; any future overlapping-request study needs its own coordinator, request timing and concurrency oracle.

## 14 Returning to Mealie for tool comparison

Return after at least two transfer workflows are accepted, the engine and oracle are frozen, and the comparison protocol is recorded before tool outcomes are inspected. Mealie then serves as a known-finding benchmark and a separate exploratory workflow set. Reproducing F01-F05 is known-finding confirmation, not fresh discovery. Every benchmark finding must meet the same evidence criterion regardless of which tool generated its requests.

Compare the full method with a simpler Provengo baseline, RESTler and EvoMaster in black-box mode. RESTler compiles OpenAPI and can use explicit annotations; EvoMaster supports black-box testing with an API schema. Freeze actual tool versions and settings rather than assuming current defaults reproduce earlier experiments. White-box instrumentation would introduce additional information and should be a separate arm.

Two comparison tracks avoid confusing extra semantic information with better exploration. The contract-only track supplies the same contract, allowed operation boundary, credentials and start state, and measures structural reachability and native detections. The declared-semantics track additionally supplies the same reviewed relationship and invariant information through a documented adapter or common independent evaluator. Account for the modeling effort of every tool and annotate any unsupported input capability.

Do not give a baseline the known failure sequence and call the resulting run a discovery experiment. Such a run can be a labeled transport or oracle sanity check. Conversely, do not give only our tool rich policies and interpret its semantic score as an input-equivalent comparison. Publish both tracks and their input differences.

The common evaluator must examine one recorded sequence at a time using only its captured bindings and state evidence. It must not combine unrelated sequences to create a counterexample. Report tool-native alerts separately from common-evaluator findings. A tool that receives a 500 has observed a server error; that does not automatically demonstrate the owner-visible state change relevant to F05.

Use matched request and wall-clock bounds, equivalent resource isolation, the same image/configuration, randomized tool order and a declared seed set. Count unique qualified groups, time and requests to first qualified finding, context reachability, validity rate, oracle availability and false positives. If required state evidence is absent, record NOT_EVALUABLE rather than confidently concluding that no semantic defect was present.

Official capability references checked 9 October 2026 are Vikunja API Documentation at https://vikunja.io/docs/api-documentation/, RESTler Compiling at https://github.com/microsoft/restler-fuzzer/blob/main/docs/user-guide/Compiling.md, and EvoMaster black-box documentation at https://github.com/WebFuzzing/EvoMaster/blob/master/docs/blackbox.md. These establish integration options, not comparative effectiveness. Pin the deployed API instead of replacing it with a live demonstration service schema.

## Appendix Evidence register

E01 Historical supervisory archive, dated 5 October 2026. All 371 manifest entries verified in this preparation. Quantity freeze, copy requalification and historical reports are extracted under evidence/historical.

E02 Quantity primary records under evidence/primary. The freeze summary has 24 runs, 18 discrepancies and six passes. Reported causal hypotheses are distinct from these counts.

E03 Historical identity and scope receipts under evidence/historical and evidence/historical exports. Original archive provenance and any exported transformations are recorded.

E04 Historical server export under evidence/server/historical. Audit v001 matches 16 selected request paths and exceptions; the separate disk I/O observation is excluded.

E05 New native execution records under evidence/new. The supplied source package manifest had 349 of 349 matching hashes in the prior audit. The current artifact deliberately includes read only records rather than active boundary runners.

E06 Current server export under evidence/server/current. Audit v002 links six exact paths to exceptions and service frames; stdout and stderr must both be retained.

E07 Live home review_v007.zip and the published positive control source under positive. These establish pipeline acceptance with 27 callbacks.

E08 Regression v006 archive and defensive guard patch. The archive supports recorded baseline and patched test outcomes, with no implied patched live acceptance.

Evidence references are local artifact paths so that the claims can be evaluated offline. Public literature superiority and novelty claims are not part of this report.

E09 Original discovery automation audit under evidence/discovery. Eight complete native receipts, eight profile-to-plan comparisons and twelve source text matches corroborate the original compilation and detection lineage. The reviewed source snapshot is not an exact installed-source attestation.


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
