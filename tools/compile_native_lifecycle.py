"""Contract-bound declarative lifecycle compiler; emits native BP, no HTTP client.
The existing generator_v56 CLI supplies the baseline. This optional compiler
adds an explicitly scoped lifecycle policy without modifying the pinned core.
"""
import argparse, copy, hashlib, json, re
from pathlib import Path


def resolve(document, schema, seen=()):
    if '$ref' in schema:
        ref=schema['$ref']
        if ref in seen: return {}
        node=document
        for part in ref.removeprefix('#/').split('/'): node=node[part]
        return resolve(document,node,seen+(ref,))
    out=dict(schema)
    for part in schema.get('allOf',[]):
        p=resolve(document,part,seen)
        out.setdefault('properties',{}).update(p.get('properties',{}))
        out['required']=list(set(out.get('required',[])+p.get('required',[])))
    for choice in ('anyOf','oneOf'):
        if choice in out:
            options=[resolve(document,x,seen) for x in out[choice]]
            return next((x for x in options if x.get('type')!='null'),{})
    return out


def request_schema(document, operation):
    body=resolve(document,operation.get('requestBody',{}))
    content=body.get('content',{})
    return resolve(document,content.get('application/json',{}).get('schema',{}))


def find_field(document,schema,normal):
    props=resolve(document,schema).get('properties',{})
    fields=[x for x in props if re.sub('[^a-z0-9]','',x.lower())==normal]
    if len(fields)!=1:raise ValueError('Contract field unresolved: '+normal)
    return fields[0]


def validate_template(document,schema,value,label):
    schema=resolve(document,schema)
    if isinstance(value,dict):
        props=schema.get('properties',{})
        for key in value:
            if key not in props:raise ValueError(label+': field absent from contract: '+key)
            validate_template(document,props[key],value[key],label+'.'+key)
        # Runtime snapshots satisfy other required fields for projection updates.
    elif isinstance(value,list):
        for v in value:validate_template(document,schema.get('items',{}),v,label+'[]')


def bind(document,profile):
    result=copy.deepcopy(profile)
    for name,op in result['operations'].items():
        path=op['path'];method=op['method'].lower()
        actual=document.get('paths',{}).get(path,{}).get(method)
        if not actual:
            canonical=lambda x:re.sub(r'\{[^}]+\}', '{}', x)
            candidates=[(k,v[method]) for k,v in document.get('paths',{}).items() if canonical(k)==canonical(path) and method in v]
            if len(candidates)==1:op['path'],actual=candidates[0]
        if not actual:raise ValueError('Operation absent from local OpenAPI: '+method+' '+path)
        op['operation_id']=actual.get('operationId')
        op['schema']=request_schema(document,actual)
        codes=[int(x) for x in actual.get('responses',{}) if x.isdigit() and 200<=int(x)<300]
        if not codes:raise ValueError('Success status absent: '+name)
        op['codes']=codes
        if name=='contribution':
            op['increment_field']=find_field(document,op['schema'],'recipeincrementquantity')
            if resolve(document,op['schema']['properties'][op['increment_field']]).get('type') not in ('number','integer'):raise ValueError('Increment quantity is not numeric')
        if name=='recipe_update':
            op['writable_fields']=[k for k,v in op['schema'].get('properties',{}).items() if not resolve(document,v).get('readOnly')]
            for field in ['recipeIngredient','settings']:
                if field not in op['writable_fields']:raise ValueError('Recipe update field unavailable: '+field)
            ingredient=resolve(document,op['schema']['properties']['recipeIngredient'])
            fields=resolve(document,ingredient.get('items',{})).get('properties',{})
            for field in ['quantity','food','unit','note']:
                if field not in fields:raise ValueError('Ingredient field absent: '+field)
            op['ingredient_fields']=list(fields)
    return result


def render(document,profile,base,namespace):
    bound=bind(document,profile)
    bound.update(base_url=base,namespace=namespace)
    operations=bound['operations']
    for step in bound['steps'].values():
        op=operations[step['operation']]
        if 'scale' in step:step['body']={op['increment_field']:step['scale']}
        if 'body' in step:validate_template(document,op['schema'],step['body'],step['operation'])
        for check in step.get('verify',[]):
            if 'prepare' in check:
                prep=check['prepare'];validate_template(document,operations[prep['operation']]['schema'],prep['override'],prep['operation']+':override')
    engine=(Path(__file__).with_name('native_lifecycle_interfaces.js')).read_text()
    interfaces='//@provengo summon rest\n//@provengo summon rtv\nvar MODEL='+json.dumps(bound,separators=(',',':'))+';\n'+engine
    actors=bound['actors'];lines=['//@provengo summon rest','//@provengo summon rtv',
      'function nativeMatch(name,actor,step){return EventSet(name+":"+actor+":"+step,function(e){return e.name===name&&(!actor||e.data.actor===actor)&&(!step||e.data.step===step);});}',
      'bthread("bootstrap:authentication",function(){nativeLogin();sync({request:Event("Native:Authenticated",{})});var seen={};while(Object.keys(seen).length<'+str(len(actors))+'){var e=sync({waitFor:nativeMatch("Native:Registered","","")});seen[e.data.actor]=true;}sync({request:Event("Native:Start",{})});});']
    for actor,spec in actors.items():
        dependencies=spec.get('depends',[])
        # Collector starts at initialization, remembers every dependency ready event.
        if dependencies:
            lines.append('bthread('+json.dumps('dependencies:'+actor)+',function(){var required='+json.dumps(dependencies)+',seen={};while(required.some(function(k){return !seen[k];})){var e=sync({waitFor:nativeMatch("Native:Ready","","")});seen[e.data.actor]=true;}sync({request:Event("Native:DependenciesReady",{actor:'+json.dumps(actor)+'})});});')
        body=['sync({waitFor:nativeMatch("Native:Authenticated","","")});',
          'sync({request:Event("Native:Registered",{actor:'+json.dumps(actor)+'})});',
          'sync({waitFor:nativeMatch("Native:Start","","")});']
        if dependencies:body.append('sync({waitFor:nativeMatch("Native:DependenciesReady",'+json.dumps(actor)+',"")});')
        for sid in spec['steps']:
            data=json.dumps({'actor':actor,'step':sid})
            body+=['sync({request:Event("Native:ActionBegin",'+data+')});','nativeStep('+json.dumps(sid)+');',
              'sync({request:Event("Native:ActionDone",'+data+')});',
              'sync({waitFor:nativeMatch("Native:Verified",'+json.dumps(actor)+','+json.dumps(sid)+')});',
              'sync({request:Event("Native:ActionEnd",'+data+')});']
            verifier='nativeVerify('+json.dumps(sid)+');sync({request:Event("Native:Verified",'+data+')});'
            lines.append('bthread('+json.dumps('verify:'+sid)+',function(){sync({waitFor:nativeMatch("Native:ActionDone",'+json.dumps(actor)+','+json.dumps(sid)+')});'+verifier+'});')
        body+=['sync({request:Event("Native:Ready",{actor:'+json.dumps(actor)+'})});','sync({request:Event("Native:Finished",{actor:'+json.dumps(actor)+'})});']
        lines.append('bthread('+json.dumps('lifecycle:'+actor)+',function(){'+''.join(body)+'});')
    lines.append('bthread("guard:action-readback",function(){while(true){var e=sync({waitFor:nativeMatch("Native:ActionBegin","","")});sync({waitFor:nativeMatch("Native:ActionEnd",e.data.actor,e.data.step),block:nativeMatch("Native:ActionBegin","","")});}});')
    lines.append('bthread("completion",function(){var seen={};while(Object.keys(seen).length<'+str(len(actors))+'){var e=sync({waitFor:nativeMatch("Native:Finished","","")});seen[e.data.actor]=true;}sync({request:Event("Native:Complete",{})});});')
    return interfaces,'\n'.join(lines)+'\n',bound


def main():
    p=argparse.ArgumentParser();p.add_argument('--openapi',required=True);p.add_argument('--profile',required=True);p.add_argument('--output',required=True);p.add_argument('--base-url',default='http://127.0.0.1:9925');p.add_argument('--namespace',required=True)
    a=p.parse_args();doc=json.loads(Path(a.openapi).read_text(encoding='utf-8-sig'));profile=json.loads(Path(a.profile).read_text(encoding='utf-8-sig'))
    interfaces,stories,bound=render(doc,profile,a.base_url,a.namespace)
    output=Path(a.output);js=output/'spec/js';js.mkdir(parents=True,exist_ok=True);(output/'config').mkdir(exist_ok=True)
    for name,data in [('interfaces.mealie.js',interfaces),('stories.mealie.js',stories)]: (js/name).write_bytes(data.encode())
    (output/'config/provengo.yml').write_text('version: 2\n')
    (output/'native-policy-bound.json').write_text(json.dumps(bound,indent=2))
    report={'status':'GENERATED_NOT_EXECUTED','contract_normalized_sha256':hashlib.sha256(Path(a.openapi).read_bytes().replace(b'\r\n',b'\n')).hexdigest(),'policy_sha256':hashlib.sha256(Path(a.profile).read_bytes().replace(b'\r\n',b'\n')).hexdigest(),'actors':list(bound['actors']),'steps':list(bound['steps']),'simultaneous_http':False,'historical_stories_reused':False,'core_modified':False,'full_crud':False,'deletion':False,'semantic_policy_from_openapi':False}
    (output/'generation-report-native.json').write_text(json.dumps(report,indent=2));print('F01_NATIVE_JS_GENERATED: '+str(output))
if __name__=='__main__':main()
