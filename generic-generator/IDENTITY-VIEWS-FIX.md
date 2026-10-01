# Explicit relationship identity views

The reviewed native run passed authentication and record initialization. It stopped after 64 callback responses and 19 accepted tasks, at shopping-item task link:1:3. The PUT payload contained a bound food.id but foodId remained null. The native readback failed; later symbolic completion events do not establish live success.

The optional relationship compiler now accepts explicit relationship_identity_views. Each rule identifies an operation, relationship field_path, scalar write_path, target_field and readback_path. Paths and scalar wire types are checked against the contract; unmatched, duplicate and conflicting rules fail generation. No equivalence is inferred from field spelling alone.

The Mealie runtime profile explicitly configures food/foodId and unit/unitId for shopping-item PUT. These mappings are configuration hypotheses pending native verification, not facts established by OpenAPI or by the previous failed run. During each link task the interface binds both representations from the observed target snapshot, then verifies the nested relationship and configured scalar identity on GET. Failed readback records task, expected/observed identities and view observations in sbt_rel_failed_readback.

HTTP remains entirely in interfaces. Stories and task dependencies remain unchanged. The existing generator without relationship compilation retains its previous output. No deletion, retry, rollback or server reset is added.

The Node stub models scalar foreign keys as authoritative for these two shopping-item relationships. Omitting the configuration reproduces a failure; adding it completes 54 tasks and 167 HTTP callbacks. Corrupting the scalar readback fails even when the nested object still appears valid. This stub does not establish actual Mealie semantics for other relationship fields.

Validation: 34 Python tests passed; all 466 original transport comparisons passed. Native sampling and live replay of this update are pending.

## Apply and run on Windows

Download generic_generator_identity_views_delta.zip into Downloads. Apply it to the existing study tree, then run the pilot to regenerate a new project. Existing generated projects do not acquire these changes automatically.

```powershell
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\generic_generator_identity_views_delta.zip" -DestinationPath 'C:\work\temp\mealie_sbt_study' -Force
Set-Location 'C:\work\temp\mealie_sbt_study'
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
Get-ChildItem '.\scripts' -Filter '*.ps1' -File | Unblock-File
& .\scripts\Run-Generic-Relationship-Pilot.ps1 -Username 'changeme@example.com' -SampleSize 1
```

The live pilot creates new owned resources. Review output remains in Downloads\generic_relationship_live_review.zip. Sampling is symbolic; live acceptance requires the complete observed runtime receipt.
