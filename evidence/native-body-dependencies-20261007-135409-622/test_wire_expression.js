const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
let events=[];
const box={RESTSession:function(url,name,opts){this.baseURL=url;this.defaultHeaders=opts.headers;},
 bp:{Event:(name,data)=>({name,data}),EventSet:(name,fn)=>({name,fn})},sync:opts=>{events.push(opts.request);return opts.request;}};
vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8'),box);
const resources={FixtureResource:{id:'FixtureResource_1',expected:{name:'r'}},Food:{id:'Food_1',expected:{name:'f'}},Unit:{id:'Unit_1',expected:{name:'u'}}};
box.cloneExpected=v=>JSON.parse(JSON.stringify(v));
box.observeProcess0(resources,{FixtureResource:'ID_FixtureResource_1',Food:'ID_Food_1',Unit:'ID_Unit_1'},{FixtureResource:'ROUTE_FixtureResource_1',Food:'ROUTE_Food_1',Unit:'ROUTE_Unit_1'},'test');
const event=events.find(e=>e.name==='POST');assert(event);
const phrase=event.data.body;assert(phrase.startsWith('@{JSON.stringify('));
const body=JSON.parse(vm.runInNewContext(phrase.slice(2,-1),{ID_Food_1:'food-actual',ID_Unit_1:'unit-actual'}));
assert.deepEqual(body,{food:{name:'f',id:'food-actual'},unit:{name:'u',id:'unit-actual'},amount:1});
assert.equal(events[0].name,'ObservationBegin');assert.equal(events[0].data.targets.length,3);
console.log('BODY_WIRE_EXPRESSION_PASS: two actual identity bindings, three readback targets; mocked transport only');
