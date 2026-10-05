# Stateful API Testing of Mealie with Provengo

Research report for supervisory review

Evidence freeze 5 October 2026

## Abstract

This case study examines how contract driven scenario generation and behavioral scheduling expose defects in a recipe management service. The retained Mealie evidence contains five finding groups: incorrect shopping list quantity increments, incorrect decrements after resource merges, dangling internal references after recipe duplication, unhandled unavailable recipe references, and shopping list changes retained after a failed operation across household boundaries. Five groups do not establish five independent implementation defects. In particular, the addition and removal manifestations may have a common quantity accounting cause.

The evidence supports repeatable observable failures, rather than an exhaustive assessment of Mealie. It includes generated models, native Provengo execution records, response bodies, independent receipt checks and checksummed original archives. Provengo supplied dependency constrained schedules and repeatable execution; explicit semantic and identity policies supplied the test oracles. No measured comparison with another testing method was performed. Global novelty, minimal reproduction and full clean reset replay remain unestablished. The household finding proves a recorded state change after HTTP 500; its final authorization classification also requires the effective household policy.

## 1 Study scope and research questions

The system under study is Mealie v3.28.0. The study used an existing generic OpenAPI generator, extended through optional relationship analysis and explicit profiles. Generated stories describe logical tasks and prerequisites. Generated interfaces implement HTTP, authentication, runtime binding and response validation. Native Provengo samples eligible task orders and replays one operation at a time. These experiments investigate sequential stateful composition, not simultaneous HTTP requests.

The questions are: Which state invariants fail after legal resource compositions? What additional behavior becomes visible when identities and ownership scopes vary? Which part of discovery is attributable to behavioral scheduling, and which requires domain knowledge? How far do independent evidence checks support defect classification and cause hypotheses?

The unit of analysis is a finding group. A second execution or another task order is a reproduction of a group, unless evidence establishes a distinct mechanism. An HTTP error alone is insufficient to establish the quantity or state corruption findings. Conversely, an HTTP success alone is insufficient to establish correctness of a copied object graph.

### Finding inventory

| ID | Observable finding | Evidence strength | Cause qualification |
| --- | --- | --- | --- |
| F01 | Incorrect quantity increment with repeated ingredient keys | Repeated, with narrower controls | Quantity accounting hypothesis |
| F02 | Incorrect decrement after food or unit merges | Repeated, with no merge controls | May share F01 cause |
| F03 | Copied instructions retain source ingredient references | Two fresh reproductions and object reads | Identifier remapping supported by code inspection |
| F04 | Unavailable recipe reference yields unhandled HTTP 500 | Foreign and absent reference observations | Unhandled lookup failure supported by logs |
| F05 | Another household list changes despite HTTP 500 | Four fresh directional observations | Partial state update proven; permission policy still to qualify |

## 2 Method and evidence controls

OpenAPI parsing supplies operation shapes, request schemas, response schemas and candidate dependencies. An explicit profile supplies semantic relationships that cannot be inferred reliably from a contract: contribution arithmetic, canonical merge keys, protected fields, actor scope and expected response policies. A compiler emits actors, interface functions and a dependency plan. Provengo samples the model; the sample audit requires complete task admission, dependency order, completion and model hashes. Live callbacks record returned identities and observations. Independent Python validators inspect the original archived receipts.

Fresh runs use different resource identities. This reduces contamination from earlier fixtures and supports repeatability, but it is not a substitute for a documented empty database reset. Independent validators reduce reliance on a single callback implementation. They remain dependent on the retained HTTP responses and may share assumptions with the original oracle. Checksums establish byte integrity, not truth of an observation or completeness of capture.

The quantity family freeze contains 24 native runs: 18 semantic discrepancies and six successful runs. Authentication failures are excluded. These counts combine discovery and controls selected adaptively, and are not a statistical estimate of failure probability. Earlier successful construction campaigns are contextual evidence, outside that denominator. The copy campaign contains eight runs; corrected qualification yields six passing runs and two internal reference findings. Four original display related candidates were false positives, retained and explained rather than deleted.

The first identity campaign contains four complete runs and 206 responses. The subsequent scope control campaign contains four complete runs and 186 responses. These are different campaigns, not additive estimates of unique bugs. Sampled but unexecuted suffixes do not constitute live coverage.

### Quantitative quantity oracle

For each canonical food and unit key k, the list quantity should satisfy Qafter(k) = Qbefore(k) + a × Rbefore(k), where a is the signed recipe contribution and Rbefore is the freshly read recipe quantity for that key. Aggregation sums all rows with the key, so splitting or consolidating rows does not itself cause failure. Floating comparison uses the configured tolerance, 1e−8. The list recipe association quantity is checked independently. A correct association with an incorrect ingredient total is a meaningful partial consistency failure.

### Identity and copy oracles

The copy invariant is local referential closure: each instruction ingredient reference must resolve to an ingredient referenceId in the same copied recipe. Source and copy identities are distinguished. Scope checks compare explicit actor identities, group and household identifiers, permission flags, permitted positive controls, rejected reads, mutation responses and owner authorized reads. The household result is conditioned on the recorded sequence and selected protected fields; it does not establish the absence of all other state changes in the server.

## 3 F01 Incorrect shopping list increments

### Observation and impact

The discovery scenario produced two ingredients sharing the same food and unit after a merge, each with quantity 2. Their aggregate recipe contribution was 4. A list quantity of 17, increased by half of that recipe, should become 19. The observed total was 20. The recipe association changed correctly from 1 to 1.5, while the ingredient aggregate was excessive. This represents inconsistent accounting within a successful stateful workflow, potentially causing an incorrect shopping quantity.

Two fresh executions with different semantic orders reproduced the discrepancy. Narrower controls reproduced it with duplicate keys without a preceding merge, and without the earlier decrement. Single ingredient controls passed. These observations narrow the trigger to repeated canonical ingredient keys and scaling; they do not make merge itself a necessary condition.

### Cause interpretation

The observed excess is compatible with applying the requested scale to one contribution while leaving another contribution unscaled. This is an arithmetic hypothesis, not a proven internal execution trace. No patch and regression result establishes the precise faulty statement. The control evidence supports a smaller causal explanation than the original long scenario, but does not establish a formally minimal reproducer.

### Contribution of Provengo

Provengo composed creation, binding, merge and contribution tasks under prerequisites and executed different eligible orders. Runtime reads made the numerical discrepancy observable after a sequence whose individual API calls could otherwise appear successful. The domain arithmetic oracle was essential: neither OpenAPI nor scheduling alone predicts the correct total. Necessity of Provengo relative to a handwritten sequence was not tested.

## 4 F02 Incorrect decrements after merges

### Observation and impact

In the food lifecycle, both fresh runs completed two merges and then removed one recipe contribution. Before removal, list total was 15 and the freshly read recipe total was 4. Expected remaining total was 11; observed total was 9. The remaining association was correct. In the unit lifecycle, the list changed from 13 to 11 after removing a recipe whose fresh total was 6. Expected total was 7. No recipe associations remained, yet excess quantity 4 remained.

Narrower single merge controls also left total 9 where manual baseline 7 should remain. Food controls retained a distinct quantity 2 item; unit controls retained an excessive aggregate. Four no merge integer schedules completed add, remove, readd and remove with final manual total 7. Four single merge controls failed. Their histories are not perfectly matched, so this is supporting contrast rather than a controlled one factor ablation.

### Cause interpretation and grouping

The evidence implicates inconsistency between current canonical ingredient identity, stored list contribution history and decrement accounting. It does not identify which representation or statement is wrong. F01 and F02 are retained separately because their observable transitions differ, but counted conservatively as one potentially shared quantity defect family. Calling all schedules separate bugs would inflate the result.

### Contribution of Provengo

The scheduler made merge placement relative to contribution operations explicit and preserved the completed prefix. Fresh pre mutation recipe reads prevented reliance on an obsolete cached recipe. The independent validator recomputed signed deltas. Runs stopped on the first semantic mismatch; later readdition stages were not executed in failed runs. No claim of complete lifecycle coverage follows from the planned suffix.

## 5 F03 Dangling references in a duplicated recipe

### Observation and impact

Recipe duplication returned HTTP 201. The copied ingredients had newly assigned referenceId values, while an instruction ingredient reference retained a source ingredient identifier absent from the copy. The copied response and a subsequent read exhibited the inconsistency. Two fresh reproductions support the same finding. A successful creation response therefore contained an internally inconsistent graph.

The direct impact is loss of local referential closure. A user interface consequence is plausible from the reference lookup design, but was not measured through a browser interaction in this evidence. No unintended sharing of protected source content was established by this finding.

### Cause interpretation

Inspection of pinned duplication service code supports the hypothesis that ingredient reference identifiers are reassigned without applying a corresponding old to new mapping to instruction references. This connects a concrete transformation to the observed invariant violation. It remains a source supported cause hypothesis until a fix and controlled regression demonstrate that the remapping is sufficient.

### Oracle correction and contribution of Provengo

The original campaign also flagged display field differences. Qualification identified an exclusion error in the validator: the recipeIngredient[].display exclusion was applied incorrectly when checking root membership. Corrected analysis classified six runs as passing and retained the two internal reference findings. Original archives and the correction are preserved. This episode shows why a failing callback is a candidate, not a final conclusion.

Provengo supplied source first and copy first stateful orders, fresh bindings and returned object observations. The finding depended on checking nested reference consistency, not only status codes. The retained functional reproduction uses an archived generated story with a shared transport interface; it is not claimed to be minimized.

## 6 F04 Unhandled unavailable recipe lookup

### Observation and classification

Two regular users in separate groups triggered four HTTP 500 manifestations in the initial identity campaign. Subsequent reference controls exercised both foreign group recipes and absent recipe identifiers in two fresh runs. These produced eight further 500 responses; absence controls returned 404 for reads. Positive controls using each actor's permitted list and recipe succeeded. Elevated administrator behavior is therefore not the intended explanation for these probes.

The retained server log reports UnexpectedNone with Recipe not found. Foreign and nonexistent references are currently grouped as one unavailable lookup error handling family. Their semantic causes differ, but the exception path may be shared. No exact global root cause count is established.

### Cause and impact limits

A group filtered lookup followed by an uncontrolled missing result is consistent with the exception and status behavior. The observations establish unhandled failure handling rather than an accepted foreign reference. Selected state checks found no change for these reference controls. They do not establish server wide atomicity, confidentiality exposure, or sustained service unavailability. A 4xx policy should be established against the API's intended behavior before specifying the exact replacement status.

### Contribution of Provengo

Changing the identity assignment made a previously valid composition invalid by scope. The same task vocabulary could express permitted controls and unavailable references, with actor bindings checked at runtime. The independent analysis separated lookup failure from the list mutation finding below. The package supplies offline verification for this group; it does not provide a new live boundary violation reproducer.

## 7 F05 Persisted list change after failed cross household operation

### Observation

The scope campaign used two ordinary users in the same group and different households. Recorded admin and management permission flags were false. Reading a recipe from the other household and adding it to the actor's own list succeeded, providing a permitted sharing control. Reading the other household's list returned 404. An attempted change returned 500.

An authorized read by the list owner then showed that the same list had grown from two items to three. Exactly one new item identifier appeared with quantity 2, the actor recipe identifier and the victim household identifier. Previously existing item objects were unchanged. The root recipeReferences collection was unchanged, indicating that the operation did not complete consistently across representations.

The archived order contains one recorded mutation of the victim list between the baseline and owner read. Other intervening mutations target a different list identifier. This occurred in two fresh samples, in both directions, yielding four observations of one finding. Logs report a NoneType error accessing list_items, distinct from the unavailable recipe exception.

### Interpretation and outstanding qualification

The evidence establishes a retained state change after an HTTP error and a mismatch between read visibility and observed mutation behavior. Here retained means observed by the later authorized GET; it does not mean persistence across process restart was tested. The service may have committed an intermediate update before a later lookup or cleanup failed. Transactional sequencing is a plausible explanation, not a database trace.

The private household default in repository code is not proof of the effective fixture policy. Final classification as unauthorized modification requires the actual runtime preferences and intended write policy. The result is therefore reported as a strongly reproduced state and boundary discrepancy, with authorization qualification open. Minimization, a clean reset replay and restart durability remain pending. These limits do not erase the observed change after failure.

### Contribution of Provengo

Actor specific execution and subsequent owner reads exposed a cross identity state consequence that a status only test would miss. Directional repetition tested both identities and reduced the likelihood of a fixture specific artifact. The key mechanism is identity aware sequential composition, not simultaneous requests. The package retains the original observations and independent verifier rather than generating an additional live boundary violation tool.

## 8 Related reports and novelty assessment

The review is a bounded search of public Mealie issues and relevant source, completed on 5 October 2026. It is not an exhaustive maintainer triage or proof of first discovery. An issue marked closed, or a related merged fix, does not establish that the present v3.28.0 manifestation is fixed or identical. No public issue was filed on the user's behalf.

| Finding | Closest retained public context | Relationship to this evidence |
| --- | --- | --- |
| F01 and F02 | Issues 3624 and 3417 | Related merging and list aggregation area; exact arithmetic failure not established as a duplicate |
| F03 | Issue 3956 | Dangling ingredient instruction links after deletion; different trigger from duplication |
| F04 | No exact match identified in bounded review | Novelty unresolved; absence in this search is not absence in the tracker |
| F05 | Issue 7072 | Related persisted state after failed mutation; different resource, operation and ownership setting |

Issue 3624 reports a merge failure caused by a shopping list foreign key constraint in v1.6.0. Our quantity manifestations follow completed compositions and incorrect arithmetic, so the report is related rather than an exact match. Issue 3417 concerns failure to consolidate equivalent list items; our aggregate oracle sums equivalent rows and does not treat unconsolidated rows alone as a failure.

Issue 3956 concerns instruction links retained after an ingredient is removed in v1.10.2. It supports the importance of local reference integrity but does not establish that duplication with new identifiers is the same defect. Issue 7072 describes invalid ingredient state retained after a failed recipe PATCH. It is evidence of related failure atomicity problems, not confirmation of the household list mechanism.

## 9 Validity threats and research interpretation

Internal validity is limited by adaptive campaign selection, partial state observations and absence of clean reset replication. Fresh identities reduce some carryover but do not eliminate all shared configuration effects. Source inspection and logs support hypotheses without substituting for a repair experiment. Changed oracle versions can alter classification; original and corrected classifications are therefore both retained.

Construct validity depends on explicit profiles. OpenAPI describes shape more reliably than ownership and arithmetic semantics. A permission expectation must match effective policy. Derived display fields should not be equated automatically with protected semantic content. The corrected copy analysis demonstrates this distinction.

External validity is limited to one application version, recorded fixture settings and selected operations. The study did not cover all 266 contract operations or all dependency edges. Sampling is not exhaustive state exploration. Reproductions with different task orders do not imply independent defects, and sample count does not measure the application's overall defect rate.

Provengo's contribution is demonstrated as an implemented means of composing and executing eligible stateful schedules while retaining ordering evidence. The data do not establish that another method could not find these defects, a speedup over another tool, or that generation alone discovered the semantic oracles. A comparative study would require equal budgets, matched fixtures, defined detection criteria and recorded investigator effort.

## 10 Research outcome and next qualification work

This freeze establishes five reproducible finding groups and preserves their evidence without claiming five independent causes. It provides a defensible account of quantity inconsistencies, copied object graph corruption, unavailable lookup handling, and a state change after failed boundary sensitive execution. The contribution is the combined workflow of generic contract extraction, explicit semantic profiles, behavioral scheduling, runtime binding and independent evidence qualification.

The next research work should be qualification rather than broader exploration: obtain the effective household policy; establish a minimized sequence and isolated baseline for each distinct family; capture full mutation and owner read responses; test a candidate repair against the original and passing controls; and distinguish live reset reproducibility from offline archive reproducibility. These are outstanding tasks, not completed results.

## References and data availability

R1. Mealie issue 3624. Merging ingredient does not work if referenced by a shopping list. https://github.com/mealie-recipes/mealie/issues/3624

R2. Mealie issue 3417. Shopping list items of the same type are not consolidated. https://github.com/mealie-recipes/mealie/issues/3417

R3. Mealie issue 3956. Removing a recipe ingredient does not remove its links to steps. https://github.com/mealie-recipes/mealie/issues/3956

R4. Mealie issue 7072. Failed recipe PATCH can persist ingredients with a null reference identifier. https://github.com/mealie-recipes/mealie/issues/7072

R5. Mealie v3.28.0 source. https://github.com/mealie-recipes/mealie/tree/v3.28.0

R6. Mealie installation documentation. https://mealie.io/documentation/getting-started/installation/sqlite/

Public references accessed 5 October 2026. Primary study data are the original campaign archives under evidence, the historical reports, and the independently checked qualification records in this package. The current archival commit reported by the operator is c89f412a35492a03a231d9d189caa3714afb7864. That identifies the previously pushed scope findings, not a push of this new package. PACKAGE-SHA256.json links every included file to this freeze. The package is intended for private supervisory review; original observations include fixture identifiers and must not be treated as an anonymized public dataset.
