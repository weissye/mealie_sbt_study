# Repeated integer removal discrepancies

Original campaign: mealie-lifecycle-20261004-165852. Preserved campaign.zip is an exact copy of the uploaded archive. verify_campaign.py checks its SHA256, validates every completed semantic prefix independently, checks a fresh recipe readback before the failing mutation, and recomputes the expected quantity delta. It sends no API requests.

Food lifecycle: both fresh runs completed two merges, then removing one recipe contribution changed list quantity from 15 to 9. Fresh recipe total was 4, so expected quantity was 11. The remaining recipe association was correct.

Unit lifecycle: both fresh runs completed two merges. A later removal changed list quantity from 13 to 11. Fresh recipe total was 6, so expected quantity was 7. No recipe associations remained, yet excess quantity 4 remained.

Each pair uses disjoint resource identifiers and different completed semantic orders. Four failed runs are not counted as four bugs. These are two repeated removal manifestations; their independence from the previous duplicate-ingredient scaling defect remains to be determined. Internal implementation cause has not been confirmed.

The schedules stopped at the mismatch. Later re-add stages were not executed and full reset/replay is not accepted. Preserve campaign.zip and this verification alongside the original collision evidence.
