# Integer merge lifecycle campaign

Install this delta over the existing study that already contains the collision-controls delta. Run scripts/Run-Generic-Merge-Lifecycle.ps1 -Username changeme@example.com.

Two generated families, two native schedules per family, fresh owned resources per live run. Each complete schedule has 267 HTTP requests (1,068 across four successful complete runs). Requests are sequential. All HTTP remains in generated interfaces; generated stories schedule semantic tasks.

Food family: three foods, shared unit, two recipe ingredients of quantity 2. Unit family: shared food, three units, three ingredients of quantity 2. Controlled recipe yield is 1. The manual shopping quantity is 7.

Both families add two recipe contributions of quantity 1 per list, merge resources 1 into 2 and then 2 into 3, remove both contributions, add one again, and remove it again. Readbacks check recipe/list totals, identity remapping, recipe associations, source absence and manual quantity preservation. Complete final lists must retain manual total 7 and have no recipe associations.

Purpose: exercise chained identity remapping and complete removal/re-add with integer quantities, reducing dependence on the already observed fractional scaling discrepancy. A failure is a candidate for analysis, not an automatically confirmed new bug. Unit quantity preservation assumes custom units without configured conversion. Different orders of the same defect count as one bug with multiple reproductions.

Prerequisites: local pinned Mealie version, Python and Node, installed Provengo, at least 2 GiB free RAM and 1 GiB free disk. Java heap is limited to 1 GiB for this runner. Existing compatibility tests run first. Password is requested once and restored environment variables are cleaned in finally.

The runner continues after a classified semantic discrepancy to obtain the second fresh reproduction and next family. Authentication, infrastructure or unclassified failures stop the campaign. No automatic resource cleanup, rollback or full reset/replay is performed. Evidence is archived even on a failure inside the campaign loop.

Upload Downloads/mealie-lifecycle-TIMESTAMP/campaign.zip after execution. Keep this archive and original study evidence. These new scenarios have been tested against local fixtures and the native Provengo runtime here; live Mealie execution is pending on your computer.

Linked-resource deletion and changes to already-added recipes are not part of this delivery.
