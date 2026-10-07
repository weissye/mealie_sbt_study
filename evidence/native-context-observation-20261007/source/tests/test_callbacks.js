// Unit harness only: Context/REST mocks do not establish native compatibility.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const project = process.argv[2];
for (const mode of ['control', 'error', 'changed']) {
    const effects = {}, queries = {}, entities = new Map(), values = {}, failures = [], logs = [];
    let state;
    const sandbox = {
        ctx: {registerEffect: (name, fn) => effects[name] = fn, registerQuery: (name, fn) => queries[name] = fn,
            runQuery: name => [...entities.values()].filter(queries[name]),
            Entity: (id, type, data) => ({id, type, ...data}),
            insertEntity: e => entities.set(e.id, e), removeEntity: id => entities.delete(id)},
        bp: {Event: (name, data) => ({name, data}), EventSet: (name, fn) => ({name, fn})},
        RESTSession: function(url, name, options) { this.baseURL = url; this.defaultHeaders = options.headers; },
        pvg: {rtv: {set: (k, v) => values[k] = v, get: k => values[k]},
            fail: message => failures.push(message), log: {info: message => logs.push(message)}},
        sync: ({request: e}) => {
            const d = e.data;
            let response;
            if (d.method === 'POST' && d.model.action === 'create') {
                state = {id: 'fixture-1', ...JSON.parse(d.body)};
                response = {code: 201, body: JSON.stringify(state)};
            } else if (d.method === 'PATCH') {
                Object.assign(state, JSON.parse(d.body));
                response = {code: 200, body: JSON.stringify(state)};
            } else if (d.model.action === 'observe') {
                if (mode === 'changed') state.name = 'injected-change';
                response = {code: mode === 'control' ? 200 : 500,
                    body: mode === 'control' ? JSON.stringify(state) : 'Internal Server Error'};
            } else response = {code: 200, body: JSON.stringify(state)};
            d.callback(response);
            if (effects[e.name]) effects[e.name](d);
            return e;
        }
    };
    vm.createContext(sandbox);
    for (const name of ['dal.js', 'interfaces.observation.js']) {
        vm.runInContext(fs.readFileSync(path.join(project, name), 'utf8'), sandbox);
    }
    sandbox.createResource(); sandbox.verifyResource(sandbox.resourceModel()); effects.ModelVerified({revision: 1});
    sandbox.updateResource(); sandbox.verifyResource(sandbox.resourceModel()); effects.ModelVerified({revision: 2});
    const expected = JSON.parse(JSON.stringify(sandbox.resourceModel().expected));
    sandbox.observeFixtureAction(sandbox.resourceModel());
    effects.ObservationPending({expected, revision: 2});
    sandbox.verifyObservedAction(entities.get('pending-observation'));
    const review = JSON.parse(values.OBSERVATION);
    assert.equal(review.observationsComplete, true);
    assert.equal(review.contractStatusValid, mode === 'control');
    assert.equal(review.baselineMatches, mode !== 'changed');
    assert.equal(review.expectedMatches, mode !== 'changed');
    assert.equal(review.contextExpected.name, 'updated');
    assert.equal(sandbox.resourceModel().expected.name, 'updated');
    assert.equal(failures.length, mode === 'control' ? 0 : 1);
    console.log('CALLBACK_UNIT_PASS: ' + mode);
}
console.log('No native Provengo execution or SUT requests in this unit harness.');
