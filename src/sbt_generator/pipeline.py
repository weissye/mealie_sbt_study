"""Contract-derived operation IR and policy-driven scenario generation."""
import json
import hashlib
import re
from dataclasses import asdict
from pathlib import Path
from .parsing.loader import load_raw, load_and_resolve
from .parsing.normalize import normalize

TEMPLATES = {
    'read_update_verify_restore': [('read', 'capture'), ('update', 'update'),
                                   ('read', 'verify_update'), ('update', 'restore')],
    'remove_verify_add_verify': [('remove_link', 'remove_link'), ('read', 'verify_absent'),
                               ('add_link', 'add_link'), ('read', 'verify_present')]
}

def expand_policy(policy):
    template = TEMPLATES.get(policy['template'])
    if template is None:
        raise ValueError('Unknown functional scenario template: ' + policy['template'])
    for index, (role, action) in enumerate(template, 1):
        if role not in policy['operations']:
            raise ValueError('Scenario is missing an operation role: ' + role)
        yield {**policy['operations'][role], 'id': policy['id_prefix'] + str(index), 'action': action}

def compile_model(contract_path, profile_path):
    raw = load_raw(str(contract_path))
    resolved, unsupported = load_and_resolve(str(contract_path))
    if unsupported:
        raise ValueError('Unsupported references: ' + ', '.join(unsupported))
    document = normalize(resolved, raw)
    catalog = {}
    for op in document.operations:
        key = op.operation_id or (op.method.upper() + ' ' + op.path)
        if key in catalog:
            raise ValueError('Duplicate operation identity: ' + key)
        catalog[key] = asdict(op)
    profile = json.loads(Path(profile_path).read_text(encoding='utf-8-sig'))
    if profile.get('mode') != 'SYMBOLIC_ONLY':
        raise ValueError('Only symbolic generation is accepted by this backend.')
    stories = []
    identifiers = set()
    for policy in profile['stories']:
        if any(s['name'] == policy['name'] for s in stories):
            raise ValueError('Duplicate story name: ' + policy['name'])
        story = {'name': policy['name'], 'oracles': policy.get('oracles', {}), 'steps': []}
        for intent in expand_policy(policy):
            operation = catalog.get(intent['operation'])
            if operation is None:
                raise ValueError('Profile operation is absent from OpenAPI: ' + intent['operation'])
            parameters = {p['name']: p for p in operation['parameters'] if p['location'] == 'path'}
            placeholders = set(re.findall(r'\{([^}]+)\}', operation['path']))
            if set(intent['bindings']) != placeholders or set(parameters) != placeholders:
                raise ValueError('Typed bindings must cover exactly the documented path parameters.')
            if any(not v.get('symbol') or not v.get('type') for v in intent['bindings'].values()):
                raise ValueError('Each binding requires a resource symbol and business type.')
            if intent['id'] in identifiers:
                raise ValueError('Duplicate step identity: ' + intent['id'])
            identifiers.add(intent['id'])
            story['steps'].append({**intent, 'method': operation['method'].upper(), 'path': operation['path']})
        stories.append(story)
    return {'profile': profile, 'operations': catalog, 'stories': stories,
            'contract_sha256': hashlib.sha256(Path(contract_path).read_bytes()).hexdigest(),
            'profile_sha256': hashlib.sha256(Path(profile_path).read_bytes()).hexdigest(),
            'schemas': {name: asdict(schema) for name, schema in document.component_schemas.items()},
            'warnings': document.warnings, 'unsupported': document.unsupported}

def render_interfaces(model):
    selected = {step['operation'] for s in model['stories'] for step in s['steps']}
    catalog = {key: model['operations'][key] for key in sorted(selected)}
    return '''// Generated from OpenAPI. Symbolic interface backend; no HTTP transport.
var SBTInterfaces = (function () {
    var operations = ''' + json.dumps(catalog, separators=(',', ':')) + ''';
    return {
        invoke: function (operationKey, context) {
            var operation = operations[operationKey];
            if (!operation) { throw new Error("Unknown operation: " + operationKey); }
            var data = {};
            Object.keys(context).forEach(function (key) { data[key] = context[key]; });
            data.operation = operationKey;
            data.method = operation.method.toUpperCase();
            data.path = operation.path;
            request(Event("SBT:Step", data));
        }
    };
})();
'''

def render_stories(model):
    lines = ['// Generated from scenario IR. No paths, methods or REST details.']
    profile = model['profile']
    for story in model['stories']:
        lines.append('bthread(' + json.dumps(story['name']) + ', function () {')
        for step in story['steps']:
            context = {k: v for k, v in step.items() if k not in ('method', 'path', 'operation')}
            context.update(story=story['name'], actor=profile['actor'], mode=profile['mode'])
            lines.append('    SBTInterfaces.invoke(' + json.dumps(step['operation']) + ', ' + json.dumps(context, separators=(',', ':')) + ');')
        lines.append('});')
    return '\n'.join(lines) + '\n'

def emit(model, project):
    target = project / 'spec/js'
    target.mkdir(parents=True, exist_ok=True)
    (target / '00_interfaces.js').write_text(render_interfaces(model), encoding='utf-8')
    (target / '10_stories.js').write_text(render_stories(model), encoding='utf-8')
    for name, value in [('operations-ir.json', model['operations']), ('schemas-ir.json', model['schemas']),
                        ('scenario-ir.json', model['stories']), ('generation-report.json', {
                            'operation_count': len(model['operations']), 'schema_count': len(model['schemas']),
                            'contract_sha256': model['contract_sha256'], 'profile_sha256': model['profile_sha256'],
                            'selected_operations': len({s['operation'] for story in model['stories'] for s in story['steps']}),
                            'warnings': model['warnings'], 'unsupported': model['unsupported'],
                            'transport': 'symbolic', 'live_execution_accepted': False})]:
        (project / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
