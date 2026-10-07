"""Native composition: distinct parent bindings and an explicit merge policy.
The merge arithmetic policy is supplied separately; it is not inferred from OpenAPI.
"""
import json
from render_native_multi_dependencies import render as multi_render
from render_native_interleaved_dependencies import identity, marker, response_schema, concrete


def render(plan, document, base_url, namespace, parent_key, child_key, target_keys, policy, scenario):
    interfaces, stories, manifest = multi_render(plan, document, base_url, namespace, parent_key, child_key, target_keys)
    q = json.dumps
    entities = {e.entity.key:e for e in plan.entities}
    parent, child = entities[parent_key], entities[child_key]
    # Collect two verified parents without prescribing their creation order.
    lines = stories.splitlines()
    for n,line in enumerate(lines):
        if line.startswith('bthread("dependency:multi-ready"'):
            lines[n] = 'bthread("dependency:multi-ready",function(){var required='+q(target_keys)+',seen={},parents=[];while(parents.length<2||required.some(function(k){return !seen[k];})){var e=sync({waitFor:EventSet("distinct-ready",function(e){return e.name==="SBT:DependencyReady";})});if(e.data.family==='+q(parent_key)+'){if(!parents.some(function(p){return p.owner===e.data.owner;}))parents.push(e.data);}else if(required.indexOf(e.data.family)>=0&&!seen[e.data.family])seen[e.data.family]=e.data;}sync({request:Event("SBT:MultiPrereqsReady",{bindings:seen,parents:parents})});});'
        if line.startswith('bthread("dependency:linked-prefix"'):
            required = ['parent:1','parent:2']+[x['owner'] for x in manifest['optional_schema_dependencies']]
            lines[n] = 'bthread("dependency:linked-prefix",function(){var required='+q(required)+',linked=false,updates={};while(required.some(function(k){return !updates[k];})){var e=sync({waitFor:EventSet("distinct-prefix-observe",function(e){return e.name==="SBT:CrudVerified";}),block:EventSet("distinct-prefix-boundary",function(e){if(e.name!=="SBT:MutationBegin")return false;return !linked&&required.indexOf(e.data.owner)>=0||linked&&e.data.owner.indexOf("child:")===0&&e.data.stage==="create";})});if(e.data.owner.indexOf("child:")===0&&e.data.stage==="create")linked=true;if(e.data.stage==="update")updates[e.data.owner]=true;}});'
    stories = '\n'.join(lines)
    for i in (1,2):
        old='var ready={data:multi.data.bindings['+q(parent_key)+']};'
        # Each child binds a different ready parent, independent of parent creation order.
        start='bthread("crud:child:'+str(i)+'"'
        lines=stories.splitlines()
        for n,line in enumerate(lines):
            if line.startswith(start):
                if old not in line:raise ValueError('Distinct readiness anchor missing')
                lines[n]=line.replace(old,'var ready={data:multi.data.parents['+str(i-1)+']};')
        stories='\n'.join(lines)
    manifest.update(scenario=scenario,parent_binding_policy='Two distinct independently verified ready parents, assigned by readiness order; optional food/unit bindings shared',merge_policy=policy if scenario=='merge' else None)
    if scenario=='distinct':return interfaces,stories+'\n',manifest
    if scenario!='merge':raise ValueError('Unknown scenario')
    idf,mf=identity(child),marker(child)
    edge=manifest['dependency']['field']
    quantity=policy['quantity_field']; add=policy['added_quantity']; env=policy['response_envelope']
    if policy['quantity_rule']!='sum' or policy['identity_rule']!='retain_existing':raise ValueError('Unsupported explicit merge policy')
    from generator_v56.request_variants import select_request_variant
    props=select_request_variant(child.create_op.op)[1]['properties']
    if quantity not in props or concrete(props[quantity]).get('type') not in ('integer','number'):raise ValueError('Quantity policy is not supported by create schema')
    schema=response_schema(child.create_op)['properties']
    if any(v not in schema for v in env.values()):raise ValueError('Merge envelope policy differs from contract')
    collections=[]
    for field,shape in response_schema(parent.get_op)['properties'].items():
        shape=concrete(shape)
        if shape.get('type')=='array' and idf in concrete(shape.get('items',{})).get('properties',{}) and edge in concrete(shape.get('items',{})).get('properties',{}) and mf in concrete(shape.get('items',{})).get('properties',{}):collections.append(field)
    if len(collections)!=1:raise ValueError('Parent collection ambiguous')
    cf=collections[0]
    def emit(fn,op,path,body,callback):
        options={'headers':{'Authorization':'Bearer @{mealie_acceptance_token}'},'expectedResponseCodes':op.success_codes}
        if body is not None:options['headers']['Content-Type']='application/json';options['body']=body
        receipt='bp.log.info("DEPENDENCY_RECEIPT "+JSON.stringify({operation:'+q(fn)+',body:JSON.parse(response.body)}));'
        return 'function '+fn+'(){svc.'+op.op.method.lower()+'('+q(path)+','+q(options)[:-1]+',"callback":function(response){'+receipt+callback+'}});}'
    # Final snapshots are protected by waiting for both final verifiers, not just worker completion.
    body={mf:namespace+'-merge-contribution',edge:'@{dep_child1_parent}',quantity:add}
    fields=[edge]+[x['field'] for x in manifest['optional_schema_dependencies']]
    for link in manifest['optional_schema_dependencies']:body[link['field']]='@{dep_child1_'+link['field']+'}'
    callback='var envelope=JSON.parse(response.body),before=JSON.parse(pvg.rtv.get("dep_child1_snapshot"));if(!Array.isArray(envelope['+q(env['created'])+'])||!Array.isArray(envelope['+q(env['updated'])+'])||!Array.isArray(envelope['+q(env['deleted'])+'])||envelope['+q(env['created'])+'].length!==0||envelope['+q(env['deleted'])+'].length!==0||envelope['+q(env['updated'])+'].length!==1){pvg.fail("MERGE_ENVELOPE_MISMATCH");return;}var obj=envelope['+q(env['updated'])+'][0];var expected=before['+q(quantity)+']+'+q(add)+';var note=before['+q(mf)+']+'+q(policy['note_separator']+namespace+'-merge-contribution')+';if(obj['+q(idf)+']!==before['+q(idf)+']||obj['+q(quantity)+']!==expected||obj['+q(mf)+']!==note||'+q(fields)+'.some(function(k){return obj[k]!==before[k];})){pvg.fail("MERGE_RESPONSE_STATE_MISMATCH");return;}pvg.rtv.set("dep_merge_expected",JSON.stringify({id:before['+q(idf)+'],quantity:expected,note:note,bindings:before}));pvg.success("MERGE_RESPONSE_PASS");'
    interfaces+='\n'+emit('depMergeAdd',child.create_op,child.create_op.op.path,q(body),callback)
    path=child.get_op.op.path.replace('{'+child.key.fields[0]+'}','@{dep_child1_id}')
    check='var obj=JSON.parse(response.body),expected=JSON.parse(pvg.rtv.get("dep_merge_expected"));if(obj['+q(idf)+']!==expected.id||obj['+q(quantity)+']!==expected.quantity||obj['+q(mf)+']!==expected.note||'+q(fields)+'.some(function(k){return obj[k]!==expected.bindings[k];})){pvg.fail("MERGE_PERSISTED_STATE_MISMATCH");return;}'
    for link in manifest['optional_schema_dependencies']:
        check+='if(!obj['+q(link['embedded_field'])+']||obj['+q(link['embedded_field'])+']['+q(link['identity_field'])+']!==obj['+q(link['field'])+']){pvg.fail("MERGE_EMBEDDED_IDENTITY_MISMATCH");return;}'
    check+='pvg.rtv.set("dep_merge_persisted",JSON.stringify(obj));pvg.success("MERGE_PERSISTED_READBACK_PASS");'
    interfaces+='\n'+emit('depMergeReadback',child.get_op,path,None,check)
    path=parent.get_op.op.path.replace('{'+parent.key.fields[0]+'}','@{dep_child1_parent}')
    check='var obj=JSON.parse(response.body),expected=JSON.parse(pvg.rtv.get("dep_merge_expected")),items=obj['+q(cf)+'];if(obj['+q(identity(parent))+']!==expected.bindings['+q(edge)+']||!Array.isArray(items)||items.length!==1||items[0]['+q(idf)+']!==expected.id||items[0]['+q(quantity)+']!==expected.quantity||items[0]['+q(mf)+']!==expected.note||'+q(fields)+'.some(function(k){return items[0][k]!==expected.bindings[k];})){pvg.fail("MERGE_PARENT_VIEW_MISMATCH");return;}pvg.success("MERGE_PARENT_VIEW_PASS");'
    interfaces+='\n'+emit('depMergeParentReadback',parent.get_op,path,None,check)
    stories+='\nbthread("merge:contribution",function(){var seen={};while(Object.keys(seen).length<2){var e=sync({waitFor:EventSet("merge-finals",function(e){return e.name==="SBT:FinalVerified";})});seen[e.data.owner]=true;}sync({request:Event("SBT:MutationBegin",{owner:"merge:1",stage:"add"})});depMergeAdd();sync({request:Event("SBT:MergeStep")});sync({waitFor:EventSet("merge-verified",function(e){return e.name==="SBT:MergeVerified";})});sync({request:Event("SBT:MutationEnd",{owner:"merge:1",stage:"add"})});sync({request:Event("SBT:MergeFinished")});});'
    stories+='\nbthread("verify:merge:readback",function(){sync({waitFor:EventSet("merge-step",function(e){return e.name==="SBT:MergeStep";})});depMergeReadback();sync({request:Event("SBT:MergeReadVerified")});});'
    finals=''.join('depVerifyprereq'+str(i)+'update();' for i in range(len(target_keys)))
    stories+='\nbthread("verify:merge:views",function(){sync({waitFor:EventSet("merge-read-verified",function(e){return e.name==="SBT:MergeReadVerified";})});depMergeParentReadback();depVerifychild2update();depMembershipchild2();'+finals+'sync({request:Event("SBT:MergeVerified")});});'
    manifest['merge_checks']=['retained identity','quantity sum','explicit note policy','stable direct/embedded dependencies','independent item GET','parent collection GET','other list item unchanged','prerequisite GETs']
    return interfaces+'\n',stories+'\n',manifest
