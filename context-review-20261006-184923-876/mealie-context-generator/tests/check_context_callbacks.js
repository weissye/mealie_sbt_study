// Unit audit of generated callbacks/effects. This is NOT a Provengo scheduler.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=process.argv[2];
const entities=new Map(),effects=new Map(),queries=new Map(),runtime=new Map(),events=[];
const sandbox={console,JSON,Object,Array,Error,Number,String,
 pvg:{fail(message){throw new Error(message);},rtv:{get(k){return runtime.get(k);},set(k,v){runtime.set(k,v);}}},
 bp:{Event:(name,data)=>({name,data}),EventSet:(name,predicate)=>({name,contains:predicate})},
 RESTSession:function(baseURL,name,opts){this.baseURL=baseURL;this.defaultHeaders=opts.headers;},
 sync(spec){if(!spec.request)throw new Error('WAIT');events.push(spec.request);return spec.request;},
 request(e){events.push(e);return e;},waitFor(){throw new Error('WAIT');},
 ctx:{Entity:(id,type,props)=>Object.assign({id,type},props),insertEntity(e){entities.set(e.id,e);},removeEntity(id){entities.delete(id);},registerQuery(n,p){queries.set(n,p);},runQuery(n){return [...entities.values()].filter(queries.get(n));},registerEffect(n,f){effects.set(n,f);},bthread(){}}
};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(root+'/interfaces.mealie.js','utf8'),sandbox);
vm.runInContext(fs.readFileSync(root+'/dal.js','utf8'),sandbox);
function dispatch(e){if(effects.has(e.name))effects.get(e.name)(e.data);}
function act(e,body){e.data.callback({code:e.data.expectedResponseCodes[0],body:JSON.stringify(body)});dispatch(e);}
function ack(id,rev){dispatch({name:'ModelVerified',data:{logicalId:id,revision:rev}});}
let checks=0;
// Creation identity + DAL expected state are independent of server response extras.
sandbox.createIngredientFood('F',{name:'food'},{});let create=events.pop();act(create,{id:'food-real',name:'food',description:'untrusted'});
assert.strictEqual(sandbox.getModelEntity('F').expected.description,undefined);checks++;
sandbox.verifyIngredientFood(sandbox.getModelEntity('F'));let read=events.pop();act(read,{id:'food-real',name:'food'});ack('F',1);checks++;
sandbox.verifyIngredientFood(sandbox.getModelEntity('F'));assert.throws(()=>act(events.pop(),{id:'other',name:'food'}),/identity/);checks++;
sandbox.verifyIngredientFood(sandbox.getModelEntity('F'));assert.throws(()=>act(events.pop(),{id:'food-real',name:'changed'}),/Value mismatch/);checks++;
// Patch preparation and typed references resolve at actuation rather than sampling.
sandbox.updateIngredientFood(sandbox.getModelEntity('F'),{description:'new'});
let update=events.pop(),prepare=events.pop(),begin=events.pop();dispatch(begin);
act(prepare,{id:'food-real',name:'food',description:'old'});
assert.strictEqual(JSON.parse(runtime.get('UPDATE_F')).description,'new');act(update,{});checks++;
sandbox.verifyIngredientFood(sandbox.getModelEntity('F'));act(events.pop(),{id:'food-real',name:'food',description:'new'});ack('F',2);
assert.strictEqual(sandbox.getModelEntity('F').expected.description,'new');assert.strictEqual(sandbox.ctx.runQuery('WriteLock.All').length,0);checks++;
// Nested array mismatch must fail even when top-level identity is correct.
sandbox.createRecipe('R',{name:'recipe'},{});act(events.pop(),'route');
sandbox.verifyRecipe(sandbox.getModelEntity('R'));act(events.pop(),{id:'recipe-real',name:'recipe'});ack('R',1);
let source=sandbox.validationSource({recipeIngredient:[{quantity:2,food:{id:'@{ID_F}'}}]},'ID_R',null);
let cb=sandbox.callbackFromSource(source);
cb({body:JSON.stringify({id:'recipe-real',recipeIngredient:[{quantity:2,food:{id:'food-real'}}]})});checks++;
assert.throws(()=>cb({body:JSON.stringify({id:'recipe-real',recipeIngredient:[{quantity:1,food:{id:'food-real'}}]})}),/Value mismatch/);checks++;
// Nested update preparation must turn symbolic IDs into typed wire IDs.
sandbox.updateRecipe(sandbox.getModelEntity('R'),{recipeIngredient:[{quantity:2,food:{id:'@{ID_F}',name:'food'}}]});
let nestedWrite=events.pop(),nestedPrepare=events.pop(),nestedBegin=events.pop();dispatch(nestedBegin);
act(nestedPrepare,{id:'recipe-real',name:'recipe'});
assert.strictEqual(JSON.parse(runtime.get('UPDATE_R')).recipeIngredient[0].food.id,'food-real');checks++;
// All independent parent readiness orders are accepted. Missing parents wait.
const types=['IngredientFood','IngredientUnit','Recipe','ShoppingListOut'];
function permutations(a){return a.length?a.flatMap((x,i)=>permutations(a.filter((_,k)=>k!==i)).map(p=>[x,...p])):[[]];}
for(const order of permutations(types)){
 entities.clear();
 for(let i=0;i<order.length;i++){
  const type=order[i];entities.set(type,{id:type,type:'resource',resourceType:type,expected:{name:type},revision:1,verifiedRevision:1});
  if(i<3)assert.throws(()=>sandbox.waitForDependencies(types),/WAIT/);
 }
 let parents=sandbox.waitForDependencies(types);assert.strictEqual(Object.keys(parents).length,4);checks++;
}
// Guard includes child writes that affect a parent, and permits its owning write.
let guard=sandbox.matchesConflictingWrites('LIST','owner');
assert(guard.contains({name:'POST',data:{model:{action:'create',logicalId:'ITEM',affected:['ITEM','LIST']}}}));
assert(!guard.contains({name:'PUT',data:{model:{action:'update',logicalId:'LIST',owner:'owner'}}}));checks+=2;
console.log(JSON.stringify({status:'CALLBACK_AND_DAL_UNIT_AUDIT_PASS',checks,native_provengo_executed:false,sut_requests:0}));
