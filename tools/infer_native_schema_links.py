"""OpenAPI reference-backed optional dependency inference, without application names."""
import re

def canonical(ref):
    return re.sub(r'-(Input|Output)$','',ref.rsplit('/',1)[-1])

def refs(shape):
    if '$ref' in shape:yield shape['$ref']
    for name in ('anyOf','oneOf','allOf'):
        for branch in shape.get(name,[]):yield from refs(branch)

def request_schema(document,operation):
    value=document['paths'][operation.op.path][operation.op.method.lower()]['requestBody']['content']['application/json']['schema']
    return document['components']['schemas'][value['$ref'].rsplit('/',1)[-1]] if '$ref' in value else value

def response_refs(document,entity):
    responses=document['paths'][entity.get_op.op.path]['get']['responses']
    found=set()
    for code,response in responses.items():
        if code.isdigit() and 200<=int(code)<300:
            for media,value in response.get('content',{}).items():
                if media=='application/json':found.update(refs(value['schema']))
    return found

def infer_links(document,plan,child_key,target_keys):
    from render_native_interleaved_dependencies import concrete,identity
    entities={e.entity.key:e for e in plan.entities};child=entities[child_key]
    properties=request_schema(document,child.create_op).get('properties',{})
    result=[]
    for key in target_keys:
        target=entities[key];get_refs=response_refs(document,target);matches=[]
        for field,shape in properties.items():
            matched=[ref for ref in refs(shape) if canonical(ref) in {canonical(x) for x in get_refs}]
            if not matched:continue
            # Generic companion field convention; confirm identity scalar type/format.
            binding=field+identity(target)[0].upper()+identity(target)[1:]
            if binding not in properties:continue
            scalar=concrete(properties[binding])
            from render_native_interleaved_dependencies import response_schema
            target_id=concrete(response_schema(target.get_op)['properties'][identity(target)])
            if scalar.get('type')!=target_id.get('type') or scalar.get('format')!=target_id.get('format'):continue
            matches.append({'target':key,'field':binding,'embedded_field':field,'source_refs':matched,'target_get_refs':sorted(get_refs),'rule':'Canonical Input/Output schema reference + schema-checked companion identity field','optional':binding not in request_schema(document,child.create_op).get('required',[])})
        if len(matches)!=1:raise ValueError('Optional dependency reference ambiguous or missing: '+key)
        result.extend(matches)
    return result
