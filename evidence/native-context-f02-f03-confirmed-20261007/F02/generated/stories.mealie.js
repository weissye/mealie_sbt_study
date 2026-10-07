// Generated stories: explicit entity instances; Context-driven verification.
// HTTP paths and request bodies are confined to interfaces.
ctx.bthread("protectWriteAndReadback", "WriteLock.All", function(lock) {
    sync({block:matchesConflictingWrites(lock.logicalId,lock.owner),waitFor:matchesVerified(lock.logicalId,lock.revision)});
});
ctx.bthread("protectPendingVerification", "Verification.Pending", function(resource) {
    sync({block:matchesMutations(resource.id),waitFor:matchesVerified(resource.id,resource.revision)});
});
// Authentication is a separate protocol process; all HTTP stays in interfaces.
bthread("authenticate client",function(){
    authenticate();
    request(AuthenticationReady);
});
bthread("require authentication before business HTTP",function(){
    sync({block:BusinessHTTP,waitFor:AuthenticationReady});
});

// Verification is activated by a Context query, independently of producers.
ctx.bthread("verifyIngredientFoodAfterEveryWrite", "Verification.Pending", function(resource) {
    if(resource.resourceType!=="IngredientFood") return;
    verifyIngredientFood(resource);
    request(bp.Event("ModelVerified",{logicalId:resource.id,revision:resource.revision}));
});

// Instance IngredientFood_1: creation, independent readback, update, independent readback.
bthread("lifecycle IngredientFood_1", function() {
    var parents=waitForDependencies([]);
    createIngredientFood("IngredientFood_1",{"name":"sbt-869772553-IngredientFood-1-name","pluralName":"sbt-869772553-IngredientFood-1-pluralName"},parents);
    waitFor(matchesVerified("IngredientFood_1",1));
    updateIngredientFood(getModelEntity("IngredientFood_1"),{"description":"sbt-869772553-IngredientFood_1-updated"});
    waitFor(matchesVerified("IngredientFood_1",2));
});

// Instance IngredientFood_2: creation, independent readback, update, independent readback.
bthread("lifecycle IngredientFood_2", function() {
    var parents=waitForDependencies([]);
    createIngredientFood("IngredientFood_2",{"name":"sbt-869772553-IngredientFood-2-name","pluralName":"sbt-869772553-IngredientFood-2-pluralName"},parents);
    waitFor(matchesVerified("IngredientFood_2",1));
    updateIngredientFood(getModelEntity("IngredientFood_2"),{"description":"sbt-869772553-IngredientFood_2-updated"});
    waitFor(matchesVerified("IngredientFood_2",2));
});

// Verification is activated by a Context query, independently of producers.
ctx.bthread("verifyIngredientUnitAfterEveryWrite", "Verification.Pending", function(resource) {
    if(resource.resourceType!=="IngredientUnit") return;
    verifyIngredientUnit(resource);
    request(bp.Event("ModelVerified",{logicalId:resource.id,revision:resource.revision}));
});

// Instance IngredientUnit_1: creation, independent readback, update, independent readback.
bthread("lifecycle IngredientUnit_1", function() {
    var parents=waitForDependencies([]);
    createIngredientUnit("IngredientUnit_1",{"name":"sbt-869772553-IngredientUnit-1-name","pluralName":"sbt-869772553-IngredientUnit-1-pluralName"},parents);
    waitFor(matchesVerified("IngredientUnit_1",1));
    updateIngredientUnit(getModelEntity("IngredientUnit_1"),{"description":"sbt-869772553-IngredientUnit_1-updated"});
    waitFor(matchesVerified("IngredientUnit_1",2));
});

// Verification is activated by a Context query, independently of producers.
ctx.bthread("verifyRecipeAfterEveryWrite", "Verification.Pending", function(resource) {
    if(resource.resourceType!=="Recipe") return;
    verifyRecipe(resource);
    request(bp.Event("ModelVerified",{logicalId:resource.id,revision:resource.revision}));
});

// Instance Recipe_1: creation, independent readback, update, independent readback.
bthread("lifecycle Recipe_1", function() {
    var parents=waitForDependencies([]);
    createRecipe("Recipe_1",{"name":"sbt-869772553-Recipe-1-name"},parents);
    waitFor(matchesVerified("Recipe_1",1));
    updateRecipe(getModelEntity("Recipe_1"),{"description":"sbt-869772553-Recipe_1-updated"});
    waitFor(matchesVerified("Recipe_1",2));
});

// Verification is activated by a Context query, independently of producers.
ctx.bthread("verifyShoppingListOutAfterEveryWrite", "Verification.Pending", function(resource) {
    if(resource.resourceType!=="ShoppingListOut") return;
    verifyShoppingListOut(resource);
    request(bp.Event("ModelVerified",{logicalId:resource.id,revision:resource.revision}));
});

// Instance ShoppingListOut_1: creation, independent readback, update, independent readback.
bthread("lifecycle ShoppingListOut_1", function() {
    var parents=waitForDependencies([]);
    createShoppingListOut("ShoppingListOut_1",{"name":"sbt-869772553-ShoppingListOut-1-name"},parents);
    waitFor(matchesVerified("ShoppingListOut_1",1));
    updateShoppingListOut(getModelEntity("ShoppingListOut_1"),{"name":"sbt-869772553-ShoppingListOut_1-updated"});
    waitFor(matchesVerified("ShoppingListOut_1",2));
});

// Verification is activated by a Context query, independently of producers.
ctx.bthread("verifyShoppingListItemOutAfterEveryWrite", "Verification.Pending", function(resource) {
    if(resource.resourceType!=="ShoppingListItemOut") return;
    verifyShoppingListItemOut(resource);
    request(bp.Event("ModelVerified",{logicalId:resource.id,revision:resource.revision}));
});

// Independent dependency construction: all ready requirements are checked together.
bthread('F02 source graph',function(){waitF02Parents();waitForResource({"operation_path":"/api/households/shopping/lists/{item_id}/recipe","codes":[200],"recipe_type":"Recipe","list_type":"ShoppingListOut","item_type":"ShoppingListItemOut","ingredients_field":"recipeIngredient","quantity_field":"quantity","recipe_key":"recipeId","increment_field":"recipeIncrementQuantity","item_array":"listItems","item_refs":"recipeReferences","list_refs":"recipeReferences","reference_quantity":"recipeQuantity","reference_scale":"recipeScale","owner_key":"shoppingListId","child_key":"shoppingListItemId","keys":[{"source":"unit","item":"unitId"},{"source":"food","item":"foodId"}],"recipe_detail":"/api/recipes/{slug}","recipe_parameter":"slug","list_detail":"/api/households/shopping/lists/{item_id}","list_parameter":"item_id","item_detail":"/api/households/shopping/items/{item_id}","item_parameter":"item_id","sources":["#/paths/~1api~1households~1shopping~1lists~1{item_id}~1recipe/post","#/paths/~1api~1recipes~1{slug}/patch/requestBody","#/paths/~1api~1households~1shopping~1items~1{item_id}/get","#/paths/~1api~1households~1shopping~1lists~1{item_id}/get","#/paths/~1api~1foods~1merge/put","#/paths/~1api~1households~1shopping~1lists~1{item_id}~1recipe~1{recipe_id}~1delete/post"],"inference":"summary Add; array input; source Id; numeric Increment; unique container response; schema-linked item and references","hypothesis":"Canonical merge preserves aggregate quantities; removing one recipe subtracts its current canonical ingredient aggregate and leaves the manual baseline. Not implied by OpenAPI alone.","scales":[1,0.5],"fixture_quantities":[2,2],"mode":"removal","variant":"food","merge_type":"IngredientFood","merge_source_field":"food","merge_item_key":"foodId","merge_path":"/api/foods/merge","merge_method":"PUT","merge_codes":[200],"merge_from":"fromFood","merge_to":"toFood","remove_path":"/api/households/shopping/lists/{item_id}/recipe/{recipe_id}/delete","remove_codes":[200],"decrement":"recipeDecrementQuantity","manual_quantity":7,"dependency_links":[{"field":"unit","target":"IngredientUnit","required":["id","name"]},{"field":"food","target":"IngredientFood","required":["id","name"]}],"item_create_path":"/api/households/shopping/items","item_create_codes":[201],"required_ready":{"IngredientFood":2,"IngredientUnit":1,"Recipe":1,"ShoppingListOut":1},"skip_merge":false,"zero_fields_js":"delta[\"recipeServings\"]=1;delta[\"recipeYieldQuantity\"]=1;"}.recipe_type+'_1',2);createRemovalSource(getModelEntity({"operation_path":"/api/households/shopping/lists/{item_id}/recipe","codes":[200],"recipe_type":"Recipe","list_type":"ShoppingListOut","item_type":"ShoppingListItemOut","ingredients_field":"recipeIngredient","quantity_field":"quantity","recipe_key":"recipeId","increment_field":"recipeIncrementQuantity","item_array":"listItems","item_refs":"recipeReferences","list_refs":"recipeReferences","reference_quantity":"recipeQuantity","reference_scale":"recipeScale","owner_key":"shoppingListId","child_key":"shoppingListItemId","keys":[{"source":"unit","item":"unitId"},{"source":"food","item":"foodId"}],"recipe_detail":"/api/recipes/{slug}","recipe_parameter":"slug","list_detail":"/api/households/shopping/lists/{item_id}","list_parameter":"item_id","item_detail":"/api/households/shopping/items/{item_id}","item_parameter":"item_id","sources":["#/paths/~1api~1households~1shopping~1lists~1{item_id}~1recipe/post","#/paths/~1api~1recipes~1{slug}/patch/requestBody","#/paths/~1api~1households~1shopping~1items~1{item_id}/get","#/paths/~1api~1households~1shopping~1lists~1{item_id}/get","#/paths/~1api~1foods~1merge/put","#/paths/~1api~1households~1shopping~1lists~1{item_id}~1recipe~1{recipe_id}~1delete/post"],"inference":"summary Add; array input; source Id; numeric Increment; unique container response; schema-linked item and references","hypothesis":"Canonical merge preserves aggregate quantities; removing one recipe subtracts its current canonical ingredient aggregate and leaves the manual baseline. Not implied by OpenAPI alone.","scales":[1,0.5],"fixture_quantities":[2,2],"mode":"removal","variant":"food","merge_type":"IngredientFood","merge_source_field":"food","merge_item_key":"foodId","merge_path":"/api/foods/merge","merge_method":"PUT","merge_codes":[200],"merge_from":"fromFood","merge_to":"toFood","remove_path":"/api/households/shopping/lists/{item_id}/recipe/{recipe_id}/delete","remove_codes":[200],"decrement":"recipeDecrementQuantity","manual_quantity":7,"dependency_links":[{"field":"unit","target":"IngredientUnit","required":["id","name"]},{"field":"food","target":"IngredientFood","required":["id","name"]}],"item_create_path":"/api/households/shopping/items","item_create_codes":[201],"required_ready":{"IngredientFood":2,"IngredientUnit":1,"Recipe":1,"ShoppingListOut":1},"skip_merge":false,"zero_fields_js":"delta[\"recipeServings\"]=1;delta[\"recipeYieldQuantity\"]=1;"}.recipe_type+'_1'),f02Parents());waitFor(matchesVerified({"operation_path":"/api/households/shopping/lists/{item_id}/recipe","codes":[200],"recipe_type":"Recipe","list_type":"ShoppingListOut","item_type":"ShoppingListItemOut","ingredients_field":"recipeIngredient","quantity_field":"quantity","recipe_key":"recipeId","increment_field":"recipeIncrementQuantity","item_array":"listItems","item_refs":"recipeReferences","list_refs":"recipeReferences","reference_quantity":"recipeQuantity","reference_scale":"recipeScale","owner_key":"shoppingListId","child_key":"shoppingListItemId","keys":[{"source":"unit","item":"unitId"},{"source":"food","item":"foodId"}],"recipe_detail":"/api/recipes/{slug}","recipe_parameter":"slug","list_detail":"/api/households/shopping/lists/{item_id}","list_parameter":"item_id","item_detail":"/api/households/shopping/items/{item_id}","item_parameter":"item_id","sources":["#/paths/~1api~1households~1shopping~1lists~1{item_id}~1recipe/post","#/paths/~1api~1recipes~1{slug}/patch/requestBody","#/paths/~1api~1households~1shopping~1items~1{item_id}/get","#/paths/~1api~1households~1shopping~1lists~1{item_id}/get","#/paths/~1api~1foods~1merge/put","#/paths/~1api~1households~1shopping~1lists~1{item_id}~1recipe~1{recipe_id}~1delete/post"],"inference":"summary Add; array input; source Id; numeric Increment; unique container response; schema-linked item and references","hypothesis":"Canonical merge preserves aggregate quantities; removing one recipe subtracts its current canonical ingredient aggregate and leaves the manual baseline. Not implied by OpenAPI alone.","scales":[1,0.5],"fixture_quantities":[2,2],"mode":"removal","variant":"food","merge_type":"IngredientFood","merge_source_field":"food","merge_item_key":"foodId","merge_path":"/api/foods/merge","merge_method":"PUT","merge_codes":[200],"merge_from":"fromFood","merge_to":"toFood","remove_path":"/api/households/shopping/lists/{item_id}/recipe/{recipe_id}/delete","remove_codes":[200],"decrement":"recipeDecrementQuantity","manual_quantity":7,"dependency_links":[{"field":"unit","target":"IngredientUnit","required":["id","name"]},{"field":"food","target":"IngredientFood","required":["id","name"]}],"item_create_path":"/api/households/shopping/items","item_create_codes":[201],"required_ready":{"IngredientFood":2,"IngredientUnit":1,"Recipe":1,"ShoppingListOut":1},"skip_merge":false,"zero_fields_js":"delta[\"recipeServings\"]=1;delta[\"recipeYieldQuantity\"]=1;"}.recipe_type+'_1',3));request(bp.Event('F02Ready',{flag:'source'}));});
bthread('F02 manual child lifecycle',function(){waitF02Parents();waitForResource({"operation_path":"/api/households/shopping/lists/{item_id}/recipe","codes":[200],"recipe_type":"Recipe","list_type":"ShoppingListOut","item_type":"ShoppingListItemOut","ingredients_field":"recipeIngredient","quantity_field":"quantity","recipe_key":"recipeId","increment_field":"recipeIncrementQuantity","item_array":"listItems","item_refs":"recipeReferences","list_refs":"recipeReferences","reference_quantity":"recipeQuantity","reference_scale":"recipeScale","owner_key":"shoppingListId","child_key":"shoppingListItemId","keys":[{"source":"unit","item":"unitId"},{"source":"food","item":"foodId"}],"recipe_detail":"/api/recipes/{slug}","recipe_parameter":"slug","list_detail":"/api/households/shopping/lists/{item_id}","list_parameter":"item_id","item_detail":"/api/households/shopping/items/{item_id}","item_parameter":"item_id","sources":["#/paths/~1api~1households~1shopping~1lists~1{item_id}~1recipe/post","#/paths/~1api~1recipes~1{slug}/patch/requestBody","#/paths/~1api~1households~1shopping~1items~1{item_id}/get","#/paths/~1api~1households~1shopping~1lists~1{item_id}/get","#/paths/~1api~1foods~1merge/put","#/paths/~1api~1households~1shopping~1lists~1{item_id}~1recipe~1{recipe_id}~1delete/post"],"inference":"summary Add; array input; source Id; numeric Increment; unique container response; schema-linked item and references","hypothesis":"Canonical merge preserves aggregate quantities; removing one recipe subtracts its current canonical ingredient aggregate and leaves the manual baseline. Not implied by OpenAPI alone.","scales":[1,0.5],"fixture_quantities":[2,2],"mode":"removal","variant":"food","merge_type":"IngredientFood","merge_source_field":"food","merge_item_key":"foodId","merge_path":"/api/foods/merge","merge_method":"PUT","merge_codes":[200],"merge_from":"fromFood","merge_to":"toFood","remove_path":"/api/households/shopping/lists/{item_id}/recipe/{recipe_id}/delete","remove_codes":[200],"decrement":"recipeDecrementQuantity","manual_quantity":7,"dependency_links":[{"field":"unit","target":"IngredientUnit","required":["id","name"]},{"field":"food","target":"IngredientFood","required":["id","name"]}],"item_create_path":"/api/households/shopping/items","item_create_codes":[201],"required_ready":{"IngredientFood":2,"IngredientUnit":1,"Recipe":1,"ShoppingListOut":1},"skip_merge":false,"zero_fields_js":"delta[\"recipeServings\"]=1;delta[\"recipeYieldQuantity\"]=1;"}.list_type+'_1',2);createRemovalBaseline(getModelEntity({"operation_path":"/api/households/shopping/lists/{item_id}/recipe","codes":[200],"recipe_type":"Recipe","list_type":"ShoppingListOut","item_type":"ShoppingListItemOut","ingredients_field":"recipeIngredient","quantity_field":"quantity","recipe_key":"recipeId","increment_field":"recipeIncrementQuantity","item_array":"listItems","item_refs":"recipeReferences","list_refs":"recipeReferences","reference_quantity":"recipeQuantity","reference_scale":"recipeScale","owner_key":"shoppingListId","child_key":"shoppingListItemId","keys":[{"source":"unit","item":"unitId"},{"source":"food","item":"foodId"}],"recipe_detail":"/api/recipes/{slug}","recipe_parameter":"slug","list_detail":"/api/households/shopping/lists/{item_id}","list_parameter":"item_id","item_detail":"/api/households/shopping/items/{item_id}","item_parameter":"item_id","sources":["#/paths/~1api~1households~1shopping~1lists~1{item_id}~1recipe/post","#/paths/~1api~1recipes~1{slug}/patch/requestBody","#/paths/~1api~1households~1shopping~1items~1{item_id}/get","#/paths/~1api~1households~1shopping~1lists~1{item_id}/get","#/paths/~1api~1foods~1merge/put","#/paths/~1api~1households~1shopping~1lists~1{item_id}~1recipe~1{recipe_id}~1delete/post"],"inference":"summary Add; array input; source Id; numeric Increment; unique container response; schema-linked item and references","hypothesis":"Canonical merge preserves aggregate quantities; removing one recipe subtracts its current canonical ingredient aggregate and leaves the manual baseline. Not implied by OpenAPI alone.","scales":[1,0.5],"fixture_quantities":[2,2],"mode":"removal","variant":"food","merge_type":"IngredientFood","merge_source_field":"food","merge_item_key":"foodId","merge_path":"/api/foods/merge","merge_method":"PUT","merge_codes":[200],"merge_from":"fromFood","merge_to":"toFood","remove_path":"/api/households/shopping/lists/{item_id}/recipe/{recipe_id}/delete","remove_codes":[200],"decrement":"recipeDecrementQuantity","manual_quantity":7,"dependency_links":[{"field":"unit","target":"IngredientUnit","required":["id","name"]},{"field":"food","target":"IngredientFood","required":["id","name"]}],"item_create_path":"/api/households/shopping/items","item_create_codes":[201],"required_ready":{"IngredientFood":2,"IngredientUnit":1,"Recipe":1,"ShoppingListOut":1},"skip_merge":false,"zero_fields_js":"delta[\"recipeServings\"]=1;delta[\"recipeYieldQuantity\"]=1;"}.list_type+'_1'),f02Parents());waitFor(matchesVerified({"operation_path":"/api/households/shopping/lists/{item_id}/recipe","codes":[200],"recipe_type":"Recipe","list_type":"ShoppingListOut","item_type":"ShoppingListItemOut","ingredients_field":"recipeIngredient","quantity_field":"quantity","recipe_key":"recipeId","increment_field":"recipeIncrementQuantity","item_array":"listItems","item_refs":"recipeReferences","list_refs":"recipeReferences","reference_quantity":"recipeQuantity","reference_scale":"recipeScale","owner_key":"shoppingListId","child_key":"shoppingListItemId","keys":[{"source":"unit","item":"unitId"},{"source":"food","item":"foodId"}],"recipe_detail":"/api/recipes/{slug}","recipe_parameter":"slug","list_detail":"/api/households/shopping/lists/{item_id}","list_parameter":"item_id","item_detail":"/api/households/shopping/items/{item_id}","item_parameter":"item_id","sources":["#/paths/~1api~1households~1shopping~1lists~1{item_id}~1recipe/post","#/paths/~1api~1recipes~1{slug}/patch/requestBody","#/paths/~1api~1households~1shopping~1items~1{item_id}/get","#/paths/~1api~1households~1shopping~1lists~1{item_id}/get","#/paths/~1api~1foods~1merge/put","#/paths/~1api~1households~1shopping~1lists~1{item_id}~1recipe~1{recipe_id}~1delete/post"],"inference":"summary Add; array input; source Id; numeric Increment; unique container response; schema-linked item and references","hypothesis":"Canonical merge preserves aggregate quantities; removing one recipe subtracts its current canonical ingredient aggregate and leaves the manual baseline. Not implied by OpenAPI alone.","scales":[1,0.5],"fixture_quantities":[2,2],"mode":"removal","variant":"food","merge_type":"IngredientFood","merge_source_field":"food","merge_item_key":"foodId","merge_path":"/api/foods/merge","merge_method":"PUT","merge_codes":[200],"merge_from":"fromFood","merge_to":"toFood","remove_path":"/api/households/shopping/lists/{item_id}/recipe/{recipe_id}/delete","remove_codes":[200],"decrement":"recipeDecrementQuantity","manual_quantity":7,"dependency_links":[{"field":"unit","target":"IngredientUnit","required":["id","name"]},{"field":"food","target":"IngredientFood","required":["id","name"]}],"item_create_path":"/api/households/shopping/items","item_create_codes":[201],"required_ready":{"IngredientFood":2,"IngredientUnit":1,"Recipe":1,"ShoppingListOut":1},"skip_merge":false,"zero_fields_js":"delta[\"recipeServings\"]=1;delta[\"recipeYieldQuantity\"]=1;"}.item_type+'_1',1));request(bp.Event('F02Ready',{flag:'manual'}));});
bthread('F02 full contribution',function(){waitF02Flag('source');waitF02Flag('manual');addRemovalContribution();waitF02Stage(1);});
bthread('F02 canonical dependency merge',function(){waitF02Stage(1);mergeRemovalDependency();waitF02Stage(2);});
bthread('F02 remove source contribution',function(){waitF02Stage(2);removeRemovalContribution();waitF02Stage(3);request(bp.Event('F02Completed'));});
ctx.bthread('F02 verify every transition','F02.Pending',function(state){readRemovalList(state,false);readRemovalRecipe(state);readRemovalItem(state,0);readRemovalItem(state,1);readRemovalList(state,true);request(bp.Event('F02Verified',{stage:state.stage}));});

