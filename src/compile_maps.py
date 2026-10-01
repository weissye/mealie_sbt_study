"""Compile separate data, operation-input and relationship-template maps.

Python 3.9+, standard library only. Static candidates never become proven
preconditions. Schema recursion never becomes a mandatory execution cycle.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

METHODS = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'}

def references(node, location=''):
    if isinstance(node, dict):
        if '$ref' in node:
            yield location, node['$ref']
        for key, value in node.items():
            if key not in {'$ref', 'example', 'examples', 'default', 'enum', 'const'}:
                yield from references(value, location + '/' + key)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from references(value, location + '/' + str(i))

def components(nodes, edges):
    """Return cyclic strongly connected components using Tarjan's algorithm."""
    graph = {n: [] for n in nodes}
    for a, b in edges:
        if a in graph and b in graph:
            graph[a].append(b)
    index, low, stack, active, result = {}, {}, [], set(), []
    def visit(n):
        index[n] = low[n] = len(index)
        stack.append(n); active.add(n)
        for nxt in graph[n]:
            if nxt not in index:
                visit(nxt); low[n] = min(low[n], low[nxt])
            elif nxt in active:
                low[n] = min(low[n], index[nxt])
        if low[n] == index[n]:
            part = []
            while True:
                x = stack.pop(); active.remove(x); part.append(x)
                if x == n: break
            if len(part) > 1 or n in graph[n]: result.append(sorted(part))
    for n in graph:
        if n not in index: visit(n)
    return sorted(result)

def nullable(node):
    return node.get('nullable') is True or node.get('type') == 'null' or (
        isinstance(node.get('type'), list) and 'null' in node['type']) or any(
        x.get('type') == 'null' for key in ('anyOf', 'oneOf') for x in node.get(key, []) if isinstance(x, dict))

def compile_contract(spec, profile, raw_bytes):
    schemas = spec.get('components', {}).get('schemas', {})
    alias = {}
    for family, meta in profile['families'].items():
        for view in meta['schemas']:
            if view not in schemas: continue
            if view in alias and alias[view] != family:
                raise ValueError('Ambiguous schema-family assignment: ' + view)
            alias[view] = family
    schema_edges = []
    for name, schema in schemas.items():
        for location, target in references(schema):
            if target.startswith('#/components/schemas/'):
                schema_edges.append({'source': name, 'target': target.split('/')[-1],
                                     'location': location, 'evidence': 'explicit $ref'})
    slots = []
    for name, schema in schemas.items():
        for field, node in schema.get('properties', {}).items():
            target = profile['field_targets'].get(field)
            if field in ('id', 'slug', 'username'):
                target = alias.get(name)
                if field == 'username' and target != 'User': target = None
            if target:
                kind = field if field in ('id', 'slug', 'username') else 'id'
                slots.append({'schema': name, 'field': field, 'entity_type': target,
                              'identifier_kind': kind, 'business_type': target + '.' + kind,
                              'wire_schema': node, 'required': field in schema.get('required', []),
                              'nullable': nullable(node), 'read_only': bool(node.get('readOnly')),
                              'evidence': 'reviewed profile; runtime co-reference still required'})
    slot_index = {(x['schema'], x['field']): x for x in slots}
    operations = []
    def resource(path):
        matches = [(prefix, family) for prefix, family in profile['resource_routes'].items()
                   if path == prefix or path.startswith(prefix + '/')]
        return max(matches, key=lambda item: len(item[0]))[1] if matches else None
    for path, path_item in spec['paths'].items():
        for method, op in path_item.items():
            if method not in METHODS: continue
            parameters = path_item.get('parameters', []) + op.get('parameters', [])
            fields, unresolved = [], []
            for param in parameters:
                if '$ref' in param:
                    unresolved.append({'reason':'parameter reference unresolved', 'reference':param['$ref']}); continue
                name = param['name']; role = profile['path_roles'].get(name)
                if role is None and param.get('in') == 'path':
                    # The route prefix at the parameter position, not the final response entity,
                    # identifies nested parent parameters such as users/{id}/ratings/{slug}.
                    prefix = path.split('{' + name + '}')[0].rstrip('/')
                    family = resource(prefix)
                    if family and name in ('id', 'item_id', 'slug'):
                        role = [family, 'slug' if name == 'slug' else 'id']
                    if family == 'User' and name == 'slug': role = ['Recipe', 'slug']
                row = {'location':param.get('in'), 'name':name,
                       'required':bool(param.get('required')), 'wire_schema':param.get('schema', {})}
                if role:
                    row.update(entity_type=role[0], identifier_kind=role[1], business_type='.'.join(role),
                               evidence='reviewed route/profile candidate', runtime_confirmed=False)
                elif param.get('in') == 'path': unresolved.append({'reason':'path identity role unknown','name':name})
                fields.append(row)
            body_schemas=[]; body_slots=[]
            body=op.get('requestBody', {})
            if '$ref' in body:
                unresolved.append({'reason':'requestBody reference unresolved','reference':body['$ref']})
            def scan_request(node, location, required, visited):
                if not isinstance(node, dict): return
                ref=node.get('$ref')
                if ref:
                    if not ref.startswith('#/components/schemas/'):
                        unresolved.append({'reason':'external reference unresolved','reference':ref}); return
                    name=ref.split('/')[-1]
                    if name in visited:
                        unresolved.append({'reason':'recursive input expansion stopped','schema':name,'location':location}); return
                    schema=schemas.get(name, {})
                    for field, child in schema.get('properties', {}).items():
                        if child.get('readOnly'): continue
                        slot=slot_index.get((name,field))
                        req=required and field in schema.get('required', [])
                        if slot:
                            body_slots.append({'location':location+'/'+field,'entity_type':slot['entity_type'],
                                               'identifier_kind':slot['identifier_kind'],'business_type':slot['business_type'],
                                               'required':req,'nullable':nullable(child),'evidence':'profile + schema field',
                                               'runtime_confirmed':False})
                        scan_request(child,location+'/'+field,req,visited | {name})
                    if not schema.get('properties'): scan_request(schema,location,required,visited | {name})
                else:
                    for field,child in node.get('properties',{}).items():
                        if not child.get('readOnly'):
                            scan_request(child,location+'/'+field,required and field in node.get('required',[]),visited)
                    if 'items' in node: scan_request(node['items'],location+'[]',required and node.get('minItems',0)>0,visited)
                    for key in ('anyOf','oneOf','allOf'):
                        for i,child in enumerate(node.get(key,[])):
                            # A union branch is not a jointly mandatory dependency.
                            scan_request(child,location+'/'+key+'/'+str(i),required and key=='allOf',visited)
            for media, content in body.get('content', {}).items():
                schema=content.get('schema', {})
                body_schemas.extend(target.split('/')[-1] for _, target in references(schema))
                scan_request(schema,'body/'+media,bool(body.get('required')),set())
            response_schemas=sorted(set(target.split('/')[-1] for _, target in references(op.get('responses', {}))
                                        if target.startswith('#/components/schemas/')))
            operations.append({'operation_id':op.get('operationId',method.upper()+' '+path),
                               'method':method.upper(),'path':path,'resource_candidate':resource(path),
                               'parameters':fields,'body_required':bool(body.get('required')),
                               'body_schemas':sorted(set(body_schemas)),'body_identity_slots':body_slots,
                               'response_schemas':response_schemas,'security':op.get('security',spec.get('security',[])),
                               'binding_mode':'joint context binding; never independent random IDs',
                               'status':'STATIC_CANDIDATES_NOT_LIVE_PRECONDITIONS','unresolved':unresolved})
    cycles=components(schemas,[(e['source'],e['target']) for e in schema_edges])
    cycle_details=[]
    for part in cycles:
        members=set(part);breaks=[]
        for name in part:
            schema=schemas[name]
            for field,node in schema.get('properties',{}).items():
                if any(t.split('/')[-1] in members for _,t in references(node)):
                    options=[]
                    if field not in schema.get('required',[]): options.append('omit optional property')
                    if nullable(node): options.append('choose explicit null alternative')
                    variants=[node]+[x for k in ('anyOf','oneOf') for x in node.get(k,[]) if isinstance(x,dict)]
                    if any(x.get('type')=='array' and x.get('minItems',0)==0 for x in variants):
                        options.append('use empty array where allowed')
                    breaks.append({'schema':name,'field':field,'contract_allowed_breaks':options})
        cycle_details.append({'members':part,'kind':'SCHEMA_RECURSION','fields':breaks,
                              'execution_policy':'create bounded objects first; attach by a documented operation only',
                              'mandatory_creation_cycle_proven':False})
    templates=[]
    for hint in profile.get('relationship_hints',[]):
        if hint['source'] not in profile['families'] or hint['target'] not in profile['families']: continue
        templates.append({**hint,'status':'STATIC_RELATIONSHIP_TEMPLATE',
                          'is_creation_precondition':False,'is_database_fk':False,
                          'runtime_edge_requires':'successful response / independent observation',
                          'profile_present_in_contract':any(s in schemas for s in profile['families'][hint['source']]['schemas']) and
                                                        any(s in schemas for s in profile['families'][hint['target']]['schemas'])})
    manifest={'stage':'M2_STATIC_READY','contract_sha256':hashlib.sha256(raw_bytes).hexdigest(),
              'info':spec.get('info',{}),'schema_count':len(schemas),'schema_reference_count':len(schema_edges),
              'operation_count':len(operations),'family_count':len(profile['families']),
              'schema_alias_count':len(alias),'identity_slot_count':len(slots),
              'relationship_template_count':len(templates),'schema_cycle_count':len(cycles),
              'live_server_validated':False,'runtime_bindings_observed':0,
              'validation_scope':'Static contract analysis only. Server reachability is recorded separately in the acceptance report.',
              'warning':('Reference nightly contract. Recompile from the pinned local server before live execution.'
                         if str(spec.get('info',{}).get('version','')).lower()=='nightly'
                         else 'Static maps compiled for the supplied contract version. Authentication, fixtures and runtime bindings are not validated by this compiler.')}
    return {'01_data_map.json':{'nodes':schemas,'schema_aliases':alias,'edges':schema_edges},
            '02_operation_map.json':{'operations':operations,'scope':'input binding candidates, not proven business preconditions'},
            '03_relationship_map.json':{'templates':templates,'instances':[],'observed_edges':[]},
            'resource_catalog.json':{'families':profile['families'],'schema_aliases':alias,'identity_slots':slots,
                                     'identity_rule':'Same business type + same run/scope + observed alias evidence; wire format alone never merges entities.'},
            'cycle_report.json':{'components':cycle_details,'creation_dependencies':'not yet empirically confirmed'},
            'manifest.json':manifest}

def main():
    p=argparse.ArgumentParser();p.add_argument('--contract',required=True);p.add_argument('--profile',required=True);p.add_argument('--out',required=True)
    args=p.parse_args();raw=Path(args.contract).read_bytes();spec=json.loads(raw.decode('utf-8-sig'));profile=json.loads(Path(args.profile).read_text(encoding='utf-8-sig'))
    results=compile_contract(spec,profile,raw);out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    for name,value in results.items(): (out/name).write_text(json.dumps(value,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
    print(json.dumps(results['manifest.json'],indent=2))
    print('MEALIE_M2_STATIC_MAPS_READY')

if __name__=='__main__': main()
