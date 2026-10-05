# Generic association write/readback views

## Native evidence

The latest project generic-mealie-b27ae4dfed25 was sampled successfully for all 55 tasks. The four model file hashes in the sampling acceptance match the live review files. The live run accepted 20 tasks and 67 callbacks, then stopped at shopping-item task link:2:2. The PUT succeeded but GET did not return the target under referencedRecipe. Neither cycle probe was executed.

The previously accepted manual fixture provides a useful shape control: adding recipes to lists returned item referencedRecipe as null while item recipeReferences contained recipeId, id and shoppingListItemId. This confirms the association readback shape, not the new direct item PUT effect.

## Explicit profile binding

The compiler now accepts optional relationship_write_views. For the selected item-to-recipe relationship, the Mealie runtime profile configures write_path recipeReferences[], item_identity_field recipeId, target_field id, defaults recipeQuantity=1 and recipeScale=1, and readback_path recipeReferences[].recipeId. The engine validates selected operations, documented paths, target identity types and constructible association items. It contains no application-specific branch.

This is a configured association effect rather than a declaration that referencedRecipe and recipeReferences are interchangeable schema aliases. The original inferred path remains visible in the relationship plan beside configured_write_view. The compilation report lists the explicit mapping and marks its write semantics pending native verification. No story is removed and no mismatch is reclassified as success.

Interfaces merge new target identities into the existing collection and retain existing association records and quantities. Verification checks the target UUID under the configured association readback path. All HTTP and response handling remain in interfaces; stories retain their coordination role.

The compiled runtime projection also prefers the accepted union branch that preserves the most documented fields. An observed association with id and shoppingListItemId therefore retains the update representation instead of being reduced to the create representation. A null branch now rejects non-null values; malformed nullable data can no longer bypass projection.

## Validation

41 Python tests and all 466 original transport comparisons passed. The Node mock ignores inherited item referencedRecipe, persists association records, seeds an existing association and asserts its id and quantity survive updates. Removing the mapping reproduces the readback failure. Corrupting association readback and supplying a non-null number to a nullable object schema fail closed. Existing cycle acceptance, mutation-on-rejection and server-error tests remain covered.

The complete model still has 55 tasks, 170 HTTP callbacks and two cycle probes of lengths 2 and 3. Native sampling and Mealie execution of this updated association mapping are pending. Existing default generator output remains compatible. The projection remains a documented subset rather than a full JSON Schema validator.

## Windows execution

Apply this delta to the existing study root and regenerate a new project:

```powershell
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\generic_generator_association_views_delta.zip" -DestinationPath 'C:\work\temp\mealie_sbt_study' -Force
Set-Location 'C:\work\temp\mealie_sbt_study'
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
Get-ChildItem '.\scripts' -Filter '*.ps1' -File | Unblock-File
& .\scripts\Run-Generic-Relationship-Pilot.ps1 -Username 'changeme@example.com' -SampleSize 1
```

This creates new owned fixture resources. It does not retry an old failed schedule or delete earlier fixtures. Upload Downloads\generic_relationship_live_review.zip after execution.
