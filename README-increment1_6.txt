Increment 1.6 - accepted live fixture review and offline Provengo symbolic model. Requires increments 1.0-1.5.
Extract into C:\work\temp\mealie_sbt_study. Run scripts\Prepare-Mealie-Provengo-Model.ps1 -Sample.
The model requests eight symbolic events in two ordered four-step stories. All 70 order-preserving combinations are listed in expected-orders.json.
Story A: read R2 description, set a fixture description, verify it, restore the captured description.
Story B: unlink R2 from L1, verify absence, relink it, verify presence. These are symbolic prospective actions only.
No HTTP executor or REST library is loaded. Provengo sampling does not execute these operations or change server data.
Provengo sample invocation uses the documented full algorithm. A missing executable or sample error is packaged for review; generated coverage is not declared accepted until the output is inspected.
Output: Downloads\mealie_provengo_model_review.zip. Use -ProvengoPath when Provengo is not on PATH.
Next gate: accept each standalone functional story and semantic restoration before live composition. Regenerated item/link UUIDs must not be equated to preserved semantic state. Cyclic links and actual parallel HTTP remain untested.
Validation: 28 Python unit tests passed; model generation from the actual uploaded fixture passed; generated JS syntax checked with Node. Provengo and the new PowerShell wrapper have not been executed here.
Sources: https://docs.provengo.tech/ProvengoCli/0.9.5/dsls/bp-base.html and https://docs.provengo.tech/ProvengoCli/0.9.5/subcommands/sample.html
