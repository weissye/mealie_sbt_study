# Engineering and research record: stale snapshots after dependency deletion

Pinned system: Mealie v3.28.0. Contract SHA256: 90e19aa713ab4ba15352627aca7dc37290f868b213eb65a3e1564f3b7a7ff292. Home campaign: 2026-10-04 20:56:17 Asia/Jerusalem, seed 498616.

## Result and evidence

Four no-deletion controls completed with independently validated receipts (101 responses each). Four deletion probes reached the policy-qualification stop: an old recipe snapshot was accepted with HTTP 200, the intended description persisted, the removed food/unit remained absent with HTTP 404, and its ingredient reference remained null. All six protected source/control readbacks matched the independently examined expectations. These probes do not constitute complete post-qualification schedules or reset/replay acceptance. No new defect was confirmed. Acceptance with HTTP 200 alone is not a defect oracle.

The archive preserves the exact original campaign and the preceding false-positive campaign. SHA256 values are recorded in checksums.json; verify_campaign.py verifies the archive and the nested live-run archives without requests. The false positive was caused by treating an embedded live recipe view in a shopping list as immutable despite an intentional description update. The corrected generic oracle allows only the intended field and declared timestamps of the matching owned source view to change, while retaining association identity and quantity checks. This correction was made before the accepted follow-up campaign.

## Research interpretation and limitations

The observed behavior supports a scoped consistency result for deletion followed by stale writes in these schedules. It does not establish correctness of all stale writes, all references, other versions, concurrent operations or server reset/replay. Policies and expected effects are explicitly configured hypotheses validated against OpenAPI paths, not inferred business semantics. There is no new bug count for this campaign. The previously confirmed quantity discrepancy remains a separate finding.

## Next experiment: dependency ownership transfer

The new generic opt-in campaign avoids deletion and merge. Recipes R1 and R2 initially contain references to A and B; R3 contains C twice. Target names change before and between sequential rebindings: update A, move R1's A slot to B, update A again, move R2's A slot to B, update B, return R1's original slot to A, update B again. Every phase checks all three recipe projections and all three targets. R3/C must remain unchanged. Existing ingredient quantities, reference IDs and non-target fields remain protected; the derived display string is excluded explicitly. No quantity aggregation or shopping-list contribution oracle is used.

Matched controls perform the same target updates without rebindings. Food and unit variants each run two native schedules with fresh owned resources. Multiple schedules reproducing the same root cause are one defect family. A first mismatch is preserved as a candidate, not declared a confirmed defect. A second scheduled run uses fresh resources for reproduction; infrastructure/authentication failures stop the campaign. HTTP remains exclusively in generated interfaces; stories select and coordinate task events. This initial campaign explicitly orders transfer phases while varying the generated prefix schedules. It does not exhaust permutations of transfer phases.
