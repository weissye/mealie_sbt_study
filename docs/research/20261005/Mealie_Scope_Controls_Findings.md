# Mealie multi-account confirmation review

Review date: 2026-10-05. Observed server version: v3.28.0.

## Experiment lineage

The accepted study uses two regular users with separate credentials. An administrator bootstraps users and scopes. Shared-household cases provide positive controls; separate-group cases exercise isolation. The follow-up separates foreign recipe references from missing references and separates household boundaries from group boundaries.

| Evidence | Seed | Cases | Conclusion |
|---|---:|---|---|
| campaign(20261005-065923).zip | 844524 | shared: two PASS; separate: two IDENTITY_CANDIDATE | Original server-error observation |
| campaign(20261005-073436).zip | 264758 | reference-controls: two complete runs; household-controls: two complete runs | Cross-seed confirmation of original error; additional household state deviation |

## Evidence classification

1. Original server-error finding: reproduced in two campaigns with different seeds and newly created identities/resources. Both actor directions fail in both samples of each campaign: eight matching foreign-reference failures. Classify as REPRODUCED_SERVER_ERROR. This establishes reproducibility, not previously unreported status.
2. Missing-reference control: four server errors in the latest campaign. List content remains unchanged. This shows the server error is not unique to foreign references.
3. Household state deviation: four failed operations in two latest samples. Owner readback shows each affected list changing from two items to three. A new item identity is present; existing items are unchanged. This is substantive content change, not timestamp-only drift. Classify as OBSERVED_REPEATED_HOUSEHOLD_ISOLATION_DEVIATION. Cross-seed confirmation of this particular deviation remains pending.
4. Same-group recipe sharing is consistent with documented behavior and must not be counted as an isolation defect.

## Official policy check

https://mealie.io/documentation/getting-started/features/ (Groups and Households): groups isolate data; households share recipes within a group while shopping lists, meal plans and integrations are household-scoped. This supports the distinction used by the controls and makes the observed foreign-household list mutation inconsistent with documented scope.

https://mealie.io/documentation/getting-started/usage/permissions-and-public-access/ describes configurable public recipe access. Public recipe access must not be generalized to shopping-list write access.

These are current documentation pages, not a retrieved documentation snapshot pinned to v3.28.0.

## Diagnostics and root-cause limits

The latest captured server log contains four household failure timestamps with an AttributeError involving a missing list object during list-reference maintenance. Duplicate traceback entries occur; exception-line counts must not be treated as independent incidents. The log does not provide equivalent root-cause evidence for all eight reference-control failures. Observed state survives into the owner's follow-up read; transaction ordering and commit/rollback behavior remain unverified in source.

Fetching the v3.28.0 source file through GitHub and the raw-source route failed. No source-level root cause is claimed. Treat reference validation and household mutation as separate findings until code evidence links them.

## Existing reports search

Targeted searches of the official repository covered the exception signature, household shopping-list errors and permission-related fixes. Related material includes issue #7640 (checked ingredients reappearing), PR #8280 (shopping-list entry fixes), and release references to #7899 (repository scope fixes). These retrieved items do not establish an exact match to the observed failures. Search coverage is incomplete; absence of an exact match is not proof of novelty or absence of a fix.

Official references:
- https://github.com/mealie-recipes/mealie/issues/7640
- https://github.com/mealie-recipes/mealie/pull/8280
- https://github.com/mealie-recipes/mealie/releases

## Remaining work

- Review pinned source or provide a matching source snapshot to verify scope checks and transaction behavior.
- Independently confirm the household state deviation under another seed on the user's isolated local server. No live requests were made in this review.
- Verify existing-report overlap before claiming novelty.
- Preserve original evidence and original new_bug_confirmed fields. The analytical classification is separate from those fields; their producer semantics were not audited here.

No concurrency, long-prefix necessity, tool superiority, or causal equivalence between the findings is established by these campaigns.

## Repository closure record

Uses the established multi-identity evidence layout and frozen qualification oracle. See evidence/scope-controls-20261005-073218 for original campaign, independent qualification, manifest, environment gaps and handoff. Source snapshot is from the review checkout; it is not represented as the exact historical installed source. Existing original-campaign bytes were recovered and matched to its pre-existing checksums. No previous finding files or verdict fields were rewritten.

Original HANDOFF requested exception capture, missing-reference control, and same-group/different-household coverage. The latest campaign implements those controls. Independent qualification finds four discrepancies per latest run: reference runs have four HTTP deviations; household runs have two HTTP deviations and two state deviations.

Closure still needs precise actual runtime image/DB/tool provenance and a fresh-seed confirmation of household state deviation. Source-level diagnosis and novelty remain separately qualified. Next planned coverage after closure: reference removal/replacement and copy/import scope boundaries, as stated in the existing original findings report. No new execution commands or new offensive test workflow are supplied by this archive.
