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
// Authentication uses a separate header set, validates the token, and separates business events.
sandbox.authenticate();const auth=events.pop();
assert.strictEqual(auth.data.url,'http://127.0.0.1:9925/api/auth/token');checks++;
assert.strictEqual(auth.data.headers.Authorization,undefined);checks++;
assert.ok(auth.data.body.includes("System.getenv('SBT_PASSWORD')"));checks++;
auth.data.callback({body:JSON.stringify({access_token:'test-token',token_type:'bearer'})});
assert.strictEqual(runtime.get('SBT_AUTH_TOKEN'),'test-token');checks++;
assert.throws(()=>auth.data.callback({body:'{}'}),/access_token/);checks++;
assert.throws(()=>auth.data.callback({body:JSON.stringify({access_token:'x',token_type:'other'})}),/token type/);checks++;
assert.strictEqual(sandbox.BusinessHTTP.contains(auth),false);checks++;
assert.strictEqual(sandbox.BusinessHTTP.contains({data:{lib:'REST',model:{action:'create'}}}),true);checks++;
// Native first-read binding: recipe POST returns only a route locator.
entities.clear();runtime.clear();
const originalGet=sandbox.pvg.rtv.get;
sandbox.pvg.rtv.get=function(key){return runtime.has(key)?runtime.get(key):'@{'+key+'}';};
sandbox.createRecipe('Fresh',{name:'fresh'},{});act(events.pop(),'fresh-route');
sandbox.verifyRecipe(sandbox.getModelEntity('Fresh'));
act(events.pop(),{id:'first-stable-uuid',name:'fresh'});ack('Fresh',1);
assert.strictEqual(runtime.get('ID_Fresh'),'first-stable-uuid');checks++;
sandbox.verifyRecipe(sandbox.getModelEntity('Fresh'));
assert.throws(()=>act(events.pop(),{id:'different-uuid',name:'fresh'}),/Stable identity changed/);checks++;
sandbox.pvg.rtv.get=originalGet;
// Explicit join-record persistence: do not accept an empty or different recipe link.
entities.clear();runtime.clear();
const parents={};
for(const type of types){parents[type]={id:type};runtime.set('ID_'+type,type+'-real');}
sandbox.createShoppingListItemOut('ITEM',{note:'fixture'},parents);
const itemCreate=events.pop();
const itemBody=itemCreate.data.model.expected;
assert.strictEqual(itemBody.referencedRecipe,undefined);checks++;
assert.strictEqual(itemBody.recipeReferences[0].recipeId,'@{ID_Recipe}');checks++;
act(itemCreate,{createdItems:[{id:'item-real'}],updatedItems:[]});
const expected=JSON.parse(JSON.stringify(sandbox.getModelEntity('ITEM').expected));
function resolved(v){if(typeof v==='string'&&/^@\{[^}]+\}$/.test(v))return runtime.get(v.slice(2,-1));if(Array.isArray(v))return v.map(resolved);if(v&&typeof v==='object'){let out={};Object.keys(v).forEach(k=>out[k]=resolved(v[k]));return out;}return v;}
const actual=resolved(expected);actual.id='item-real';actual.referencedRecipe=null;
sandbox.verifyShoppingListItemOut(sandbox.getModelEntity('ITEM'));act(events.pop(),actual);checks++;
const missing=JSON.parse(JSON.stringify(actual));missing.recipeReferences=[];
sandbox.verifyShoppingListItemOut(sandbox.getModelEntity('ITEM'));
assert.throws(()=>act(events.pop(),missing),/Array mismatch/);checks++;
const wrong=JSON.parse(JSON.stringify(actual));wrong.recipeReferences[0].recipeId='wrong';
sandbox.verifyShoppingListItemOut(sandbox.getModelEntity('ITEM'));
assert.throws(()=>act(events.pop(),wrong),/Value mismatch/);checks++;
// Wire serialization uses one expression, with nested UUID values resolved before JSON encoding.
assert.ok(itemCreate.data.body.startsWith('@{JSON.stringify('));checks++;
const expression=itemCreate.data.body.slice(2,-1);
for(const type of types)sandbox['ID_'+type]=runtime.get('ID_'+type);
const wire=JSON.parse(vm.runInContext(expression,sandbox));
assert.strictEqual(wire.recipeReferences[0].recipeId,'Recipe-real');checks++;
assert.strictEqual(wire.foodId,'IngredientFood-real');checks++;
assert.strictEqual(wire.shoppingListId,'ShoppingListOut-real');checks++;
assert.strictEqual(wire.recipeReferences[0].recipeQuantity,1);checks++;
const escaped=sandbox.requestBodyExpression({note:'quote " slash \\ and newline\n',refs:[{id:'@{ID_Recipe}'}]});
assert.strictEqual(JSON.parse(vm.runInContext(escaped.slice(2,-1),sandbox)).note,'quote " slash \\ and newline\n');checks++;
console.log(JSON.stringify({status:'CALLBACK_AND_DAL_UNIT_AUDIT_PASS',checks,native_provengo_executed:false,sut_requests:0}));
