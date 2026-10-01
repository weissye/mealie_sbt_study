"""Validated Provengo event replay and typed interfaces for bounded acceptance."""
import copy
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from accept_identity import AcceptanceError
from create_pilot_fixture import require
from rtv import RTV
from .pipeline import compile_model, render_interfaces, render_stories

def verify_live_contract(client, expected_digest):
    request = urllib.request.Request(client.base + '/openapi.json', headers={'Accept': 'application/json'}, method='GET')
    try:
        with client.opener.open(request, timeout=20) as response:
            require(response.status == 200, 'Live contract request did not return HTTP 200.')
            raw = response.read(2 * 1024 * 1024 + 1)
    except (urllib.error.URLError, OSError):
        raise AcceptanceError('Live contract read failed; no authentication or mutation was sent.') from None
    require(len(raw) <= 2 * 1024 * 1024, 'Live contract exceeds the accepted response bound.')
    require(hashlib.sha256(raw).hexdigest() == expected_digest, 'Live server contract differs from the pinned reviewed contract; no authentication or mutation was sent.')
    return {'path': '/openapi.json', 'method': 'GET', 'status': 200, 'sha256': expected_digest}

def load_project(root, project=None):
    if project is None:
        candidates = sorted((root / 'provengo').glob('offline-*/readiness.json'), key=lambda p: p.stat().st_mtime, reverse=True)
        require(bool(candidates), 'No sampled offline project was found.')
        project = candidates[0].parent
    project = project.resolve()
    require(project.parent == (root / 'provengo').resolve() and project.name.startswith('offline-'), 'Project must be an owned offline project.')
    def load(name):
        return json.loads((project / name).read_text(encoding='utf-8-sig'))
    model = compile_model(root / 'model/mealie-openapi.v3.28.0.reviewed.json', root / 'profiles/mealie-pilot.json')
    readiness = load('readiness.json')
    require(readiness.get('sampleExitCode') == 0, 'The selected project was not sampled successfully.')
    report = load('generation-report.json')
    require(report.get('contract_sha256') == model['contract_sha256'] and report.get('profile_sha256') == model['profile_sha256'], 'Sampled contract/profile hashes differ from current generator inputs.')
    for name, expected in [('operations-ir.json', model['operations']), ('scenario-ir.json', model['stories']), ('schemas-ir.json', model['schemas'])]:
        require(load(name) == expected, 'Sampled IR differs from the current generator: ' + name)
    for name, expected in [('00_interfaces.js', render_interfaces(model)), ('10_stories.js', render_stories(model))]:
        require((project / 'spec/js' / name).read_text(encoding='utf-8-sig') == expected, 'Sampled JavaScript differs from the current generator.')
    samples = load('samples.json')
    from prepare_provengo_model import enumerate_orders
    expected_orders = enumerate_orders(model['stories'])
    require(load('expected-orders.json') == expected_orders, 'Expected schedule manifest differs.')
    expected = {step['id']: {**step, 'story': story['name'], 'actor': model['profile']['actor'], 'mode': model['profile']['mode']}
                for story in model['stories'] for step in story['steps']}
    require(isinstance(samples, list) and len(samples) == len(expected_orders), 'Sample count differs from exhaustive coverage.')
    observed = []
    for sequence in samples:
        require(isinstance(sequence, list) and len(sequence) == len(expected), 'Incomplete symbolic sample.')
        identifiers = []
        for event in sequence:
            require(isinstance(event, dict) and event.get('name') == 'SBT:Step', 'Unexpected sampled event.')
            data = event.get('data', {})
            require(isinstance(data, dict) and data.get('id') in expected and data == expected[data['id']], 'Sampled event differs from the generated operation or typed binding.')
            identifiers.append(data['id'])
        observed.append(tuple(identifiers))
    require(len(set(observed)) == len(expected_orders) and set(observed) == set(map(tuple, expected_orders)), 'Sample coverage is duplicate, incomplete or order-invalid.')
    bindings = load('fixture-bindings.json')
    require(bindings.get('contract_sha256') == model['contract_sha256'], 'Fixture contract hash differs.')
    return project, model, bindings, samples

class TypedBindings:
    def __init__(self, identity, owned, seeded_runtime):
        self.rtv = RTV(identity['run_id'])
        self.owned = owned
        self.seeded = seeded_runtime
        user = next(x for x in identity['records'].values() if x['entity_type'] == 'User')
        self.scope = user['scope']
        self.user_id = user['identifiers']['id']
        self.records = {}
        mapping = {}
        for old_id, old in identity['records'].items():
            mapping[old_id] = self.rtv.observe(old['entity_type'], old['symbols'][0], old['scope'], old['identifiers'],
                                             'current authenticated self reads', values=old['values'])
        for edge in identity['observed_edges']:
            self.rtv.observe_link(edge['relation'], mapping[edge['source']], mapping[edge['target']], edge['evidence'])

    def observe(self, entity, symbol, body, source):
        seed = [x for x in self.seeded['records'].values() if entity == x['entity_type'] and symbol in x['symbols']]
        require(len(seed) == 1 and seed[0]['state'] == 'OBSERVED', 'Owned resource lacks one accepted typed seed.')
        require(body.get('id') == self.owned[symbol]['id'] == seed[0]['identifiers']['id'] and body.get('name') == self.owned[symbol]['name'], 'Fresh resource differs from its owned identity/name.')
        require(body.get('groupId', self.scope['group']) == self.scope['group'], 'Fresh resource group differs.')
        scoped = entity in ('Recipe', 'Shopping list')
        if scoped:
            require(body.get('householdId') == self.scope['household'] and body.get('userId') == self.user_id, 'Fresh resource household or user differs.')
        scope = self.scope if scoped else {'group': self.scope['group']}
        require(seed[0]['scope'] == scope, 'Accepted fixture scope differs from authenticated scope.')
        identifiers = {'id': body['id']}
        if entity in ('Recipe', 'Category', 'Tag'):
            require(body.get('slug') == self.owned[symbol].get('slug') == seed[0]['identifiers'].get('slug'), 'Fresh resource slug differs.')
            identifiers['slug'] = body['slug']
        self.records[symbol] = self.rtv.observe(entity, symbol, scope, identifiers, source, values={'name': body['name']})

    def resolve(self, binding):
        entity, kind = binding['type'].rsplit('.', 1)
        matches = [x for x in self.rtv.records.values() if binding['symbol'] in x['symbols'] and x['entity_type'] == entity and x['state'] == 'OBSERVED']
        require(len(matches) == 1 and kind in matches[0]['identifiers'], 'No fresh typed runtime binding: ' + binding['symbol'])
        return matches[0]['identifiers'][kind]

class BoundedTransport:
    def __init__(self, client, allowed_pairs):
        self.client = client
        self.allowed_pairs = set(allowed_pairs)

    def call(self, method, path, payload=None):
        require((method, path) in self.allowed_pairs, 'Dispatch is outside the standalone operation allowlist.')
        return self.client.call(method, path, payload)

class OperationInterfaces:
    def __init__(self, model, bindings, transport):
        self.model = model
        self.bindings = bindings
        self.transport = transport
        self.events = []

    def invoke(self, event, payload=None):
        data = event['data']
        operation = self.model['operations'][data['operation']]
        require(data['method'] == operation['method'].upper() and data['path'] == operation['path'], 'Event transport details differ from operation IR.')
        path = operation['path']
        for parameter, binding in data['bindings'].items():
            path = path.replace('{' + parameter + '}', urllib.parse.quote(str(self.bindings.resolve(binding)), safe=''))
        require('{' not in path and '}' not in path, 'Operation still has unbound path parameters.')
        require(any(x['status'] == '200' for x in operation['responses']), 'Standalone backend expects a documented HTTP 200 response.')
        self.events.append({'event': copy.deepcopy(event), 'resolved_path': path, 'completed': False})
        response = self.transport.call(operation['method'].upper(), path, payload)
        self.events[-1]['completed'] = True
        return response
