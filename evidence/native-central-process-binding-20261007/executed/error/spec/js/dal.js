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

ctx.registerQuery("FixtureResource.Ready",function(e){return e.type==="resource" && e.resourceType==="FixtureResource" && e.verifiedRevision===e.revision;});


ctx.registerQuery('Observation.All',function(e){return e.type==='observation';});
ctx.registerQuery('Observation.Pending',function(e){return e.type==='observation' && e.ready;});
ctx.registerEffect('ObservationBegin',function(data){
    if(ctx.runQuery('Observation.All').some(function(e){return e.id===data.id;})) throw new Error('Duplicate observation');
    data.targets.forEach(function(target){
        var resource=getModelEntity(target.logicalId);
        if(JSON.stringify(resource.expected)!==JSON.stringify(target.expected)) throw new Error('Expected readback differs from DAL');
        if(resource.revision!==resource.verifiedRevision) throw new Error('Unverified observation target');
        if(!target.identityKey || !target.identityField || !target.url || !target.codes.length) throw new Error('Incomplete observation binding');
    });
    ctx.insertEntity(ctx.Entity(data.id,'observation',{targets:cloneExpected(data.targets),ready:false}));
});
ctx.registerEffect('ObservationReady',function(data){
    var found=ctx.runQuery('Observation.All').filter(function(e){return e.id===data.id;});
    if(found.length!==1 || found[0].ready) throw new Error('Missing/duplicate captured action');
    var targets=cloneExpected(found[0].targets);
    ctx.removeEntity(data.id);
    ctx.insertEntity(ctx.Entity(data.id,'observation',{targets:targets,ready:true}));
});
ctx.registerEffect('ObservationCompleted',function(data){ctx.removeEntity(data.id);});

