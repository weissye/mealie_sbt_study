"""Opt-in Context observation renderer for a local fixture acceptance project.

This additive module does not replace existing generation entry points.
"""
import hashlib
import json
from pathlib import Path

DAL = r'''//@provengo summon context
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
'''

INTERFACES = r'''//@provengo summon rest
//@provengo summon rtv
// Generated HTTP boundary and runtime verifiers.
var wirePlan = PLAN;
var session = new RESTSession(BASE, "context-fixture", {headers: {"Content-Type": "application/json"}});
function fixtureRequest(method, path, body, codes, model, callback) {
    var data = {lib: "REST", method: method, url: session.baseURL + path,
        headers: session.defaultHeaders, parameters: {}, expectedResponseCodes: codes,
        model: model, callback: callback};
    if (body !== undefined) data.body = JSON.stringify(body);
    return sync({request: bp.Event(method, data)});
}
function callbackSource(source) { return new Function("response", source); }
function createResource() {
    return fixtureRequest("POST", wirePlan.create.path, wirePlan.initial, wirePlan.create.codes,
        {action: "create", logicalId: "Resource_1", expected: wirePlan.initial},
        callbackSource("var body=JSON.parse(response.body);if(!body.id){pvg.fail('Create identity missing');return;}pvg.rtv.set('RESOURCE_ID',body.id);pvg.log.info('CONTEXT_CREATE_CAPTURED');"));
}
function updateResource() {
    return fixtureRequest("PATCH", wirePlan.read.path.replace("{id}", "@{RESOURCE_ID}"), wirePlan.delta,
        wirePlan.update.codes, {action: "update", logicalId: "Resource_1", delta: wirePlan.delta},
        callbackSource("JSON.parse(response.body);pvg.log.info('CONTEXT_UPDATE_CAPTURED');"));
}
function verifyResource(resource) {
    var source = "var expected=" + JSON.stringify(resource.expected) + ";var body=JSON.parse(response.body);";
    source += "if(body.id!==pvg.rtv.get('RESOURCE_ID')){pvg.fail('Readback identity mismatch');return;}";
    source += "var good=Object.keys(expected).every(function(k){return body[k]===expected[k];});if(!good){pvg.fail('Lifecycle readback mismatch');return;}";
    source += "pvg.rtv.set('BASELINE',JSON.stringify(body));pvg.log.info('CONTEXT_REVISION_VERIFIED revision=" + resource.revision + "');";
    return fixtureRequest("GET", wirePlan.read.path.replace("{id}", "@{RESOURCE_ID}"), undefined,
        wirePlan.read.codes, {action: "read", logicalId: resource.id}, callbackSource(source));
}
function observeFixtureAction(resource) {
    // 500 is admitted solely for evidence collection; contract validity is evaluated below.
    var source = "var codes=" + JSON.stringify(wirePlan.action.codes) + ";";
    source += "var evidence={code:response.code,body:response.body,contractStatusValid:codes.indexOf(response.code)>=0,baseline:JSON.parse(String(pvg.rtv.get('BASELINE')))};";
    source += "pvg.rtv.set('OBSERVATION',JSON.stringify(evidence));pvg.log.info('CONTEXT_RESPONSE_CAPTURED code='+response.code);";
    return fixtureRequest("POST", wirePlan.action.path.replace("{id}", "@{RESOURCE_ID}"), {},
        wirePlan.action.codes.concat([500]), {action: "observe", logicalId: resource.id}, callbackSource(source));
}
function verifyObservedAction(pending) {
    var source = "var expected=" + JSON.stringify(pending.expected) + ";";
    source += "var review=JSON.parse(String(pvg.rtv.get('OBSERVATION')));var actual=JSON.parse(response.body);";
    source += "review.readbackCode=response.code;review.readback=actual;review.contextExpected=expected;review.revision=" + pending.revision + ";";
    source += "review.identityMatches=actual.id===pvg.rtv.get('RESOURCE_ID');review.expectedMatches=Object.keys(expected).every(function(k){return actual[k]===expected[k];});";
    source += "review.baselineMatches=JSON.stringify(actual)===JSON.stringify(review.baseline);review.observationsComplete=true;";
    source += "pvg.rtv.set('OBSERVATION',JSON.stringify(review));pvg.log.info('CONTEXT_OBSERVATION_EVIDENCE '+JSON.stringify(review));";
    source += "if(!review.contractStatusValid||!review.identityMatches){pvg.fail('Deferred contract/identity failure after Context readback');return;}pvg.log.info('CONTEXT_OBSERVATION_PASS');";
    return fixtureRequest("GET", wirePlan.read.path.replace("{id}", "@{RESOURCE_ID}"), undefined,
        wirePlan.read.codes, {action: "readAfterObservation", logicalId: "Resource_1"}, callbackSource(source));
}
'''

STORIES = r'''// Generated by the opt-in Context observation renderer. All HTTP is in interfaces.
bthread("lifecycle Resource_1", function() {
    createResource();
    waitFor(verifiedEvent(1));
    updateResource();
    waitFor(verifiedEvent(2));
});
ctx.bthread("verify each lifecycle write", "Verification.Pending", function(resource) {
    verifyResource(resource);
    request(bp.Event("ModelVerified", {revision: resource.revision}));
});
bthread("observe action after verified lifecycle", function() {
    var resource = waitVerified(2);
    observeFixtureAction(resource);
    request(bp.Event("ObservationPending", {expected: cloneModel(resource.expected), revision: resource.revision}));
});
ctx.bthread("verify action after response capture", "Observation.Pending", function(pending) {
    verifyObservedAction(pending);
    request(bp.Event("ObservationCompleted"));
});
ctx.bthread("protect lifecycle readback", "Verification.Pending", function(resource) {
    sync({block: bp.EventSet("Resource mutations", function(e) {
        return !!(e.data && e.data.model && e.data.model.action === "update");
    }), waitFor: verifiedEvent(resource.revision)});
});
'''


def generate(contract_path, output, base_url):
    if not base_url.startswith('http://127.0.0.1:'):
        raise ValueError('This acceptance renderer is restricted to the local fixture')
    raw = Path(contract_path).read_bytes()
    document = json.loads(raw)
    paths = document['paths']
    def operation(method, summary):
        found = [(path, methods[method]) for path, methods in paths.items()
                 if method in methods and methods[method].get('summary') == summary]
        if len(found) != 1:
            raise ValueError('Missing or ambiguous fixture operation: ' + summary)
        path, value = found[0]
        return {'path': path, 'codes': [int(code) for code in value['responses'] if code.isdigit()],
                'source': '#/paths/' + path.replace('~', '~0').replace('/', '~1') + '/' + method}
    plan = {'create': operation('post', 'Create Resource'), 'read': operation('get', 'Read Resource'),
            'update': operation('patch', 'Update Resource'), 'action': operation('post', 'Observe Action')}
    for key in ('create', 'update'):
        op = paths[plan[key]['path']]['post' if key == 'create' else 'patch']
        example = op['requestBody']['content']['application/json']['example']
        plan['initial' if key == 'create' else 'delta'] = example
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output must be empty')
    output.mkdir(parents=True, exist_ok=True)
    interface_source = INTERFACES.replace('var wirePlan = PLAN;', 'var wirePlan = ' + json.dumps(plan) + ';')
    interface_source = interface_source.replace('new RESTSession(BASE,', 'new RESTSession(' + json.dumps(base_url) + ',')
    values = {'dal.js': DAL, 'interfaces.observation.js': interface_source,
              'stories.observation.js': STORIES}
    for name, value in values.items():
        (output / name).write_text(value, encoding='utf-8', newline='\n')
    (output / 'generation_report.json').write_text(json.dumps({
        'status': 'GENERATED_NOT_EXECUTED', 'contract_sha256': hashlib.sha256(raw).hexdigest(),
        'plan': plan, 'limitations': ['Fixture-only experimental renderer; existing generator entry points unchanged',
                                   'Operation roles selected by fixture summary; not a universal action classifier',
                                   'Context expected state is request-derived; response observations remain in RTV',
                                   'No live F04 or boundary probe is generated']}, indent=2), encoding='utf-8')
    config = output.parent.parent / 'config'
    config.mkdir(exist_ok=True)
    (config / 'provengo.yml').write_text('version: 2\nscenario.max-length: 100\n', encoding='utf-8')
