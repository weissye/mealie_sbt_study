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
    createIngredientFood("IngredientFood_1",{"name":"sbt-717883341-IngredientFood-1-name","pluralName":"sbt-717883341-IngredientFood-1-pluralName"},parents);
    waitFor(matchesVerified("IngredientFood_1",1));
    updateIngredientFood(getModelEntity("IngredientFood_1"),{"description":"sbt-717883341-IngredientFood_1-updated"});
    waitFor(matchesVerified("IngredientFood_1",2));
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
    createIngredientUnit("IngredientUnit_1",{"name":"sbt-717883341-IngredientUnit-1-name","pluralName":"sbt-717883341-IngredientUnit-1-pluralName"},parents);
    waitFor(matchesVerified("IngredientUnit_1",1));
    updateIngredientUnit(getModelEntity("IngredientUnit_1"),{"description":"sbt-717883341-IngredientUnit_1-updated"});
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
    createRecipe("Recipe_1",{"name":"sbt-717883341-Recipe-1-name"},parents);
    waitFor(matchesVerified("Recipe_1",1));
    updateRecipe(getModelEntity("Recipe_1"),{"description":"sbt-717883341-Recipe_1-updated"});
    waitFor(matchesVerified("Recipe_1",2));
});

// Embedded objects have separate planning bthreads; persistence uses the containing API.
bthread('F03 ingredient instance 1',function(){waitCopyParents();request(bp.Event('F03Ready',{flag:'ingredient1'}));});
bthread('F03 ingredient instance 2',function(){waitCopyParents();request(bp.Event('F03Ready',{flag:'ingredient2'}));});
bthread('F03 persist ingredient graph',function(){waitCopyFlag('ingredient1');waitCopyFlag('ingredient2');buildCopyIngredients(getModelEntity({"mode":"copy","recipe_type":"Recipe","item_type":"","copy_path":"/api/recipes/{slug}/duplicate","copy_codes":[201],"detail":"/api/recipes/{slug}","parameter":"slug","ingredients":"recipeIngredient","steps":"recipeInstructions","references":"ingredientReferences","reference_id":"referenceId","text":"text","links":[{"field":"unit","target":"IngredientUnit","required":["id","name"]},{"field":"food","target":"IngredientFood","required":["id","name"]}],"required_ready":{"IngredientFood":1,"IngredientUnit":1,"Recipe":1},"sources":["#/paths/~1api~1recipes~1{slug}~1duplicate/post","#/paths/~1api~1recipes~1{slug}/patch/requestBody","#/components/schemas/RecipeIngredient-Input/properties/referenceId","#/components/schemas/RecipeStep/properties/ingredientReferences","#/components/schemas/IngredientReferences/properties/referenceId"],"hypothesis":"Copy preserves internal reference closure, corresponding ingredient links and source state. UUID schemas and copy description do not fully specify identity remapping. This is an opt-in generic graph-copy integrity hypothesis.","seed":717883341,"fixtures":[{"referenceId":"62a9a736-2c63-497b-a984-c47a1b9e9806","note":"sbt-717883341-ingredient-0","quantity":2},{"referenceId":"f009a1a8-be45-4cc3-a7ce-8fbff7420c17","note":"sbt-717883341-ingredient-1","quantity":4}],"step_fixtures":[{"text":"sbt-717883341-step-0","ingredientReferences":[{"referenceId":"62a9a736-2c63-497b-a984-c47a1b9e9806"},{"referenceId":"f009a1a8-be45-4cc3-a7ce-8fbff7420c17"}]},{"text":"sbt-717883341-step-1","ingredientReferences":[{"referenceId":"f009a1a8-be45-4cc3-a7ce-8fbff7420c17"}]}]}.recipe_type+'_1'));waitFor(matchesVerified({"mode":"copy","recipe_type":"Recipe","item_type":"","copy_path":"/api/recipes/{slug}/duplicate","copy_codes":[201],"detail":"/api/recipes/{slug}","parameter":"slug","ingredients":"recipeIngredient","steps":"recipeInstructions","references":"ingredientReferences","reference_id":"referenceId","text":"text","links":[{"field":"unit","target":"IngredientUnit","required":["id","name"]},{"field":"food","target":"IngredientFood","required":["id","name"]}],"required_ready":{"IngredientFood":1,"IngredientUnit":1,"Recipe":1},"sources":["#/paths/~1api~1recipes~1{slug}~1duplicate/post","#/paths/~1api~1recipes~1{slug}/patch/requestBody","#/components/schemas/RecipeIngredient-Input/properties/referenceId","#/components/schemas/RecipeStep/properties/ingredientReferences","#/components/schemas/IngredientReferences/properties/referenceId"],"hypothesis":"Copy preserves internal reference closure, corresponding ingredient links and source state. UUID schemas and copy description do not fully specify identity remapping. This is an opt-in generic graph-copy integrity hypothesis.","seed":717883341,"fixtures":[{"referenceId":"62a9a736-2c63-497b-a984-c47a1b9e9806","note":"sbt-717883341-ingredient-0","quantity":2},{"referenceId":"f009a1a8-be45-4cc3-a7ce-8fbff7420c17","note":"sbt-717883341-ingredient-1","quantity":4}],"step_fixtures":[{"text":"sbt-717883341-step-0","ingredientReferences":[{"referenceId":"62a9a736-2c63-497b-a984-c47a1b9e9806"},{"referenceId":"f009a1a8-be45-4cc3-a7ce-8fbff7420c17"}]},{"text":"sbt-717883341-step-1","ingredientReferences":[{"referenceId":"f009a1a8-be45-4cc3-a7ce-8fbff7420c17"}]}]}.recipe_type+'_1',3));request(bp.Event('F03Ready',{flag:'ingredients'}));});
bthread('F03 instruction links',function(){waitCopyFlag('ingredients');buildCopySteps(getModelEntity({"mode":"copy","recipe_type":"Recipe","item_type":"","copy_path":"/api/recipes/{slug}/duplicate","copy_codes":[201],"detail":"/api/recipes/{slug}","parameter":"slug","ingredients":"recipeIngredient","steps":"recipeInstructions","references":"ingredientReferences","reference_id":"referenceId","text":"text","links":[{"field":"unit","target":"IngredientUnit","required":["id","name"]},{"field":"food","target":"IngredientFood","required":["id","name"]}],"required_ready":{"IngredientFood":1,"IngredientUnit":1,"Recipe":1},"sources":["#/paths/~1api~1recipes~1{slug}~1duplicate/post","#/paths/~1api~1recipes~1{slug}/patch/requestBody","#/components/schemas/RecipeIngredient-Input/properties/referenceId","#/components/schemas/RecipeStep/properties/ingredientReferences","#/components/schemas/IngredientReferences/properties/referenceId"],"hypothesis":"Copy preserves internal reference closure, corresponding ingredient links and source state. UUID schemas and copy description do not fully specify identity remapping. This is an opt-in generic graph-copy integrity hypothesis.","seed":717883341,"fixtures":[{"referenceId":"62a9a736-2c63-497b-a984-c47a1b9e9806","note":"sbt-717883341-ingredient-0","quantity":2},{"referenceId":"f009a1a8-be45-4cc3-a7ce-8fbff7420c17","note":"sbt-717883341-ingredient-1","quantity":4}],"step_fixtures":[{"text":"sbt-717883341-step-0","ingredientReferences":[{"referenceId":"62a9a736-2c63-497b-a984-c47a1b9e9806"},{"referenceId":"f009a1a8-be45-4cc3-a7ce-8fbff7420c17"}]},{"text":"sbt-717883341-step-1","ingredientReferences":[{"referenceId":"f009a1a8-be45-4cc3-a7ce-8fbff7420c17"}]}]}.recipe_type+'_1'));waitFor(matchesVerified({"mode":"copy","recipe_type":"Recipe","item_type":"","copy_path":"/api/recipes/{slug}/duplicate","copy_codes":[201],"detail":"/api/recipes/{slug}","parameter":"slug","ingredients":"recipeIngredient","steps":"recipeInstructions","references":"ingredientReferences","reference_id":"referenceId","text":"text","links":[{"field":"unit","target":"IngredientUnit","required":["id","name"]},{"field":"food","target":"IngredientFood","required":["id","name"]}],"required_ready":{"IngredientFood":1,"IngredientUnit":1,"Recipe":1},"sources":["#/paths/~1api~1recipes~1{slug}~1duplicate/post","#/paths/~1api~1recipes~1{slug}/patch/requestBody","#/components/schemas/RecipeIngredient-Input/properties/referenceId","#/components/schemas/RecipeStep/properties/ingredientReferences","#/components/schemas/IngredientReferences/properties/referenceId"],"hypothesis":"Copy preserves internal reference closure, corresponding ingredient links and source state. UUID schemas and copy description do not fully specify identity remapping. This is an opt-in generic graph-copy integrity hypothesis.","seed":717883341,"fixtures":[{"referenceId":"62a9a736-2c63-497b-a984-c47a1b9e9806","note":"sbt-717883341-ingredient-0","quantity":2},{"referenceId":"f009a1a8-be45-4cc3-a7ce-8fbff7420c17","note":"sbt-717883341-ingredient-1","quantity":4}],"step_fixtures":[{"text":"sbt-717883341-step-0","ingredientReferences":[{"referenceId":"62a9a736-2c63-497b-a984-c47a1b9e9806"},{"referenceId":"f009a1a8-be45-4cc3-a7ce-8fbff7420c17"}]},{"text":"sbt-717883341-step-1","ingredientReferences":[{"referenceId":"f009a1a8-be45-4cc3-a7ce-8fbff7420c17"}]}]}.recipe_type+'_1',4));request(bp.Event('F03Ready',{flag:'graph'}));});
bthread('F03 duplicate graph',function(){waitCopyFlag('graph');var expected=copyExpectation();readCopySource(expected,'source-before');duplicateCopySource(expected);request(bp.Event('F03CopyRequested',{expected:expected}));});
ctx.bthread('F03 verify copied graph','F03.Pending',function(state){readCopyTarget(state.expected,false);readCopySource(state.expected,'source-after');readCopyTarget(state.expected,true);request(bp.Event('F03Verified'));request(bp.Event('F03Completed'));});

