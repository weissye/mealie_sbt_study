"""Gitea-style bounded renderer over an existing generic generator Plan.

No system names, paths, entity properties or response codes are embedded here.
Supports one single-key family with a single writable string field. Other
shapes are rejected explicitly rather than guessed.
"""
import json

def render(plan, base_url, namespace):
    if len(plan.entities)!=1:
        raise ValueError('Acceptance renderer requires exactly one selected family')
    entity=plan.entities[0]
    create=entity.create_op
    read=entity.get_op
    updates=[op for op in entity.ops if op.kind=='update' and op.op.method in ('PUT','PATCH')]
    if not create or not read or len(updates)!=1 or len(entity.key.fields)!=1:
        raise ValueError('Unsupported CRUD family shape')
    update=updates[0]
    if len(create.body_props)!=1 or create.body_props!=update.body_props:
        raise ValueError('Acceptance requires one shared writable field')
    field=create.body_props[0]
    if create.body_prop_types.get(field)!='string':
        raise ValueError('Acceptance requires a writable string')
    identity=entity.key.response_field
    if not identity:
        raise ValueError('No contract-inferred response identity field')
    quote=json.dumps
    interfaces=['//@provengo summon rest','//@provengo summon rtv',
                'var svc=new RESTSession('+quote(base_url)+',"provengo-client");']
    stories=['//@provengo summon rest','//@provengo summon rtv']
    for instance in (1,2):
        owner='P1:'+entity.entity.key+':'+str(instance)
        rv='acceptance_id_'+str(instance)
        initial=namespace+'-'+str(instance)
        changed=initial+'-updated'
        item=read.op.path.replace('{'+entity.key.fields[0]+'}','@{'+rv+'}')
        updated_path=update.op.path.replace('{'+entity.key.fields[0]+'}','@{'+rv+'}')
        def function(name,method,path,statuses,body,callback):
            options={'headers':{'Authorization':'Bearer @{mealie_acceptance_token}'},'expectedResponseCodes':statuses}
            if body is not None:
                options['headers']['Content-Type']='application/json'
                options['body']=json.dumps(body)
            raw=json.dumps(options)[:-1]+',"callback":function(response){'+callback+'}}'
            interfaces.append('function '+name+'(){svc.'+method.lower()+'('+quote(path)+','+raw+');}')
        function('acceptanceCreate'+str(instance),create.op.method,create.op.path,create.success_codes,
                 {field:initial},'var obj=JSON.parse(response.body);var id=obj['+quote(identity)+'];'
                 'if(id===undefined||id===null||id===""){pvg.fail("Create identity unavailable");return;}'
                 'pvg.rtv.set('+quote(rv)+',id);pvg.success("Create identity captured");')
        for stage,value in [('Create',initial),('Update',changed)]:
            function('acceptanceVerify'+stage+str(instance),read.op.method,item,read.success_codes,None,
                     'var obj=JSON.parse(response.body);'
                     'if(obj['+quote(identity)+']!==pvg.rtv.get('+quote(rv)+')||obj['+quote(field)+']!=='+quote(value)+')'
                     '{pvg.fail("Independent readback mismatch");return;}'
                     'pvg.success('+quote('ACCEPTANCE_READBACK_PASS '+owner+' '+stage)+');')
        function('acceptanceUpdate'+str(instance),update.op.method,updated_path,update.success_codes,{field:changed},
                 'pvg.success("Update response accepted");')
        matcher=lambda stage:'EventSet('+quote(owner+stage)+',function(e){return e.name==="SBT:CrudVerified"&&e.data&&e.data.owner==='+quote(owner)+'&&e.data.stage==='+quote(stage)+';})'
        step=lambda stage:'sync({request:Event("SBT:CrudStep",{owner:'+quote(owner)+',stage:'+quote(stage)+'})});sync({waitFor:'+matcher(stage)+'});'
        stories.append('bthread('+quote('crud:'+owner)+',function(){'
                       'sync({waitFor:EventSet("auth-ready-'+str(instance)+'",function(e){return e.name==="SBT:LiveAuthReady";})});'
                       'acceptanceCreate'+str(instance)+'();'+step('create')+
                       'sync({request:Event("SBT:InstanceReady",{owner:'+quote(owner)+'})});'
                       'acceptanceUpdate'+str(instance)+'();'+step('update')+
                       'sync({request:Event("SBT:WorkerFinished",{owner:'+quote(owner)+',reason:"complete"})});});')
        for stage in ('create','update'):
            stories.append('bthread('+quote('verify:'+owner+':'+stage)+',function(){'
                           'sync({waitFor:EventSet('+quote(owner+'-'+stage)+' ,function(e){return e.name==="SBT:CrudStep"&&e.data&&e.data.owner==='+quote(owner)+'&&e.data.stage==='+quote(stage)+';})});'
                           'acceptanceVerify'+stage.capitalize()+str(instance)+'();'
                           'sync({request:Event("SBT:CrudVerified",{owner:'+quote(owner)+',stage:'+quote(stage)+'})});});')
    return '\n'.join(interfaces)+'\n','\n'.join(stories)+'\n'
