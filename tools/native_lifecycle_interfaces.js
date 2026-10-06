// Transport and semantic policies are separate from behavioral scheduling.
var svc = new RESTSession(MODEL.base_url,"native-lifecycle");
function nget(key){var v=pvg.rtv.get(key);if(v===undefined||v===null)throw new Error("Missing runtime binding: "+key);return v;}
function njson(key){return JSON.parse(nget(key));}
function nput(key,value){pvg.rtv.set(key,typeof value==="string"?value:JSON.stringify(value));}
function nfail(code,evidence){bp.log.info("NATIVE_ORACLE "+JSON.stringify({status:code,evidence:evidence}));pvg.fail(code);throw new Error(code);}
function neq(actual,expected,label){if(JSON.stringify(actual)!==JSON.stringify(expected))nfail("STATE_MISMATCH",{label:label,expected:expected,observed:actual});}
function nnear(a,b){return typeof a==="number"&&isFinite(a)&&Math.abs(a-b)<=MODEL.arithmetic.tolerance;}
function nvalue(v){
  if(typeof v==="string"){
    if(v.indexOf("$snapshot:")===0)return njson(v.substring(10));
    var m=/^@\{([^}]+)\}$/.exec(v);if(m)return nget(m[1]);
    return v.replace(/\$namespace/g,MODEL.namespace);
  }
  if(Array.isArray(v))return v.map(nvalue);
  if(v&&typeof v==="object"){var out={};Object.keys(v).forEach(function(k){out[k]=nvalue(v[k]);});return out;}
  return v;
}
function nwire(v){if(typeof v==="string")return v.replace(/\$namespace/g,MODEL.namespace);if(Array.isArray(v))return v.map(nwire);if(v&&typeof v==="object"){var o={};Object.keys(v).forEach(function(k){o[k]=nwire(v[k]);});return o;}return v;}
function npath(obj,path){return path.split('.').reduce(function(o,k){return o===undefined?undefined:o[k];},obj);}
function nheaders(){return {Authorization:"Bearer @{native_token}","Content-Type":"application/json"};}
function nativeLogin(){svc.post(MODEL.authentication.path,{headers:{"Content-Type":"application/x-www-form-urlencoded"},body:"grant_type=password&username=@{getEnv('MEALIE_ACCEPTANCE_USERNAME')}&password=@{getEnv('MEALIE_ACCEPTANCE_PASSWORD')}",expectedResponseCodes:[200],callback:function(response){var b=JSON.parse(response.body);if(!b.access_token)throw new Error("Authentication returned no token");nput("native_token",b.access_token);pvg.success("AUTHENTICATION_PASS");}});}
function nativeRequest(operation,body,callback){var op=MODEL.operations[operation],args={headers:nheaders(),expectedResponseCodes:op.codes,callback:callback};if(body!==undefined)args.body=typeof body==="string"?body:JSON.stringify(nwire(body));svc[op.method.toLowerCase()](op.url||op.path,args);}
function nreceipt(label,response){var b=JSON.parse(response.body||'null');bp.log.info("NATIVE_RECEIPT "+JSON.stringify({operation:label,status:response.status||response.statusCode,body:b}));return b;}
function ncapture(action,b){Object.keys(action.capture||{}).forEach(function(key){var path=action.capture[key],v=path==='$'?b:npath(b,path);if(v===undefined||v===null)throw new Error("Response identity missing: "+key);nput(key,v);});}
function ncheck(check,b){
  Object.keys(check.snapshot_fields||{}).forEach(function(k){var v=npath(b,check.snapshot_fields[k]);if(v===undefined)throw new Error("Snapshot field absent: "+k);v=JSON.parse(JSON.stringify(v));Object.keys((check.snapshot_overrides||{})[k]||{}).forEach(function(f){v[f]=check.snapshot_overrides[k][f];});nput(k,v);});
  if(check.equals)Object.keys(check.equals).forEach(function(path){neq(npath(b,path),nvalue(check.equals[path]),path);});
  if(check.snapshot)nput(check.snapshot,b);
  if(check.prepare){var op=MODEL.operations[check.prepare.operation],out={};(op.writable_fields||Object.keys(op.schema.properties||{})).forEach(function(k){if(b[k]!==undefined)out[k]=b[k];});Object.keys(check.prepare.override).forEach(function(k){out[k]=nvalue(check.prepare.override[k]);});nput(check.prepare.variable,out);}
  if(check.arithmetic) nquantity(check.arithmetic,b);
}
function naggregate(rows){var total=0;rows.forEach(function(row){var food=row.foodId||(row.food&&row.food.id),unit=row.unitId||(row.unit&&row.unit.id);if(food===nget('food_id')&&unit===nget('unit_id')){if(typeof row.quantity!=='number'||!isFinite(row.quantity))throw new Error('Nonnumeric contribution');total+=row.quantity;}});return total;}
function nquantity(policy,list){
  neq(list.id,nget('list_id'),'list identity');
  var recipe=njson('recipe_current');neq(recipe.id,nget('recipe_id'),'recipe identity');
  if(recipe.recipeIngredient.length!==2)throw new Error('Two duplicate-key rows were not retained');
  recipe.recipeIngredient.forEach(function(i){neq(i.food.id,nget('food_id'),'ingredient food');neq(i.unit.id,nget('unit_id'),'ingredient unit');if(!nnear(i.quantity,2))throw new Error('Unexpected fixture ingredient quantity');});
  var r=naggregate(recipe.recipeIngredient),q=naggregate(list.listItems||[]),refs=list.recipeReferences||[],association=0;
  refs.forEach(function(ref){if(ref.recipeId===recipe.id){if(typeof ref.recipeQuantity!=='number')throw new Error('Recipe association quantity missing');association+=ref.recipeQuantity;}});
  var expected=policy.initial!==undefined?policy.initial:njson('quantity_before').list+policy.scale*r;
  var expectedAssociation=policy.initial!==undefined?0:njson('quantity_before').association+policy.scale;
  var evidence={recipe_id:recipe.id,list_id:list.id,recipe_total:r,before:policy.initial!==undefined?null:njson('quantity_before'),scale:policy.scale,expected:expected,observed:q,expected_association:expectedAssociation,observed_association:association};
  bp.log.info('NATIVE_QUANTITY_OBSERVATION '+JSON.stringify(evidence));
  if(!nnear(q,expected)||!nnear(association,expectedAssociation))nfail('F01_QUANTITY_CANDIDATE',evidence);
  nput('quantity_before',{list:q,association:association,recipe:r});pvg.success('QUANTITY_AND_ASSOCIATION_READBACK_PASS');
}
function nativeStep(key){var step=MODEL.steps[key];nativeRequest(step.operation,step.body,function(response){var b=nreceipt(key,response);ncapture(MODEL.steps[key],b);pvg.success('ACTION_RESPONSE_CAPTURED:'+key);});}
function nativeVerify(key){var checks=MODEL.steps[key].verify;checks.forEach(function(check){nativeRequest(check.operation,undefined,function(response){var b=nreceipt(key+':readback:'+check.operation,response);ncapture(check,b);ncheck(check,b);pvg.success('INDEPENDENT_READBACK_PASS:'+key);});});}
