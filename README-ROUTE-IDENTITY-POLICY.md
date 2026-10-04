# Route identity continuation

This delta preserves the failed PUT control and qualifies its instruction-row replacement against pinned Mealie v3.28.0 source. It adds an explicit generic child identity policy; only recipeInstructions[].id is declared replaceable in these three Mealie profiles. Every replacement is recorded and independently verified. No new system defect is confirmed. PATCH was investigated and withdrawn as a remedy because the generic repository merges the full resource before update.

Extract at the existing study repository root. Run scripts/Save-Generic-Route-Identity.ps1 -Push, then scripts/Run-Generic-Route-Identity.ps1 -Username changeme@example.com. The existing runner detects its root from its own location and runs two fresh-resource samples per case, control first, then rename and old-alias reuse. A failure stops the campaign. It uses a 512 MiB Java heap; Chrome need not be closed when its 1 GiB RAM and disk checks pass. Existing evidence is not overwritten by this delta.

The Save script verifies archived campaigns before any Git change and pushes a scoped commit. Do not automatically repeat a failed run: upload its campaign.zip from the printed Downloads campaign directory. Six healthy native mock schedules and nine injected-fault schedules were checked locally. This does not certify Windows execution or actual Mealie outcomes.
