//@provengo summon context
// Generated Context DAL using the built-in Provengo Context library.

// Context contains expected request-derived state, never a copy of an observed response.
// Real identities and server snapshots are kept only in runtime variables at the boundary.
function getModelEntity(id) {
    var found=ctx.runQuery("Resource.All").filter(function(e){return e.id===id;});
    if(found.length!==1) throw new Error("Missing/ambiguous Context resource "+id);
    return found[0];
}
function cloneExpected(value) {return JSON.parse(JSON.stringify(value));}
function applyInterfaceEffect(event) {
    var data=extractEventData(event);
    if(data && data.action==="contribute") {applyContributionEffect(data);return;}
    if(!data || (data.action!=="create" && data.action!=="update")) return;
    if(data.action==="create") {
        ctx.insertEntity(ctx.Entity(data.logicalId,"resource",{
            resourceType:data.type,expected:cloneExpected(data.expected),revision:1,verifiedRevision:0
        }));
    } else {
        var resource=getModelEntity(data.logicalId);
        var expected=cloneExpected(resource.expected);
        Object.keys(data.expected).forEach(function(k){expected[k]=cloneExpected(data.expected[k]);});
        ctx.removeEntity(resource.id);
        ctx.insertEntity(ctx.Entity(resource.id,"resource",{
            resourceType:resource.resourceType,expected:expected,revision:resource.revision+1,
            verifiedRevision:resource.verifiedRevision
        }));
    }
}
["POST","PUT","PATCH"].forEach(function(method){
    ctx.registerEffect(method,function(data){applyInterfaceEffect(bp.Event(method,data));});
});
ctx.registerEffect("ModelWriteBegin",function(data){
    ctx.insertEntity(ctx.Entity("lock_"+data.owner,"writeLock",{logicalId:data.logicalId,owner:data.owner,revision:data.revision}));
});
ctx.registerQuery("WriteLock.All",function(e){return e.type==="writeLock";});
ctx.registerEffect("ModelVerified",function(data){
    ctx.runQuery("WriteLock.All").forEach(function(lock){
        if(lock.logicalId===data.logicalId && lock.revision===data.revision) ctx.removeEntity(lock.id);
    });
    var resource=getModelEntity(data.logicalId);
    if(resource.revision!==data.revision) throw new Error("Stale verification acknowledgement");
    ctx.removeEntity(resource.id);
    ctx.insertEntity(ctx.Entity(resource.id,"resource",{
        resourceType:resource.resourceType,expected:cloneExpected(resource.expected),
        revision:resource.revision,verifiedRevision:data.revision
    }));
});
ctx.registerQuery("Resource.All",function(e){return e.type==="resource";});
ctx.registerQuery("Verification.Pending",function(e){return e.type==="resource" && e.verifiedRevision<e.revision;});
function waitForResource(logicalId, revision) {
    while(true) {
        var resources=ctx.runQuery("Resource.All").filter(function(e){return e.id===logicalId;});
        if(resources.length===1 && resources[0].verifiedRevision>=revision && resources[0].verifiedRevision===resources[0].revision) return resources[0];
        waitFor(bp.EventSet("Resource verified "+logicalId,function(event){return event.name==="ModelVerified" && event.data.logicalId===logicalId;}));
    }
}
function readyResources(type) {
    return ctx.runQuery(type+".Ready");
}
function waitForDependencies(types) {
    // Each wakeup re-evaluates ALL dependencies. No fixed ordering of parents.
    var chosen={};
    while(true) {
        var missing=[];
        types.forEach(function(type){
            if(chosen[type]) return;
            var available=readyResources(type);
            if(available.length) chosen[type]=available[0]; else missing.push(type);
        });
        if(!missing.length) return chosen;
        waitFor(bp.EventSet("Any required dependency becomes verified",function(event){
            return event.name==="ModelVerified";
        }));
    }
}

ctx.registerQuery("IngredientFood.Ready",function(e){return e.type==="resource" && e.resourceType==="IngredientFood" && e.verifiedRevision===e.revision;});
ctx.registerQuery("IngredientUnit.Ready",function(e){return e.type==="resource" && e.resourceType==="IngredientUnit" && e.verifiedRevision===e.revision;});
ctx.registerQuery("Recipe.Ready",function(e){return e.type==="resource" && e.resourceType==="Recipe" && e.verifiedRevision===e.revision;});
ctx.registerQuery("ShoppingListOut.Ready",function(e){return e.type==="resource" && e.resourceType==="ShoppingListOut" && e.verifiedRevision===e.revision;});
ctx.registerQuery("ShoppingListItemOut.Ready",function(e){return e.type==="resource" && e.resourceType==="ShoppingListItemOut" && e.verifiedRevision===e.revision;});

// Opt-in contribution ledger. Expected state changes ONLY from selected model actions.
var contributionPlan={"operation_path":"/api/households/shopping/lists/{item_id}/recipe","codes":[200],"recipe_type":"Recipe","list_type":"ShoppingListOut","item_type":"ShoppingListItemOut","ingredients_field":"recipeIngredient","quantity_field":"quantity","recipe_key":"recipeId","increment_field":"recipeIncrementQuantity","item_array":"listItems","item_refs":"recipeReferences","list_refs":"recipeReferences","reference_quantity":"recipeQuantity","reference_scale":"recipeScale","owner_key":"shoppingListId","child_key":"shoppingListItemId","keys":[{"source":"unit","item":"unitId"},{"source":"food","item":"foodId"}],"recipe_detail":"/api/recipes/{slug}","recipe_parameter":"slug","list_detail":"/api/households/shopping/lists/{item_id}","list_parameter":"item_id","item_detail":"/api/households/shopping/items/{item_id}","item_parameter":"item_id","sources":["#/paths/~1api~1households~1shopping~1lists~1{item_id}~1recipe/post","#/paths/~1api~1recipes~1{slug}/patch/requestBody","#/paths/~1api~1households~1shopping~1items~1{item_id}/get","#/paths/~1api~1households~1shopping~1lists~1{item_id}/get"],"inference":"summary Add; array input; source Id; numeric Increment; unique container response; schema-linked item and references","hypothesis":"shared dependency keys merge into one item; quantities add sum(source quantities)*increment; container reference quantity tracks sum(increments); item reference quantity times scale equals the DAL item quantity. This is a falsifiable generic hypothesis, not a guarantee encoded by OpenAPI.","scales":[1,0.5],"fixture_quantities":[2,4]};
function contributionExpected(recipe, list, previous, scale) {
    var rows=recipe.expected[contributionPlan.ingredients_field];
    if(!rows || rows.length!==2) throw new Error("Contribution requires two linked ingredients");
    var amount=0, keys={};
    rows.forEach(function(row,index){
        var q=row[contributionPlan.quantity_field];
        if(typeof q!=="number" || !isFinite(q)) throw new Error("Non-numeric source quantity");
        amount+=q*scale;
        contributionPlan.keys.forEach(function(k){
            var id=row[k.source] && row[k.source].id;
            if(!id) throw new Error("Unbound source dependency");
            if(index && keys[k.item]!==id) throw new Error("Sources do not share dependency keys");
            keys[k.item]=id;
        });
    });
    return {quantity:(previous ? previous.quantity : 0)+amount,
        referenceQuantity:(previous ? previous.referenceQuantity : 0)+scale,keys:keys,
        recipeId:"@{ID_"+recipe.id+"}",listId:"@{ID_"+list.id+"}",recipeExpected:cloneExpected(recipe.expected)};
}
function applyContributionEffect(data) {
    var old=ctx.runQuery("Contribution.All");
    if(old.length) ctx.removeEntity(old[0].id);
    ctx.insertEntity(ctx.Entity("contribution_1","contribution",{
        stage:data.stage,expected:cloneExpected(data.expected),verified:false,
        recipe:data.recipe,list:data.list
    }));
}
ctx.registerQuery("Contribution.All",function(e){return e.type==="contribution";});
ctx.registerQuery("Contribution.Pending",function(e){return e.type==="contribution" && !e.verified;});
ctx.registerEffect("ContributionVerified",function(data){
    var e=ctx.runQuery("Contribution.All")[0];
    if(!e || e.stage!==data.stage) throw new Error("Stale contribution acknowledgement");
    ctx.removeEntity(e.id);
    ctx.insertEntity(ctx.Entity(e.id,"contribution",{stage:e.stage,expected:e.expected,verified:true,recipe:e.recipe,list:e.list}));
});

