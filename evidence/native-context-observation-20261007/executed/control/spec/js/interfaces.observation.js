//@provengo summon rest
//@provengo summon rtv
// Generated HTTP boundary and runtime verifiers.
var wirePlan = {"create": {"path": "/resources", "codes": [201], "source": "#/paths/~1resources/post"}, "read": {"path": "/resources/{id}", "codes": [200], "source": "#/paths/~1resources~1{id}/get"}, "update": {"path": "/resources/{id}", "codes": [200], "source": "#/paths/~1resources~1{id}/patch"}, "action": {"path": "/resources/{id}/action", "codes": [200], "source": "#/paths/~1resources~1{id}~1action/post"}, "initial": {"name": "initial"}, "delta": {"name": "updated"}};
var session = new RESTSession("http://127.0.0.1:63349", "context-fixture", {headers: {"Content-Type": "application/json"}});
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
