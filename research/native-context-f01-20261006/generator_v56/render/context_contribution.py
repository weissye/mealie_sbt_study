"""Schema-matched contribution experiment; explicit generic algebraic hypothesis.
No SUT-name checks, no expected quantity constants, no observed-state learning.
The action is selected from contract structure and summary, with ambiguity rejected.
"""
import json,re
from .context_model import canonical,pointer,j

def unique(values,label):
    if len(values)!=1:raise ValueError('Contribution requires unambiguous '+label)
    return values[0]

def infer_contribution(c,entities):
    recipe=unique([e for e in entities if e['nested']], 'embedded source resource')
    nested=unique(recipe['nested'],'embedded source array')
    quantity=unique([f for f,s in nested['schema']['properties'].items() if f.lower()=='quantity' and c.resolve(s).get('type') in ('number','integer')],'ingredient quantity convention')
    actions=[]
    for path,ops in c.raw['paths'].items():
        op=ops.get('post',{})
        if not op or op.get('deprecated') or not re.search(r'\badd\b',op.get('summary',''),re.I):continue
        body=c.body(op)
        if body.get('type')!='array':continue
        props=c.resolve(body.get('items',{})).get('properties',{})
        foreign=[f for f,s in props.items() if canonical(f.removesuffix('Id'))==canonical(recipe['name']) and f.endswith('Id')]
        increments=[f for f,s in props.items() if 'increment' in f.lower() and c.resolve(s).get('type') in ('number','integer')]
        lists=[e for e in entities if path.startswith(e['detail']+'/')]
        if len(foreign)==len(increments)==len(lists)==1:
            actions.append((path,op,props,foreign[0],increments[0],lists[0]))
    path,op,props,foreign,increment,container=unique(actions,'non-deprecated array contribution POST')
    codes,response=c.response(op)
    if canonical(response.get('title',''))!=canonical(container['name']):raise ValueError('Contribution response is not container')
    items=[]
    for f,s in response['properties'].items():
        if c.resolve(s).get('type')=='array':
            shape=c.resolve(c.resolve(s)['items'])
            for entity in entities:
                if canonical(shape.get('title',''))==canonical(entity['name']):items.append((f,entity))
    item_field,item=unique(items,'response item array')
    item_props=item['read_schema']['properties']
    item_refs=unique([(f,c.resolve(c.resolve(s)['items'])) for f,s in item_props.items() if c.resolve(s).get('type')=='array' and foreign in c.resolve(c.resolve(s)['items']).get('properties',{})],'item reference array')
    list_refs=unique([(f,c.resolve(c.resolve(s)['items'])) for f,s in response['properties'].items() if c.resolve(s).get('type')=='array' and foreign in c.resolve(c.resolve(s)['items']).get('properties',{})],'container reference array')
    rq=unique([f for f,s in item_refs[1]['properties'].items() if f.lower().endswith('quantity') and c.resolve(s).get('type') in ('number','integer')],'reference quantity convention')
    scale_key=unique([f for f,s in item_refs[1]['properties'].items() if f.lower().endswith('scale') and c.resolve(s).get('type') in ('number','integer')],'reference scale convention')
    if rq not in list_refs[1]['properties']:raise ValueError('Reference quantity schemas disagree')
    link_fields=[]
    for link in nested['links']:
        f=link['field']+'Id'
        if f not in item_props:raise ValueError('Missing item foreign key for '+link['field'])
        link_fields.append({'source':link['field'],'item':f})
    child_key=unique([f for f in item_refs[1]['properties'] if f.endswith('Id') and canonical(f[:-2])==canonical(item['name'])], 'reference child identity key')
    owner=unique([d['field'] for d in item['dependencies'] if d['target']==container['name'] and not d.get('array')],'item container key')
    # Optional nested objects are not added to the contribution body: use the stored recipe.
    required=c.resolve(c.body(op)['items']).get('required',[])
    if any(f!=foreign for f in required):raise ValueError('Unsupported required contribution parameter')
    for scale in (1,0.5):
        schema=c.resolve(props[increment])
        if scale<schema.get('minimum',float('-inf')) or scale>schema.get('maximum',float('inf')):raise ValueError('Contribution scale outside schema')
    return dict(operation_path=path,codes=codes,recipe_type=recipe['name'],list_type=container['name'],item_type=item['name'],
        ingredients_field=nested['field'],quantity_field=quantity,recipe_key=foreign,increment_field=increment,
        item_array=item_field,item_refs=item_refs[0],list_refs=list_refs[0],reference_quantity=rq,reference_scale=scale_key,owner_key=owner,child_key=child_key,
        keys=link_fields,recipe_detail=recipe['detail'],recipe_parameter=recipe['parameter'],
        list_detail=container['detail'],list_parameter=container['parameter'],item_detail=item['detail'],item_parameter=item['parameter'],
        sources=[pointer(path,'post'),nested['pointer'],pointer(item['detail'],'get'),pointer(container['detail'],'get')],
        inference='summary Add; array input; source Id; numeric Increment; unique container response; schema-linked item and references',
        hypothesis='shared dependency keys merge into one item; quantities add sum(source quantities)*increment; container reference quantity tracks sum(increments); item reference quantity times scale equals the DAL item quantity. This is a falsifiable generic hypothesis, not a guarantee encoded by OpenAPI.',
        scales=[1,0.5],fixture_quantities=[2,4])

DAL=r'''
// Opt-in contribution ledger. Expected state changes ONLY from selected model actions.
var contributionPlan=PLAN;
function contributionExpected(recipe, list, previous, scale) {
    var rows=recipe.expected[contributionPlan.ingredients_field];
    if(!rows || rows.length!==2) throw new Error("Contribution requires two linked ingredients");
    var amount=0, keys={};
    rows.forEach(function(row,index){
        var q=row[contributionPlan.quantity_field];
        if(typeof q!=="number" || !isFinite(q)) throw new Error("Non-numeric source quantity");
        amount+=q*scale;
        contributionPlan.keys.forEach(function(k){
            var id=row[k.source] && row[k.source].id;
            if(!id) throw new Error("Unbound source dependency");
            if(index && keys[k.item]!==id) throw new Error("Sources do not share dependency keys");
            keys[k.item]=id;
        });
    });
    return {quantity:(previous ? previous.quantity : 0)+amount,
        referenceQuantity:(previous ? previous.referenceQuantity : 0)+scale,keys:keys,
        recipeId:"@{ID_"+recipe.id+"}",listId:"@{ID_"+list.id+"}",recipeExpected:cloneExpected(recipe.expected)};
}
function applyContributionEffect(data) {
    var old=ctx.runQuery("Contribution.All");
    if(old.length) ctx.removeEntity(old[0].id);
    ctx.insertEntity(ctx.Entity("contribution_1","contribution",{
        stage:data.stage,expected:cloneExpected(data.expected),verified:false,
        recipe:data.recipe,list:data.list
    }));
}
ctx.registerQuery("Contribution.All",function(e){return e.type==="contribution";});
ctx.registerQuery("Contribution.Pending",function(e){return e.type==="contribution" && !e.verified;});
ctx.registerEffect("ContributionVerified",function(data){
    var e=ctx.runQuery("Contribution.All")[0];
    if(!e || e.stage!==data.stage) throw new Error("Stale contribution acknowledgement");
    ctx.removeEntity(e.id);
    ctx.insertEntity(ctx.Entity(e.id,"contribution",{stage:e.stage,expected:e.expected,verified:true,recipe:e.recipe,list:e.list}));
});
'''
INTERFACES=r'''
// Contribution operation and all observation HTTP stay in this shared interface.
var contributionWirePlan=PLAN;
function contributionCallback(expected, kind, finish) {
    var code="var plan="+JSON.stringify(contributionWirePlan)+";var expected="+JSON.stringify(expected)+";var kind="+JSON.stringify(kind)+";var finish="+finish+";";
    code+="("+validateContributionResponse.toString()+")(response,plan,expected,kind,finish);";
    return callbackFromSource(code);
}
function contributeSourceToList(recipe,list,scale,stage) {
    var previous=ctx.runQuery("Contribution.All");
    var expected=contributionExpected(recipe,list,previous.length ? previous[0].expected : null,scale);
    var body={};body[contributionWirePlan.recipe_key]=expected.recipeId;body[contributionWirePlan.increment_field]=scale;
    return requestRest("POST",contributionWirePlan.operation_path.replace("{"+contributionWirePlan.list_parameter+"}",expected.listId),[body],contributionWirePlan.codes,
        {action:"contribute",stage:stage,recipe:recipe.id,list:list.id,expected:expected,affected:[list.id]},
        contributionCallback(expected,"operation",false));
}
function readContributionItem(state) {
    // One RTV expression chooses bound item ID, or a read-only absent sentinel if discovery failed.
    var route=contributionWirePlan.item_detail.replace("{"+contributionWirePlan.item_parameter+"}","@{F01_ITEM_ID}");
    return requestRest("GET",route,undefined,[200,404],{action:"observeContributionItem"},contributionCallback(state.expected,"item",false));
}
function readContributionList(state,finish) {
    var route=contributionWirePlan.list_detail.replace("{"+contributionWirePlan.list_parameter+"}",state.expected.listId);
    return requestRest("GET",route,undefined,[200],{action:"observeContributionList"},contributionCallback(state.expected,"list",!!finish));
}
function readContributionRecipe(state) {
    var route=contributionWirePlan.recipe_detail.replace("{"+contributionWirePlan.recipe_parameter+"}","@{ROUTE_"+state.recipe+"}");
    return requestRest("GET",route,undefined,[200],{action:"observeContributionRecipe"},contributionCallback(state.expected,"recipe",false));
}
'''
VALIDATOR=r'''
function resolve(v){if(typeof v==='string' && /^@\{[A-Za-z0-9_]+\}$/.test(v))return pvg.rtv.get(v.slice(2,-1));if(Array.isArray(v))return v.map(resolve);if(v && typeof v==='object'){var out={};Object.keys(v).forEach(function(k){out[k]=resolve(v[k]);});return out;}return v;}
expected=resolve(expected);
if(kind==='operation' && expected.referenceQuantity===1){pvg.rtv.set('F01_REVIEW',JSON.stringify({issues:[],receipts:[],stages:0}));pvg.rtv.set('F01_ITEM_ID','');pvg.rtv.set('F01_REF_item','');pvg.rtv.set('F01_REF_list','');}
function bound(key){return String(pvg.rtv.get(key));}
var review=JSON.parse(String(pvg.rtv.get('F01_REVIEW')));
function problem(message){review.issues.push(kind+': '+message);}
function same(actual,wanted,path){if(Array.isArray(wanted)){if(!Array.isArray(actual)||actual.length!==wanted.length){problem(path+' length');return;}wanted.forEach(function(v,i){same(actual[i],v,path+'['+i+']');});}else if(wanted && typeof wanted==='object'){if(!actual){problem(path+' absent');return;}Object.keys(wanted).forEach(function(k){same(actual[k],wanted[k],path+'.'+k);});}else if(actual!==wanted)problem(path+' expected '+JSON.stringify(wanted)+' observed '+JSON.stringify(actual));}
var observed;
try {observed=JSON.parse(response.body);}catch(e){problem('Non-JSON response');observed={};}
var receipt={kind:kind,expected:expected,response:observed};review.receipts.push(receipt);
bp.log.info('F01_RECEIPT '+JSON.stringify(receipt));
function reference(rows,label){
    var matches=(rows || []).filter(function(r){return r[plan.recipe_key]===expected.recipeId;});
    if(matches.length!==1){problem(label+' requires exactly one source reference');return;}
    if(label==='list'){same(matches[0][plan.reference_quantity],expected.referenceQuantity,label+'.quantity');}
    else{var quantity=matches[0][plan.reference_quantity],scale=matches[0][plan.reference_scale];
        if(typeof quantity!=='number' || typeof scale!=='number' || !isFinite(quantity*scale))problem('Non-numeric item reference quantity/scale');
        else same(quantity*scale,expected.quantity,'item.referenceQuantityTimesScale');}
    if(!matches[0].id)problem(label+' reference identity absent');
    var refKey='F01_REF_'+label,known=bound(refKey);
    if(known && matches[0].id!==known)problem(label+' reference identity changed');
    if(!known)pvg.rtv.set(refKey,matches[0].id);
    if(label==='item')same(matches[0][plan.child_key],bound('F01_ITEM_ID'),label+'.child');
}
function item(actual){
    if(!actual){problem('Item absent');return;}
    same(actual.id,bound('F01_ITEM_ID'),'item.id');
    same(actual[plan.quantity_field],expected.quantity,'item.quantity');
    same(actual[plan.owner_key],expected.listId,'item.owner');
    Object.keys(expected.keys).forEach(function(k){same(actual[k],expected.keys[k],'item.'+k);});
    reference(actual[plan.item_refs],'item');
}
if(kind==='operation' || kind==='list'){
    same(observed.id,expected.listId,'list.id');
    var items=observed[plan.item_array] || [];
    if(items.length!==1)problem('Expected one merged item, observed '+items.length);
    if(kind==='operation' && items.length===1 && !bound('F01_ITEM_ID'))pvg.rtv.set('F01_ITEM_ID',items[0].id);
    if(!bound('F01_ITEM_ID'))pvg.rtv.set('F01_ITEM_ID','00000000-0000-4000-8000-000000000000');
    if(items.length===1)item(items[0]);
    reference(observed[plan.list_refs],'list');
}else if(kind==='item'){item(observed);
}else if(kind==='recipe'){same(observed.id,expected.recipeId,'recipe.id');same(observed,expected.recipeExpected,'recipe');}
if(finish){review.stages++;review.status=review.issues.length ? 'F01_SEMANTIC_CANDIDATE' : 'F01_STAGE_PASS';bp.log.info('F01_EVIDENCE '+JSON.stringify(review));}
pvg.rtv.set('F01_REVIEW',JSON.stringify(review));
if(finish && review.issues.length)pvg.fail('F01 semantic discrepancy; all post-write observation requests completed. Review F01_EVIDENCE.');
'''
STORIES=r'''
// Separate process: waits for the final linked source and final container revisions.
bthread("whole then partial source contribution",function(){
    waitForDependencies([RECIPE_TYPE,LIST_TYPE]);
    var recipe=waitForResource(RECIPE_ID,3);
    var list=waitForResource(LIST_ID,2);
    var scales=[1,0.5];
    for(var index=0;index<scales.length;index++){
        var scale=scales[index];
        contributeSourceToList(recipe,list,scale,index+1);
        waitFor(bp.EventSet("Contribution readbacks "+(index+1),function(e){return e.name==="ContributionVerified" && e.data.stage===index+1;}));
    }
    request(bp.Event("F01Completed"));
});
// Separate child/relationship verifier process, activated by the Context ledger.
ctx.bthread("verify contribution response and linked state", "Contribution.Pending",function(state){
    readContributionItem(state);
    readContributionList(state,false);
    readContributionRecipe(state);
    readContributionList(state,true);
    request(bp.Event("ContributionVerified",{stage:state.stage}));
});
'''

def render_contribution(plan):
    interface=INTERFACES.replace('PLAN',j(plan))+'\nfunction validateContributionResponse(response,plan,expected,kind,finish) {\n'+VALIDATOR+'\n}\n'
    dal=DAL.replace('PLAN',j(plan))
    stories=STORIES.replace('RECIPE_TYPE',j(plan['recipe_type'])).replace('LIST_TYPE',j(plan['list_type'])).replace('RECIPE_ID',j(plan['recipe_type']+'_1')).replace('LIST_ID',j(plan['list_type']+'_1'))
    return interface,dal,stories
