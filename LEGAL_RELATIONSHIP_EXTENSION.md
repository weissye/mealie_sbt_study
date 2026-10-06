# Legal relationship lifecycle extension

Opt-in generic graph transitions; Mealie endpoint names remain in the profile.
Existing profiles keep their original task counts and behavior.

The pilot creates 35 owned resources and runs 96 tasks / 326 HTTP operations.
1. Build the original acyclic recipe chain; verify source links and GET targets.
2. Reject cycles of lengths 2 through 5 with full member before/after snapshots.
3. Clear the first nullable relationship; verify no referenced recipe remains.
4. Accept a link from the last recipe to the first, now a legal acyclic edge.
5. Reject restoring the first edge, which would close a five-member cycle.
6. Validate runtime receipts for legal source/target GETs and negative atomicity.

All HTTP stays in interfaces; stories schedule tasks without overlapping HTTP.
Single-sample replay uses the original audited sample file directly, avoiding
the approximately 1.13 GiB selected-sample copy. Multi-sample replay retains
selection behavior. Existing sample files and source models are preserved.
This does not shrink the original native sample file.

Run scripts/Run-Generic-Legal-Relationship-Pilot.ps1 -Username USERNAME.
The script runs compatibility checks, generates a fresh model, samples once,
and executes it once. It sends mutating requests and creates 35 resources.
No DELETE, reset, rollback, or automatic retry. Upload the printed live.zip.
If live execution fails, retain the printed project path and diagnose before
rerunning the wrapper (which would otherwise create another new project).

Acceptance here is static and Node stub validation. Native Windows Provengo
and live Mealie acceptance of this extension must be performed locally.
No full JSON Schema validator or general absence-of-bugs claim.
Alternative paths/diamonds and deleting referenced resources are future work.
