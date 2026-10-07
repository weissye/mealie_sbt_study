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
    if(data && data.action==="f02") {applyF02Effect(data);return;}
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

var removalPlan={"operation_path":"/api/households/shopping/lists/{item_id}/recipe","codes":[200],"recipe_type":"Recipe","list_type":"ShoppingListOut","item_type":"ShoppingListItemOut","ingredients_field":"recipeIngredient","quantity_field":"quantity","recipe_key":"recipeId","increment_field":"recipeIncrementQuantity","item_array":"listItems","item_refs":"recipeReferences","list_refs":"recipeReferences","reference_quantity":"recipeQuantity","reference_scale":"recipeScale","owner_key":"shoppingListId","child_key":"shoppingListItemId","keys":[{"source":"unit","item":"unitId"},{"source":"food","item":"foodId"}],"recipe_detail":"/api/recipes/{slug}","recipe_parameter":"slug","list_detail":"/api/households/shopping/lists/{item_id}","list_parameter":"item_id","item_detail":"/api/households/shopping/items/{item_id}","item_parameter":"item_id","sources":["#/paths/~1api~1households~1shopping~1lists~1{item_id}~1recipe/post","#/paths/~1api~1recipes~1{slug}/patch/requestBody","#/paths/~1api~1households~1shopping~1items~1{item_id}/get","#/paths/~1api~1households~1shopping~1lists~1{item_id}/get","#/paths/~1api~1foods~1merge/put","#/paths/~1api~1households~1shopping~1lists~1{item_id}~1recipe~1{recipe_id}~1delete/post"],"inference":"summary Add; array input; source Id; numeric Increment; unique container response; schema-linked item and references","hypothesis":"Canonical merge preserves aggregate quantities; removing one recipe subtracts its current canonical ingredient aggregate and leaves the manual baseline. Not implied by OpenAPI alone.","scales":[1,0.5],"fixture_quantities":[2,2],"mode":"removal","variant":"food","merge_type":"IngredientFood","merge_source_field":"food","merge_item_key":"foodId","merge_path":"/api/foods/merge","merge_method":"PUT","merge_codes":[200],"merge_from":"fromFood","merge_to":"toFood","remove_path":"/api/households/shopping/lists/{item_id}/recipe/{recipe_id}/delete","remove_codes":[200],"decrement":"recipeDecrementQuantity","manual_quantity":7,"dependency_links":[{"field":"unit","target":"IngredientUnit","required":["id","name"]},{"field":"food","target":"IngredientFood","required":["id","name"]}],"item_create_path":"/api/households/shopping/items","item_create_codes":[201],"required_ready":{"IngredientFood":2,"IngredientUnit":1,"Recipe":1,"ShoppingListOut":1},"skip_merge":false,"zero_fields_js":"delta[\"recipeServings\"]=1;delta[\"recipeYieldQuantity\"]=1;"};
ctx.registerQuery("F02.Flags",function(e){return e.type==="f02flag";});
ctx.registerEffect("F02Ready",function(d){ctx.insertEntity(ctx.Entity("f02_"+d.flag,"f02flag",{flag:d.flag}));});
function waitF02Flag(flag){while(!ctx.runQuery("F02.Flags").some(function(e){return e.flag===flag;}))waitFor(bp.EventSet("F02 ready "+flag,function(e){return e.name==="F02Ready"&&e.data.flag===flag;}));}
function waitF02Parents(){
 while(true){var missing=Object.keys(removalPlan.required_ready).filter(function(t){return readyResources(t).filter(function(e){return e.verifiedRevision>=2;}).length<removalPlan.required_ready[t];});if(!missing.length)return;waitFor(bp.EventSet("Any F02 dependency verified",function(e){return e.name==="ModelVerified";}));}
}
function f02Parents(){var p={};Object.keys(removalPlan.required_ready).forEach(function(t){p[t]=readyResources(t).sort(function(a,b){return a.id<b.id?-1:1;});});return p;}
function f02Model(stage){
 var parents=f02Parents(),rows=[],manual={},recipe=getModelEntity(removalPlan.recipe_type+"_1"),list=getModelEntity(removalPlan.list_type+"_1");
 removalPlan.keys.forEach(function(k){var l=removalPlan.dependency_links.filter(function(x){return x.field===k.source;})[0];manual[k.item]="@{ID_"+parents[l.target][0].id+"}";});
 removalPlan.fixture_quantities.forEach(function(q,i){var row={quantity:q,keys:{}};removalPlan.keys.forEach(function(k){var l=removalPlan.dependency_links.filter(function(x){return x.field===k.source;})[0];var index=k.source===removalPlan.merge_source_field&&i===1&&(stage===1||removalPlan.skip_merge)?1:0;row.keys[k.item]="@{ID_"+parents[l.target][index].id+"}";});rows.push(row);});
 var expectedRows=[{quantity:removalPlan.manual_quantity,keys:manual}];if(stage<3)expectedRows=expectedRows.concat(rows);
 var total=0;expectedRows.forEach(function(r){total+=r.quantity;});
 return {stage:stage,rows:expectedRows,recipeRows:rows,total:total,association:stage===3?0:1,recipeId:"@{ID_"+recipe.id+"}",listId:"@{ID_"+list.id+"}",recipeName:recipe.expected.name};
}
function applyF02Effect(d){var old=ctx.runQuery("F02.Stages");old.forEach(function(e){ctx.removeEntity(e.id);});ctx.insertEntity(ctx.Entity("f02_stage","f02stage",{stage:d.expected.stage,expected:cloneExpected(d.expected),verified:false}));}
ctx.registerQuery("F02.Stages",function(e){return e.type==="f02stage";});
ctx.registerQuery("F02.Pending",function(e){return e.type==="f02stage"&&!e.verified;});
ctx.registerEffect("F02Verified",function(d){var e=ctx.runQuery("F02.Stages")[0];ctx.removeEntity(e.id);ctx.insertEntity(ctx.Entity(e.id,"f02stage",{stage:e.stage,expected:cloneExpected(e.expected),verified:true}));});
function waitF02Stage(stage){while(!ctx.runQuery("F02.Stages").some(function(e){return e.stage===stage&&e.verified;}))waitFor(bp.EventSet("F02 stage verified "+stage,function(e){return e.name==="F02Verified"&&e.data.stage===stage;}));}

