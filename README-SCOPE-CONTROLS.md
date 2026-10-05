# Small reference and household controls campaign

Run scripts/Save-Generic-Scope-Controls.ps1 -Push to preserve this source release.
Then run scripts/Run-Generic-Scope-Controls.ps1 -Username changeme@example.com.
The password prompt is for the existing provisioning administrator; newly created
regular users perform all resource probes. JAVA_TOOL_OPTIONS is scoped to this
invocation with -Xmx512m. Existing profiles and runners remain unchanged.

Upload the printed Downloads/mealie-scope-controls-*/campaign.zip after completion.
It contains four run results, native receipts, generated sources/samples, immediate
readbacks and optional scrubbed Docker exception evidence. No automatic cleanup.

Expected server: local Mealie v3.28.0 on http://127.0.0.1:9925.
Read docs/research/20261005/Mealie_Reference_And_Household_Controls.md for policy and
qualification limits. Two cases, two fresh replays each; 186 modeled HTTP requests.
