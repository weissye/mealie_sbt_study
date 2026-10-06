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
    createIngredientFood("IngredientFood_1",{"name":"sbt-767471548-IngredientFood-1-name","pluralName":"sbt-767471548-IngredientFood-1-pluralName"},parents);
    waitFor(matchesVerified("IngredientFood_1",1));
    updateIngredientFood(getModelEntity("IngredientFood_1"),{"description":"sbt-767471548-IngredientFood_1-updated"});
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
    createIngredientUnit("IngredientUnit_1",{"name":"sbt-767471548-IngredientUnit-1-name","pluralName":"sbt-767471548-IngredientUnit-1-pluralName"},parents);
    waitFor(matchesVerified("IngredientUnit_1",1));
    updateIngredientUnit(getModelEntity("IngredientUnit_1"),{"description":"sbt-767471548-IngredientUnit_1-updated"});
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
    createRecipe("Recipe_1",{"name":"sbt-767471548-Recipe-1-name"},parents);
    waitFor(matchesVerified("Recipe_1",1));
    updateRecipe(getModelEntity("Recipe_1"),{"description":"sbt-767471548-Recipe_1-updated"});
    waitFor(matchesVerified("Recipe_1",2));
});

// Separate process: build two embedded objects sharing independent parents.
bthread("link Recipe_1" ,function(){
    waitForDependencies(["IngredientFood","IngredientUnit","Recipe"]);
    waitForResource("Recipe_1",2);
    var parents=waitForDependencies(["IngredientFood","IngredientUnit"]);
    linkRecipeDependencies(getModelEntity("Recipe_1"),parents);
    waitFor(matchesVerified("Recipe_1",3));
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
    createShoppingListOut("ShoppingListOut_1",{"name":"sbt-767471548-ShoppingListOut-1-name"},parents);
    waitFor(matchesVerified("ShoppingListOut_1",1));
    updateShoppingListOut(getModelEntity("ShoppingListOut_1"),{"name":"sbt-767471548-ShoppingListOut_1-updated"});
    waitFor(matchesVerified("ShoppingListOut_1",2));
});

// Verification is activated by a Context query, independently of producers.
ctx.bthread("verifyShoppingListItemOutAfterEveryWrite", "Verification.Pending", function(resource) {
    if(resource.resourceType!=="ShoppingListItemOut") return;
    verifyShoppingListItemOut(resource);
    request(bp.Event("ModelVerified",{logicalId:resource.id,revision:resource.revision}));
});

// Instance ShoppingListItemOut_1: creation, independent readback, update, independent readback.
bthread("lifecycle ShoppingListItemOut_1", function() {
    var parents=waitForDependencies(["IngredientFood","IngredientUnit","Recipe","ShoppingListOut"]);
    createShoppingListItemOut("ShoppingListItemOut_1",{"note":"sbt-767471548-ShoppingListItemOut-1-note"},parents);
    waitFor(matchesVerified("ShoppingListItemOut_1",1));
    updateShoppingListItemOut(getModelEntity("ShoppingListItemOut_1"),{"note":"sbt-767471548-ShoppingListItemOut_1-updated"});
    waitFor(matchesVerified("ShoppingListItemOut_1",2));
});
