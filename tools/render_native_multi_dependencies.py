"""Contract-derived prerequisite workers and multi-dependency lifecycle composition."""
import json
from render_native_interleaved_dependencies import render as base_render,identity,marker,response_schema,concrete
from infer_native_schema_links import infer_links

def render(plan,document,base_url,namespace,parent_key,child_key,target_keys):
    interfaces,stories,manifest=base_render(plan,base_url,namespace,parent_key,child_key)
    entities={e.entity.key:e for e in plan.entities};q=json.dumps;links=infer_links(document,plan,child_key,target_keys)
    manifest['optional_schema_dependencies']=links;manifest['additional_workers']=[]
    def emit(fn,op,path,body,callback):
        opts={'headers':{'Authorization':'Bearer @{mealie_acceptance_token}'},'expectedResponseCodes':op.success_codes}
        if body is not None:opts['headers']['Content-Type']='application/json';opts['body']=body
        receipt='bp.log.info("DEPENDENCY_RECEIPT "+JSON.stringify({operation:'+q(fn)+',body:JSON.parse(response.body)}));'
        return 'function '+fn+'(){svc.'+op.op.method.lower()+'('+q(path)+','+q(opts)[:-1]+',"callback":function(response){'+receipt+callback+'}});}'
    extra=[]
    for n,link in enumerate(links):
        e=entities[link['target']];owner='prereq:'+str(n);stem='prereq'+str(n);rv='dep_'+stem+'_id';mf=marker(e);idf=identity(e);value=namespace+'-'+stem
        updates=[op for op in e.ops if op.kind=='update' and op.op.method in ('PUT','PATCH')]
        if len(updates)!=1:raise ValueError('Prerequisite update ambiguous')
        op=updates[0]
        from generator_v56.request_variants import select_request_variant
        required=select_request_variant(e.create_op.op)[1].get('required',[])
        if any(field!=mf for field in required):raise ValueError('Unsupported prerequisite create requirement')
        link.update(identity_variable=rv,owner=owner,marker_field=mf,identity_field=idf)
        record={'owner':owner,'role':'prerequisite','family':e.entity.key,'identity_field':idf,'marker_field':mf};manifest['workers'].append(record)
        capture='var obj=JSON.parse(response.body);if(obj['+q(mf)+']!=='+q(value)+'||obj['+q(idf)+']===undefined){pvg.fail("Prerequisite create identity mismatch");return;}pvg.rtv.set('+q(rv)+',obj['+q(idf)+']);pvg.success("PREREQUISITE_CREATE_CAPTURED");'
        extra.append(emit('depCreate'+stem,e.create_op,e.create_op.op.path,q({mf:value}),capture))
        path=e.get_op.op.path.replace('{'+e.key.fields[0]+'}','@{'+rv+'}')
        for stage,expected in [('create',value),('update',value+'-updated')]:
            callback='var obj=JSON.parse(response.body);if(obj['+q(idf)+']!==pvg.rtv.get('+q(rv)+')||obj['+q(mf)+']!=='+q(expected)+'){pvg.fail("Prerequisite readback mismatch");return;}'
            numeric=[]
            for field,shape in response_schema(e.get_op).get('properties',{}).items():
                try:shape=concrete(shape)
                except ValueError:continue
                if field in op.body_props and shape.get('type') in ('boolean','integer','number'):numeric.append(field)
            if stage=='create':
                callback+='var scalar={};'+q(numeric)+'.forEach(function(k){scalar[k]=obj[k];});pvg.rtv.set('+q('dep_'+stem+'_scalar')+',JSON.stringify(scalar));'
            else:
                callback+='var scalar=JSON.parse(pvg.rtv.get('+q('dep_'+stem+'_scalar')+'));if(Object.keys(scalar).some(function(k){return scalar[k]!==obj[k];})){pvg.fail("Prerequisite scalar state changed");return;}'
            callback+='pvg.rtv.set('+q('dep_'+stem+'_snapshot')+',JSON.stringify(obj));var body={};'+q(op.body_props)+'.forEach(function(k){if(obj[k]!==undefined)body[k]=obj[k];});body['+q(mf)+']='+q(value+'-updated')+';pvg.rtv.set('+q('dep_'+stem+'_updatebody')+',JSON.stringify(body));pvg.success("PREREQUISITE_READBACK_PASS");'
            extra.append(emit('depVerify'+stem+stage,e.get_op,path,None,callback))
            stories+='\nbthread('+q('verify:'+owner+':'+stage)+',function(){sync({waitFor:EventSet('+q(stem+stage)+',function(e){return e.name==="SBT:CrudStep"&&e.data.owner==='+q(owner)+'&&e.data.stage==='+q(stage)+';})});depVerify'+stem+stage+'();sync({request:Event("SBT:CrudVerified",'+q({'owner':owner,'stage':stage})+')});});'
        write='bp.log.info("INTERLEAVED_WRITE_BODY "+JSON.stringify({operation:'+q('depUpdate'+stem)+',body:JSON.parse(pvg.rtv.get('+q('dep_'+stem+'_updatebody')+'))}));pvg.success("Prerequisite update accepted");'
        extra.append(emit('depUpdate'+stem,op,op.op.path.replace('{'+e.key.fields[0]+'}','@{'+rv+'}'),'@{dep_'+stem+'_updatebody}',write))
        work='sync({waitFor:EventSet('+q('auth-'+stem)+',function(e){return e.name==="SBT:LiveAuthReady";})});depCreate'+stem+'();sync({request:Event("SBT:CrudStep",'+q({'owner':owner,'stage':'create'})+')});sync({waitFor:EventSet('+q('created-'+stem)+',function(e){return e.name==="SBT:CrudVerified"&&e.data.owner==='+q(owner)+'&&e.data.stage==="create";})});sync({request:Event("SBT:DependencyReady",'+q({'family':e.entity.key,'owner':owner,'identity_variable':rv})+')});sync({request:Event("SBT:MutationBegin",'+q({'owner':owner,'stage':'update'})+')});depUpdate'+stem+'();sync({request:Event("SBT:CrudStep",'+q({'owner':owner,'stage':'update'})+')});sync({waitFor:EventSet('+q('updated-'+stem)+',function(e){return e.name==="SBT:CrudVerified"&&e.data.owner==='+q(owner)+'&&e.data.stage==="update";})});sync({request:Event("SBT:MutationEnd",'+q({'owner':owner,'stage':'update'})+')});sync({request:Event("SBT:WorkerFinished",'+q({'owner':owner,'reason':'complete'})+')});'
        stories+='\nbthread('+q('crud:'+owner)+',function(){'+work+'});'
    families=[parent_key]+[x['target'] for x in links]
    stories=stories.replace('while(Object.keys(seen).length<4){var e=sync({waitFor:EventSet("worker-completion"','while(Object.keys(seen).length<'+str(4+len(links))+'){var e=sync({waitFor:EventSet("worker-completion"')
    # Readiness collector starts with the model, avoiding missed early ready events.
    catalog='var required='+q(families)+',seen={};while(Object.keys(seen).length<required.length){var e=sync({waitFor:EventSet("multi-ready-input",function(e){return e.name==="SBT:DependencyReady"&&e.data&&required.indexOf(e.data.family)>=0;})});if(!seen[e.data.family])seen[e.data.family]=e.data;}sync({request:Event("SBT:MultiPrereqsReady",{bindings:seen})});'
    stories+='\nbthread("dependency:multi-ready",function(){'+catalog+'});'
    # Block only parent update reservations until one linked child is verified.
    # The gate listens from startup; it cannot miss an early readiness signal.
    required_updates=[link['owner'] for link in links]
    stories+='\nbthread("dependency:linked-prefix",function(){var required='+q(required_updates)+',parent=null,linked=false,updates={};while(!parent||!updates[parent]||required.some(function(owner){return !updates[owner];})){var e=sync({waitFor:EventSet("prefix-observations",function(e){return e.name==="SBT:DependencyReady"&&e.data.owner.indexOf("parent:")===0||e.name==="SBT:CrudVerified";}),block:EventSet("linked-prefix-boundary",function(e){if(e.name!=="SBT:MutationBegin")return false;return !linked&&(e.data.owner.indexOf("parent:")===0||required.indexOf(e.data.owner)>=0)||linked&&e.data.owner.indexOf("child:")===0&&e.data.stage==="create";})});if(e.name==="SBT:DependencyReady"&&!parent)parent=e.data.owner;if(e.name==="SBT:CrudVerified"&&e.data.owner.indexOf("child:")===0&&e.data.stage==="create")linked=true;if(e.name==="SBT:CrudVerified"&&e.data.stage==="update")updates[e.data.owner]=true;}});'

    lines=interfaces.splitlines()
    for i in (1,2):
        old='var ready=sync({waitFor:EventSet("parent-child'+str(i)+'",function(e){return e.name==="SBT:DependencyReady"&&e.data&&e.data.family==='+q(parent_key)+';})});'
        new='var multi=sync({waitFor:EventSet("multi-child'+str(i)+'",function(e){return e.name==="SBT:MultiPrereqsReady";})});var ready={data:multi.data.bindings['+q(parent_key)+']};'
        if old not in stories:raise ValueError('Child readiness anchor missing')
        stories=stories.replace(old,new)
        stories=stories.replace('depCreatechild'+str(i)+'(ready.data.identity_variable);','depCreatechild'+str(i)+'(ready.data.identity_variable,multi.data.bindings);')
        for j,line in enumerate(lines):
            if line.startswith('function depCreatechild'+str(i)+'('):
                line=line.replace('(parentRV)','(parentRV,bindings)',1)
                # Add schema-derived FK fields to the JSON body, with typed ready event variables.
                main_edge=entities[child_key].dependencies[0].field_name
                anchor='\\"'+main_edge+'\\":'
                for link in links:
                    prefix='\\"'+link['field']+'\\":\\"@{'+ '"+bindings['+q(link['target'])+'].identity_variable+"'+'}\\",'
                    line=line.replace(anchor,prefix+anchor)
                    check='if(hits[0]['+q(link['field'])+']!==pvg.rtv.get(bindings['+q(link['target'])+'].identity_variable)){pvg.fail("Create optional binding mismatch");return;}pvg.rtv.set('+q('dep_child'+str(i)+'_'+link['field'])+',pvg.rtv.get(bindings['+q(link['target'])+'].identity_variable));'
                    line=line.replace('pvg.success("DEPENDENCY_CREATE_CAPTURED child:'+str(i)+'");',check+'pvg.success("DEPENDENCY_CREATE_CAPTURED child:'+str(i)+'");')
                lines[j]=line
            elif line.startswith('function depVerifychild'+str(i)):
                for link in links:
                    check='if(obj['+q(link['field'])+']!==pvg.rtv.get('+q('dep_child'+str(i)+'_'+link['field'])+')||(obj['+q(link['embedded_field'])+']&&obj['+q(link['embedded_field'])+']['+q(link['identity_field'])+']!==obj['+q(link['field'])+'])){pvg.fail("Optional dependency readback mismatch");return;}'
                    line=line.replace('pvg.rtv.set("dep_child'+str(i)+'_snapshot"',check+'pvg.rtv.set("dep_child'+str(i)+'_snapshot"')
                lines[j]=line
        # Fresh child snapshot within the reserved update action; retain original scalar baseline.
        original=next(line for line in lines if line.startswith('function depVerifychild'+str(i)+'update('))
        refresh=original.replace('depVerifychild'+str(i)+'update','depVerifychild'+str(i)+'refresh').replace(q(namespace+'-child'+str(i)+'-updated'),q(namespace+'-child'+str(i)),1)
        lines.append(refresh)
        stories=stories.replace('depUpdatechild'+str(i)+'();','depVerifychild'+str(i)+'refresh();depUpdatechild'+str(i)+'();')
    import re
    for j,line in enumerate(lines):
        if line.startswith('function depVerifyparent') and 'update()' in line:
            pattern=r'(\[[^\[\]]*\])\.some\(function\(k\)\{return x\[k\]!==undefined'
            def add_fields(match):
                fields=json.loads(match.group(1))+[link['field'] for link in links]
                return q(list(dict.fromkeys(fields)))+'.some(function(k){return x[k]!==undefined'
            lines[j],changed=re.subn(pattern,add_fields,line)
            if changed!=1:raise ValueError('Parent collection verifier anchor ambiguous')
    # Observe existing linked children after each optional prerequisite update.
    # Symbolic events decide which children exist; IDs and baselines are read only in REST callbacks.
    for i in (1,2):
        original=next(line for line in lines if line.startswith('function depVerifychild'+str(i)+'update('))
        current='JSON.parse(pvg.rtv.get('+q('dep_child'+str(i)+'_snapshot')+'))['+q(marker(entities[child_key]))+']'
        observe=original.replace('depVerifychild'+str(i)+'update','depObservechild'+str(i)).replace(q(namespace+'-child'+str(i)+'-updated'),current,1)
        lines.append(observe)
    story_lines=stories.splitlines()
    for n,link in enumerate(links):
        prefix='bthread('+q('verify:'+link['owner']+':update')
        for index,line in enumerate(story_lines):
            if not line.startswith(prefix):continue
            replacement='var seen={};while(true){var event=sync({waitFor:EventSet('+q('prereq-update-observer-'+str(n))+',function(e){return e.name==="SBT:CrudVerified"&&e.data.owner.indexOf("child:")===0||e.name==="SBT:CrudStep"&&e.data.owner==='+q(link['owner'])+'&&e.data.stage==="update";})});if(event.name==="SBT:CrudVerified"){seen[event.data.owner]=true;continue;}break;}depVerifyprereq'+str(n)+'update();if(seen["child:1"])depObservechild1();if(seen["child:2"])depObservechild2();sync({request:Event("SBT:CrudVerified",'+q({'owner':link['owner'],'stage':'update'})+')});'
            story_lines[index]=prefix+',function(){'+replacement+'});'
    stories='\n'.join(story_lines)
    # Read both prerequisite resources after all updates, through existing interfaces/verifiers.
    finals=''.join('depVerifyprereq'+str(i)+'update();' for i in range(len(links)))
    stories=stories.replace('depMembershipchild1();sync({request:Event("SBT:FinalVerified"', 'depMembershipchild1();'+finals+'sync({request:Event("SBT:FinalVerified"')
    manifest.update(full_crud=False,delete_tested=False,readiness_policy='First independently verified ready resource in each selected family; collect all families without fixed readiness order',known_inference_gap='Installed plan has one required dependency; reference-backed optional dependencies are added by this generic renderer extension')
    return '\n'.join(lines+extra)+'\n',stories+'\n',manifest
