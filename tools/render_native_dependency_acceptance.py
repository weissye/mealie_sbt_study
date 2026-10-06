"""Bounded contract-derived CRUD dependency renderer; no application field names."""
import json

def concrete(schema):
    choices=[s for s in schema.get('anyOf',[schema]) if s.get('type')!='null']
    if len(choices)!=1: raise ValueError('Ambiguous schema branch')
    return choices[0]

def response_schema(op):
    schemas=[s for r in op.op.success_responses for media,s in r.media_types.items() if media=='application/json']
    if len(schemas)!=1: raise ValueError('Ambiguous success response')
    return schemas[0]

def identity(entity):
    props=response_schema(entity.get_op).get('properties',{})
    if entity.key.response_field in props: return entity.key.response_field
    # Explicit generic convention, cross-validated against the GET schema.
    if 'id' in props and concrete(props['id']).get('type') in ('string','integer'): return 'id'
    raise ValueError('No schema-supported identity')

def marker(entity):
    from generator_v56.request_variants import select_request_variant
    props=select_request_variant(entity.create_op.op)[1].get('properties',{})
    update=next(o for o in entity.ops if o.kind=='update')
    candidates=[]
    for k,v in props.items():
        try:s=concrete(v)
        except ValueError:continue
        if k in update.body_props and s.get('type')=='string' and not s.get('format') and not v.get('readOnly'):candidates.append(k)
    if not candidates: raise ValueError('No writable string marker')
    return next((k for k in ('name','note','title','description') if k in candidates),sorted(candidates)[0])

def render(plan,base_url,namespace,parent_key,child_key):
    from generator_v56.request_variants import select_request_variant
    entities={e.entity.key:e for e in plan.entities}
    parent,child=entities[parent_key],entities[child_key]
    edges=[e for e in child.dependencies if e.target==parent_key]
    if len(edges)!=1 or len(child.dependencies)!=1 or parent.dependencies: raise ValueError('Acceptance requires one unambiguous dependency')
    edge=edges[0];q=json.dumps
    js=['//@provengo summon rest','//@provengo summon rtv','var svc=new RESTSession('+q(base_url)+',"provengo-client");']
    stories=['//@provengo summon rest','//@provengo summon rtv']
    manifest={'dependency':{'source':child_key,'target':parent_key,'field':edge.field_name,'provenance':[p.to_dict() for p in edge.provenance]},'workers':[],'instances_per_family':2,'delete_tested':False,'full_crud':False,'identity_policy':'Plan response field or schema-supported id convention'}
    def event_match(name,owner,stage=None):
        cond='e.name==='+q(name)+'&&e.data&&e.data.owner==='+q(owner)
        if stage:cond+='&&e.data.stage==='+q(stage)
        return 'EventSet('+q(owner+name+(stage or ''))+',function(e){return '+cond+';})'
    def request_event(name,data):return 'sync({request:Event('+q(name)+','+q(data)+')});'
    for role,entity in [('parent',parent),('child',child)]:
        if not entity.create_op or not entity.get_op or len(entity.key.fields)!=1: raise ValueError('Unsupported family')
        updates=[o for o in entity.ops if o.kind=='update' and o.op.method in ('PUT','PATCH')]
        if len(updates)!=1:raise ValueError('Update operation ambiguous')
        update=updates[0];idf=identity(entity);mf=marker(entity)
        create_schema=select_request_variant(entity.create_op.op)[1]
        for i in (1,2):
            owner=role+':'+str(i);stem=role+str(i);rv='dep_'+stem+'_id';snap='dep_'+stem+'_snapshot';bound='dep_'+stem+'_parent';value=namespace+'-'+stem
            manifest['workers'].append({'owner':owner,'role':role,'identity_field':idf,'marker_field':mf,'create':entity.create_op.op.path,'read':entity.get_op.op.path,'update':update.op.path})
            body={mf:value}
            for field in create_schema.get('required',[]):
                if field not in body and not(role=='child' and field==edge.field_name):raise ValueError('Unsupported required create field: '+field)
            if role=='child':body[edge.field_name]='@{'+bound+'}'
            def http(fn,op,path,payload,callback,parent_argument=False):
                options={'headers':{'Authorization':'Bearer @{mealie_acceptance_token}'},'expectedResponseCodes':op.success_codes}
                if payload is not None:options['headers']['Content-Type']='application/json';options['body']=payload
                receipt='bp.log.info("DEPENDENCY_RECEIPT "+JSON.stringify({operation:'+q(fn)+',body:JSON.parse(response.body)}));'
                raw=q(options)[:-1]+',"callback":function(response){'+receipt+callback+'}}'
                if parent_argument:raw=raw.replace('@{'+bound+'}','@{"+parentRV+"}')
                js.append('function '+fn+'('+('parentRV' if parent_argument else '')+'){svc.'+op.op.method.lower()+'('+q(path)+','+raw+');}')
            # Envelope capture is generic: recursively find one marker-correlated identity.
            capture='var root=JSON.parse(response.body),hits=[];function visit(v){if(!v||typeof v!=="object")return;if(!Array.isArray(v)&&v['+q(mf)+']==='+q(value)+'&&v['+q(idf)+']!==undefined)hits.push(v);Object.keys(v).forEach(function(k){visit(v[k]);});}visit(root);if(hits.length!==1){pvg.fail("Create envelope identity ambiguous");return;}pvg.rtv.set('+q(rv)+',hits[0]['+q(idf)+']);pvg.success("DEPENDENCY_CREATE_CAPTURED '+owner+'");'
            if role=='child':
                capture=capture.replace('pvg.success("DEPENDENCY_CREATE_CAPTURED '+owner+'");','')
                capture+='if(hits[0]['+q(edge.field_name)+']!==pvg.rtv.get(parentRV)){pvg.fail("Create parent binding mismatch");return;}pvg.rtv.set('+q(bound)+',pvg.rtv.get(parentRV));pvg.success("DEPENDENCY_CREATE_CAPTURED '+owner+'");'
            http('depCreate'+stem,entity.create_op,entity.create_op.op.path,q(body),capture,role=='child')
            read_path=entity.get_op.op.path.replace('{'+entity.key.fields[0]+'}','@{'+rv+'}')
            for stage,expected in [('create',value),('update',value+'-updated')]:
                callback='var obj=JSON.parse(response.body);if(obj['+q(idf)+']!==pvg.rtv.get('+q(rv)+')||obj['+q(mf)+']!=='+q(expected)+'){pvg.fail("CRUD readback mismatch '+owner+' '+stage+'");return;}'
                if role=='child':callback+='if(obj['+q(edge.field_name)+']!==pvg.rtv.get('+q(bound)+')){pvg.fail("Parent binding changed");return;}'
                callback+='pvg.rtv.set('+q(snap)+',JSON.stringify(obj));var body={};'+q(update.body_props)+'.forEach(function(k){if(obj[k]!==undefined)body[k]=obj[k];});body['+q(mf)+']='+q(value+'-updated')+';pvg.rtv.set('+q('dep_'+stem+'_updatebody')+',JSON.stringify(body));pvg.success("DEPENDENCY_READBACK_PASS '+owner+' '+stage+'");'
                http('depVerify'+stem+stage,entity.get_op,read_path,None,callback)
            # Preserve schema-declared writable state using the verified GET snapshot.
            updatebody='dep_'+stem+'_updatebody'
            http('depUpdate'+stem,update,update.op.path.replace('{'+entity.key.fields[0]+'}','@{'+rv+'}'),'@{'+updatebody+'}','pvg.success("Update response accepted");')
            workflow='sync({waitFor:EventSet("auth-'+stem+'",function(e){return e.name==="SBT:LiveAuthReady";})});'
            if role=='child':
                # Any verified ready parent can satisfy the dependency; no fixed parent instance.
                workflow+='var ready=sync({waitFor:EventSet("parent-'+stem+'",function(e){return e.name==="SBT:DependencyReady"&&e.data&&e.data.family==='+q(parent_key)+';})});'
            for stage,call in [('create','depCreate'+stem+'('+('ready.data.identity_variable' if role=='child' else '')+');'),('update','depUpdate'+stem+'();')]:
                workflow+=call+request_event('SBT:CrudStep',{'owner':owner,'stage':stage})+'sync({waitFor:'+event_match('SBT:CrudVerified',owner,stage)+'});'
                extra=''
                if role=='child' and stage=='update':
                    parent_arrays=[]
                    for f,s in response_schema(parent.get_op).get('properties',{}).items():
                        s=concrete(s)
                        if s.get('type')=='array':
                            props=concrete(s.get('items',{})).get('properties',{})
                            if idf in props and edge.field_name in props and mf in props:parent_arrays.append(f)
                    if len(parent_arrays)!=1:raise ValueError('Parent collection view ambiguous')
                    path=parent.get_op.op.path.replace('{'+parent.key.fields[0]+'}','@{'+bound+'}')
                    check='var obj=JSON.parse(response.body),items=obj['+q(parent_arrays[0])+'];if(obj['+q(identity(parent))+']!==pvg.rtv.get('+q(bound)+')||!Array.isArray(items)||items.filter(function(x){return x['+q(idf)+']===pvg.rtv.get('+q(rv)+');}).length!==1){pvg.fail("Parent membership readback mismatch");return;}pvg.success("PARENT_MEMBERSHIP_PASS '+owner+'");'
                    http('depMembership'+stem,parent.get_op,path,None,check)
                    extra='depMembership'+stem+'();'
                stories.append('bthread('+q('verify:'+owner+':'+stage)+',function(){sync({waitFor:'+event_match('SBT:CrudStep',owner,stage)+'});depVerify'+stem+stage+'();'+extra+request_event('SBT:CrudVerified',{'owner':owner,'stage':stage})+'});')
            if role=='parent':workflow+=request_event('SBT:DependencyReady',{'family':parent_key,'owner':owner,'identity_variable':rv})
            workflow+=request_event('SBT:WorkerFinished',{'owner':owner,'reason':'complete'})
            stories.append('bthread('+q('crud:'+owner)+',function(){'+workflow+'});')
    # One startup collector listens from the beginning; no readiness event is missed.
    for i in (1,2):
        needle='var ready=sync({waitFor:EventSet("parent-child'+str(i)+'"'
        stories=[s.replace(needle,request_event('SBT:ChildWaiting',{'owner':'child:'+str(i)})+needle) for s in stories]
        ready=request_event('SBT:DependencyReady',{'family':parent_key,'owner':'parent:'+str(i),'identity_variable':'dep_parent'+str(i)+'_id'})
        gate=request_event('SBT:ParentVerified',{'owner':'parent:'+str(i)})+'sync({waitFor:EventSet("startup-'+str(i)+'",function(e){return e.name==="SBT:DependenciesEnabled";})});'
        stories=[s.replace(ready,gate+ready) for s in stories]
    stories.append('bthread("dependency:startup",function(){var seen={};while(Object.keys(seen).length<4){var e=sync({waitFor:EventSet("startup-announcements",function(e){return e.name==="SBT:ChildWaiting"||e.name==="SBT:ParentVerified";})});seen[e.data.owner]=true;}sync({request:Event("SBT:DependenciesEnabled")});});')
    return '\n'.join(js)+'\n','\n'.join(stories)+'\n',manifest
