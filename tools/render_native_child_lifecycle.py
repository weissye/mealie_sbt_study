"""Generic bounded lifecycle extension: delete one child and retain its sibling."""
import json
from render_native_interleaved_dependencies import render as render_base,identity,marker,response_schema,concrete

def render(plan,base_url,namespace,parent_key,child_key):
    interfaces,stories,manifest=render_base(plan,base_url,namespace,parent_key,child_key)
    entities={e.entity.key:e for e in plan.entities};parent,child=entities[parent_key],entities[child_key]
    deletes=[op for op in child.ops if op.kind=='delete' and op.op.method=='DELETE']
    if len(deletes)!=1:raise ValueError('Exactly one child DELETE required')
    delete=deletes[0];edge=next(e for e in child.dependencies if e.target==parent_key)
    arrays=[]
    for field,s in response_schema(parent.get_op).get('properties',{}).items():
        try:s=concrete(s)
        except ValueError:continue
        props=concrete(s.get('items',{})).get('properties',{})
        if s.get('type')=='array' and all(f in props for f in (identity(child),marker(child),edge.field_name)):arrays.append(field)
    if len(arrays)!=1:raise ValueError('Parent membership collection ambiguous')
    q=json.dumps;deleted='dep_child1_id';bound='dep_child1_parent';cid=identity(child);pid=identity(parent)
    def emit(fn,method,path,codes,callback):
        options={'headers':{'Authorization':'Bearer @{mealie_acceptance_token}'},'expectedResponseCodes':codes}
        receipt='bp.log.info("DEPENDENCY_RECEIPT "+JSON.stringify({operation:'+q(fn)+',body:response.body?JSON.parse(response.body):null}));'
        return 'function '+fn+'(){svc.'+method+'('+q(path)+','+q(options)[:-1]+',"callback":function(response){'+receipt+callback+'}});}\n'
    def path(op,variable,entity):return op.op.path.replace('{'+entity.key.fields[0]+'}','@{'+variable+'}')
    interfaces+=emit('depDeletechild1','delete',path(delete,deleted,child),delete.success_codes,'pvg.success("Child DELETE response accepted");')
    # Explicit generic negative-read policy, not a declared GET response inferred from OpenAPI.
    interfaces+=emit('depVerifyDeletedchild1','get',path(child.get_op,deleted,child),[404],'pvg.success("DELETED_CHILD_ABSENT");')
    check='var obj=JSON.parse(response.body),items=obj['+q(arrays[0])+'];if(obj['+q(pid)+']!==pvg.rtv.get('+q(bound)+')||!Array.isArray(items)||items.some(function(x){return x['+q(cid)+']===pvg.rtv.get('+q(deleted)+');})||items.filter(function(x){return x['+q(cid)+']===pvg.rtv.get("dep_child2_id");}).length!==1){pvg.fail("Deletion parent or sibling membership mismatch");return;}pvg.success("DELETE_PARENT_AND_SIBLING_MEMBERSHIP_PASS");'
    parent_fields=[]
    for f,shape in response_schema(parent.get_op).get('properties',{}).items():
        try:shape=concrete(shape)
        except ValueError:continue
        if shape.get('type') in ('string','integer','number','boolean') and shape.get('format') not in ('date','date-time'):parent_fields.append(f)
    prefix='var candidates=[JSON.parse(pvg.rtv.get("dep_parent1_snapshot")),JSON.parse(pvg.rtv.get("dep_parent2_snapshot"))],prior=candidates.filter(function(x){return x['+q(pid)+']===pvg.rtv.get('+q(bound)+');})[0];'
    check=check.replace('pvg.success("DELETE_PARENT_AND_SIBLING_MEMBERSHIP_PASS");',prefix+'if(!prior||'+q(parent_fields)+'.some(function(k){return obj[k]!==prior[k];})){pvg.fail("Retained parent scalar state changed after child deletion");return;}pvg.success("DELETE_PARENT_AND_SIBLING_MEMBERSHIP_PASS");')
    interfaces+=emit('depVerifyDeletionParent','get',path(parent.get_op,bound,parent),parent.get_op.success_codes,check)
    tail='''sync({waitFor:EventSet("deletion-enabled",function(e){return e.name==="SBT:DeletionEnabled";})});
    sync({request:Event("SBT:MutationBegin",{owner:"child:1",stage:"delete"})});
    depDeletechild1();sync({request:Event("SBT:CrudStep",{owner:"child:1",stage:"delete"})});
    sync({waitFor:EventSet("deleted-verified",function(e){return e.name==="SBT:CrudVerified"&&e.data.owner==="child:1"&&e.data.stage==="delete";})});
    sync({request:Event("SBT:MutationEnd",{owner:"child:1",stage:"delete"})});
    sync({request:Event("SBT:LifecycleDeleted",{owner:"child:1"})});'''
    lines=stories.splitlines();changed=0
    for i,line in enumerate(lines):
        if line.startswith('bthread("crud:child:1"'):
            assert line.endswith('});');lines[i]=line[:-3]+tail+'});';changed+=1
    if changed!=1:raise ValueError('Lifecycle extension anchor missing')
    lines.append('bthread("deletion:ready",function(){var seen={};while(Object.keys(seen).length<2){var e=sync({waitFor:EventSet("final-readbacks",function(e){return e.name==="SBT:FinalVerified";})});seen[e.data.owner]=true;}sync({request:Event("SBT:DeletionEnabled")});});')
    lines.append('bthread("verify:child:1:delete",function(){sync({waitFor:EventSet("delete-step",function(e){return e.name==="SBT:CrudStep"&&e.data.owner==="child:1"&&e.data.stage==="delete";})});depVerifyDeletedchild1();depVerifyDeletionParent();depVerifychild2update();sync({request:Event("SBT:CrudVerified",{owner:"child:1",stage:"delete"})});});')
    manifest.update(delete_tested=True,full_crud=False,complete_child_lifecycles=1,retained_child_lifecycles=1,negative_read_policy='GET must return 404 after successful DELETE; explicit generic acceptance convention',deletion_scope='Only child:1 created by this schedule; parents and child:2 retained',deletion_barrier='After all create/update workers and both final readbacks; prevents later parent snapshots resurrecting deleted children')
    return interfaces,'\n'.join(lines)+'\n',manifest
