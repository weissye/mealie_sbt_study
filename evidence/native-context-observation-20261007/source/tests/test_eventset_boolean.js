const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const cp = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const python = process.env.PYTHON || 'python3';
const source = cp.execFileSync(python, ['-c', 'from generator_v56.render.context_observation import STORIES; print(STORIES)'], {cwd: root, encoding: 'utf8'});
let protect, predicate;
vm.runInNewContext(source, {
    bthread: () => {},
    ctx: {bthread: (name, query, fn) => { if(name === 'protect lifecycle readback') protect = fn; }},
    sync: options => {predicate = options.block;},
    verifiedEvent: () => ({}),
    bp: {EventSet: (name, fn) => fn}
});
protect({revision: 1});
for (const [event, expected] of [
    [{},false], [{name:'ModelVerified'},false], [{data:{}},false],
    [{data:{model:{action:'read'}}},false], [{data:{model:{action:'update'}}},true]
]) {
    assert.equal(typeof predicate(event), 'boolean');
    assert.equal(predicate(event), expected);
}
console.log('EVENTSET_BOOLEAN_REGRESSION_PASS: 5 cases');
