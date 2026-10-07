//@provengo summon context
// Generated DAL: request-derived expectations; observations remain in RTV.
function cloneModel(value) { return JSON.parse(JSON.stringify(value)); }
function resourceModel() {
    var found = ctx.runQuery("Resource.All");
    if (found.length !== 1) throw new Error("Missing or ambiguous fixture resource");
    return found[0];
}
ctx.registerQuery("Resource.All", function(e) { return e.type === "resource"; });
ctx.registerQuery("Verification.Pending", function(e) {
    return e.type === "resource" && e.verifiedRevision < e.revision;
});
ctx.registerQuery("Observation.Pending", function(e) { return e.type === "observation"; });
ctx.registerEffect("POST", function(data) {
    var model = data.model;
    if (!model || model.action !== "create") return;
    ctx.insertEntity(ctx.Entity(model.logicalId, "resource", {
        expected: cloneModel(model.expected), revision: 1, verifiedRevision: 0
    }));
});
ctx.registerEffect("PATCH", function(data) {
    var model = data.model;
    if (!model || model.action !== "update") return;
    var entity = resourceModel();
    var expected = cloneModel(entity.expected);
    Object.keys(model.delta).forEach(function(key) { expected[key] = model.delta[key]; });
    ctx.removeEntity(entity.id);
    ctx.insertEntity(ctx.Entity(entity.id, "resource", {
        expected: expected, revision: entity.revision + 1, verifiedRevision: entity.verifiedRevision
    }));
});
ctx.registerEffect("ModelVerified", function(data) {
    var entity = resourceModel();
    if (entity.revision !== data.revision) throw new Error("Stale verification acknowledgement");
    ctx.removeEntity(entity.id);
    ctx.insertEntity(ctx.Entity(entity.id, "resource", {
        expected: cloneModel(entity.expected), revision: entity.revision, verifiedRevision: data.revision
    }));
});
ctx.registerEffect("ObservationPending", function(data) {
    ctx.insertEntity(ctx.Entity("pending-observation", "observation", {
        expected: cloneModel(data.expected), revision: data.revision
    }));
});
ctx.registerEffect("ObservationCompleted", function() { ctx.removeEntity("pending-observation"); });
function verifiedEvent(revision) {
    return bp.EventSet("Verified revision " + revision, function(e) {
        return e.name === "ModelVerified" && e.data.revision === revision;
    });
}
function waitVerified(revision) {
    while (true) {
        var found = ctx.runQuery("Resource.All");
        if (found.length === 1 && found[0].verifiedRevision >= revision &&
            found[0].verifiedRevision === found[0].revision) return found[0];
        waitFor(bp.EventSet("Any verification", function(e) { return e.name === "ModelVerified"; }));
    }
}
