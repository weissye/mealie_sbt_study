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

var copyPlan={"mode":"copy","recipe_type":"Recipe","item_type":"","copy_path":"/api/recipes/{slug}/duplicate","copy_codes":[201],"detail":"/api/recipes/{slug}","parameter":"slug","ingredients":"recipeIngredient","steps":"recipeInstructions","references":"ingredientReferences","reference_id":"referenceId","text":"text","links":[{"field":"unit","target":"IngredientUnit","required":["id","name"]},{"field":"food","target":"IngredientFood","required":["id","name"]}],"required_ready":{"IngredientFood":1,"IngredientUnit":1,"Recipe":1},"sources":["#/paths/~1api~1recipes~1{slug}~1duplicate/post","#/paths/~1api~1recipes~1{slug}/patch/requestBody","#/components/schemas/RecipeIngredient-Input/properties/referenceId","#/components/schemas/RecipeStep/properties/ingredientReferences","#/components/schemas/IngredientReferences/properties/referenceId"],"hypothesis":"Copy preserves internal reference closure, corresponding ingredient links and source state. UUID schemas and copy description do not fully specify identity remapping. This is an opt-in generic graph-copy integrity hypothesis.","seed":717883341,"fixtures":[{"referenceId":"62a9a736-2c63-497b-a984-c47a1b9e9806","note":"sbt-717883341-ingredient-0","quantity":2},{"referenceId":"f009a1a8-be45-4cc3-a7ce-8fbff7420c17","note":"sbt-717883341-ingredient-1","quantity":4}],"step_fixtures":[{"text":"sbt-717883341-step-0","ingredientReferences":[{"referenceId":"62a9a736-2c63-497b-a984-c47a1b9e9806"},{"referenceId":"f009a1a8-be45-4cc3-a7ce-8fbff7420c17"}]},{"text":"sbt-717883341-step-1","ingredientReferences":[{"referenceId":"f009a1a8-be45-4cc3-a7ce-8fbff7420c17"}]}]};
ctx.registerQuery('F03.Flags',function(e){return e.type==='f03flag';});
ctx.registerEffect('F03Ready',function(d){ctx.insertEntity(ctx.Entity('f03_'+d.flag,'f03flag',{flag:d.flag}));});
function waitCopyFlag(flag){while(!ctx.runQuery('F03.Flags').some(function(e){return e.flag===flag;}))waitFor(bp.EventSet('F03 ready '+flag,function(e){return e.name==='F03Ready'&&e.data.flag===flag;}));}
function waitCopyParents(){while(true){var missing=Object.keys(copyPlan.required_ready).filter(function(t){return !readyResources(t).some(function(e){return e.verifiedRevision>=2;});});if(!missing.length)return;waitFor(bp.EventSet('F03 dependency verified',function(e){return e.name==='ModelVerified';}));}}
ctx.registerQuery('F03.Pending',function(e){return e.type==='f03verification';});
ctx.registerEffect('F03CopyRequested',function(d){ctx.insertEntity(ctx.Entity('f03_pending','f03verification',{expected:d.expected}));});
ctx.registerEffect('F03Verified',function(){ctx.removeEntity('f03_pending');});

