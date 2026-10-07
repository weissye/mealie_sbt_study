// Generated stories: explicit entity instances; Context-driven verification.
// HTTP paths and request bodies are confined to interfaces.
ctx.bthread("protectWriteAndReadback", "WriteLock.All", function(lock) {
    sync({block:matchesConflictingWrites(lock.logicalId,lock.owner),waitFor:matchesVerified(lock.logicalId,lock.revision)});
});
ctx.bthread("protectPendingVerification", "Verification.Pending", function(resource) {
    sync({block:matchesMutations(resource.id),waitFor:matchesVerified(resource.id,resource.revision)});
});

// Verification is activated by a Context query, independently of producers.
ctx.bthread("verifyFixtureResourceAfterEveryWrite", "Verification.Pending", function(resource) {
    if(resource.resourceType!=="FixtureResource") return;
    verifyFixtureResource(resource);
    request(bp.Event("ModelVerified",{logicalId:resource.id,revision:resource.revision}));
});

// Instance FixtureResource_1: creation, independent readback, update, independent readback.
bthread("lifecycle FixtureResource_1", function() {
    var parents=waitForDependencies([]);
    createFixtureResource("FixtureResource_1",{"name":"sbt-20261007-FixtureResource-1-name"},parents);
    waitFor(matchesVerified("FixtureResource_1",1));
    updateFixtureResource(getModelEntity("FixtureResource_1"),{"name":"sbt-20261007-FixtureResource_1-updated"});
    waitFor(matchesVerified("FixtureResource_1",2));
});


// Separate Context verifier bthread per pending observation instance.
ctx.bthread('complete observed response','Observation.Pending',function(observation){
    for(var index=0;index<observation.targets.length;index++) {
        readObservedTarget(observation,observation.targets[index],index);
    }
    sync({request:bp.Event('ObservationCompleted',{id:observation.id})});
});
ctx.bthread('protect observation readbacks','Observation.All',function(observation){
    var protectedWrites=bp.EventSet('Observed resources',function(event){
        if(event.name==='ObservationBegin') return !!(event.data && event.data.targets && event.data.targets.some(function(t){return observation.targets.some(function(p){return p.logicalId===t.logicalId;});}));
        var model=event.data && event.data.model;
        return !!(model && (model.action==='update' || model.action==='create') &&
            observation.targets.some(function(t){return (model.affected || [model.logicalId]).indexOf(t.logicalId)>=0;}));
    });
    var completed=bp.EventSet('Observation done',function(event){return !!(event.name==='ObservationCompleted' && event.data && event.data.id===observation.id);});
    sync({block:protectedWrites,waitFor:completed});
});

// Process from #/paths/~1resources~1{id}~1action/post; independent readback from #/paths/~1resources~1{id}/get
bthread("process_0_FixtureResource_1",function(){
    var resource=waitForResource("FixtureResource_1",2);
    observeProcess0(resource,"ID_FixtureResource_1","ROUTE_FixtureResource_1","process_0_FixtureResource_1");
    sync({waitFor:bp.Event("ObservationCompleted",{id:"process_0_FixtureResource_1"})});
});
