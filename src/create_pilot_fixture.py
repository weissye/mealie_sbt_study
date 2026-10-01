"""One bounded, serial, local functional fixture with independently read links."""
import argparse
import copy
import getpass
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from accept_identity import AcceptanceError, LocalClient, accepted_observations, check_contract, identity_uuid
from rtv import RTV

COLLECTIONS = {'Food': '/api/foods', 'Unit': '/api/units',
    'Category': '/api/organizers/categories', 'Tag': '/api/organizers/tags',
    'Shopping list': '/api/households/shopping/lists'}
FOODS = {'R1': ['F1', 'F3'], 'R2': ['F1', 'F2'], 'R3': ['F2', 'F3']}
CATEGORIES = {'R1': ['C1'], 'R2': ['C1', 'C2'], 'R3': ['C2']}
TAGS = {'R1': ['T1', 'T2'], 'R2': ['T2'], 'R3': ['T1']}
LISTS = {'L1': ['R1', 'R2'], 'L2': ['R2', 'R3']}

def require(condition, message):
    if not condition:
        raise AcceptanceError(message)

def scrub(value):
    if isinstance(value, dict):
        return {k: scrub(v) for k, v in value.items() if k.lower().replace('_', '') not in
            ('password', 'token', 'tokens', 'accesstoken', 'refreshtoken', 'apikey', 'secret', 'authorization')}
    if isinstance(value, list):
        return [scrub(v) for v in value]
    return value

class FixtureClient(LocalClient):
    def __init__(self, base, output):
        super().__init__(base)
        self.token = None
        self.output = output
        self.trace = []
        self.owned_paths = set()
        self.link_paths = set()

    def request(self, path, token=None, credentials=None):
        status, body = super().request(path, token=token, credentials=credentials)
        if credentials is not None:
            self.token = body.get('access_token')
        return status, body

    def call(self, method, path, payload=None):
        allowed = (method == 'POST' and path in list(COLLECTIONS.values()) + ['/api/recipes']) or (
            method == 'GET' and path in self.owned_paths) or (
            method == 'PUT' and path in self.owned_paths and path.startswith('/api/recipes/')) or (
            method == 'POST' and path in self.link_paths)
        require(allowed, 'Operation is outside the owned fixture allowlist.')
        require(len(self.trace) < 64, 'Fixture request budget was reached.')
        entry = {'method': method, 'path': path, 'request': scrub(payload), 'status': None}
        self.trace.append(entry)
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + self.token}
        data = None
        if payload is not None:
            data = json.dumps(payload).encode('utf-8'); headers['Content-Type'] = 'application/json'
        try:
            request = urllib.request.Request(self.base + path, data=data, headers=headers, method=method)
            try:
                with self.opener.open(request, timeout=20) as response:
                    entry['status'] = response.status
                    raw = response.read(2 * 1024 * 1024 + 1)
            except urllib.error.HTTPError as error:
                entry['status'] = error.code
                raise AcceptanceError('HTTP ' + str(error.code) + ' from fixture ' + method + ' ' + path) from None
            except (urllib.error.URLError, OSError):
                raise AcceptanceError('Fixture transport stopped. Inspect the trace before retrying; no automatic retry was sent.') from None
            require(len(raw) <= 2 * 1024 * 1024, 'Fixture response exceeds the accepted bound.')
            try:
                body = json.loads(raw)
            except ValueError:
                raise AcceptanceError('Fixture response is not JSON.') from None
            entry['response'] = scrub(body)
            expected = 201 if path in list(COLLECTIONS.values()) + ['/api/recipes'] and method == 'POST' else 200
            require(entry['status'] == expected, 'Fixture response status does not match the reviewed contract.')
            return body
        finally:
            (self.output / 'trace.json').write_text(json.dumps(self.trace, indent=2) + '\n', encoding='utf-8')

def minimal_resource(body):
    return {key: body[key] for key in ('id', 'name')}

class Pilot:
    def __init__(self, client, runtime, prefix):
        self.client = client; self.prefix = prefix; self.objects = {}; self.records = {}
        self.rtv = RTV(runtime['run_id'])
        mapping = {}
        for old, record in runtime['records'].items():
            mapping[old] = self.rtv.observe(record['entity_type'], record['symbols'][0], record['scope'],
                record['identifiers'], 'current authenticated self reads', values=record['values'])
        for edge in runtime['observed_edges']:
            self.rtv.observe_link(edge['relation'], mapping[edge['source']], mapping[edge['target']], edge['evidence'])
        user = next(r for r in runtime['records'].values() if r['entity_type'] == 'User')
        self.scope = user['scope']; self.group_scope = {'group': self.scope['group']}
        self.user_id = user['identifiers']['id']

    def bind(self, entity, symbol, body, source):
        require(isinstance(body, dict), 'Expected an object for ' + entity)
        identifier = identity_uuid(body.get('id'), entity + '.id')
        for field, expected in [('groupId', self.scope['group']), ('householdId', self.scope['household'])]:
            if body.get(field) is not None:
                require(identity_uuid(body[field], field) == expected, 'Fixture resource scope differs: ' + field)
        ids = {'id': identifier}
        if entity in ('Category', 'Tag', 'Recipe'):
            require(isinstance(body.get('slug'), str) and body['slug'], 'Missing observed slug for ' + entity)
            ids['slug'] = body['slug']
        scope = self.scope if entity in ('Recipe', 'Shopping list') else self.group_scope
        record = self.rtv.observe(entity, symbol, scope, ids, source, values={'name': body.get('name')})
        self.objects[symbol] = body; self.records[symbol] = record
        return record

    def create_collection(self, entity, symbol):
        name = self.prefix + '-' + symbol
        path = COLLECTIONS[entity]
        created = self.client.call('POST', path, {'name': name})
        identifier = created.get('id') if isinstance(created, dict) else created
        identifier = identity_uuid(identifier, entity + '.create')
        read_path = path + '/' + identifier
        self.client.owned_paths.add(read_path)
        body = self.client.call('GET', read_path)
        require(body.get('name') == name, 'Created resource did not read back with the fixture name.')
        require(identity_uuid(body.get('id'), entity + '.read') == identifier, 'Create and read identifiers disagree.')
        self.bind(entity, symbol, body, 'GET ' + read_path)

    def configure_recipe(self, symbol):
        name = self.prefix + '-' + symbol
        slug = self.client.call('POST', '/api/recipes', {'name': name})
        require(isinstance(slug, str) and slug.startswith(self.prefix), 'Recipe creation did not return the owned fixture slug.')
        path = '/api/recipes/' + urllib.parse.quote(slug, safe='')
        self.client.owned_paths.add(path)
        initial = self.client.call('GET', path)
        require(initial.get('name') == name, 'Created recipe name differs.')
        self.bind('Recipe', symbol, initial, 'GET ' + path)
        ingredients = []
        for food in FOODS[symbol]:
            unit = 'Q2' if food == 'F3' else 'Q1'
            ingredients.append({'quantity': 1, 'food': minimal_resource(self.objects[food]),
                'unit': minimal_resource(self.objects[unit]), 'referenceId': str(uuid.uuid4()), 'note': ''})
        payload = {'id': initial['id'], 'name': name, 'slug': slug,
            'userId': self.user_id, 'groupId': self.scope['group'], 'householdId': self.scope['household'],
            'recipeServings': 2, 'recipeYieldQuantity': 2, 'recipeIngredient': ingredients,
            'recipeCategory': [{k: self.objects[x][k] for k in ('id', 'name', 'slug')} for x in CATEGORIES[symbol]],
            'tags': [{k: self.objects[x][k] for k in ('id', 'name', 'slug')} for x in TAGS[symbol]],
            'description': 'Serial functional fixture; shared resources.'}
        self.client.call('PUT', path, payload)
        body = self.client.call('GET', path)
        require(body.get('id') == initial['id'] and body.get('slug') == slug, 'Recipe identity changed during configuration.')
        require({x['id'] for x in body.get('recipeCategory') or []} == {self.objects[x]['id'] for x in CATEGORIES[symbol]}, 'Recipe category readback differs.')
        require({x['id'] for x in body.get('tags') or []} == {self.objects[x]['id'] for x in TAGS[symbol]}, 'Recipe tag readback differs.')
        actual = body.get('recipeIngredient') or []
        require(len(actual) == 2, 'Recipe ingredient occurrence count differs.')
        expected = {x['referenceId']: x for x in ingredients}
        require({x.get('referenceId') for x in actual} == set(expected), 'Ingredient occurrence keys were not preserved.')
        self.bind('Recipe', symbol, body, 'GET ' + path)
        for item in actual:
            intended = expected[item['referenceId']]
            require(item.get('food', {}).get('id') == intended['food']['id'] and
                    item.get('unit', {}).get('id') == intended['unit']['id'] and item.get('quantity') == 1,
                    'Ingredient food, unit or quantity differs on readback.')
            food_symbol = next(x for x in FOODS[symbol] if self.objects[x]['id'] == item['food']['id'])
            unit_symbol = 'Q2' if food_symbol == 'F3' else 'Q1'
            ingredient = self.rtv.observe('Recipe ingredient', symbol + ':' + item['referenceId'],
                {**self.scope, 'recipe': body['id']}, {'referenceId': item['referenceId']}, 'GET ' + path)
            self.rtv.observe_link('Recipe.ingredient', self.records[symbol], ingredient, 'GET ' + path)
            self.rtv.observe_link('Ingredient.food', ingredient, self.records[food_symbol], 'GET ' + path)
            self.rtv.observe_link('Ingredient.unit', ingredient, self.records[unit_symbol], 'GET ' + path)
        for relation, symbols in [('Recipe.category', CATEGORIES[symbol]), ('Recipe.tag', TAGS[symbol])]:
            for target in symbols:
                self.rtv.observe_link(relation, self.records[symbol], self.records[target], 'GET ' + path)

    def inspect_list(self, symbol):
        list_id = self.objects[symbol]['id']
        path = COLLECTIONS['Shopping list'] + '/' + list_id
        body = self.client.call('GET', path)
        require(body.get('id') == list_id, 'Shopping list readback identity differs.')
        self.bind('Shopping list', symbol, body, 'GET ' + path)
        expected_recipes = {self.objects[r]['id']: r for r in LISTS[symbol]}
        refs = body.get('recipeReferences') or []
        require(len(refs) == len(expected_recipes) and {r.get('recipeId') for r in refs} == set(expected_recipes), 'List-level recipe links differ.')
        for ref in refs:
            require(ref.get('shoppingListId') == list_id, 'List-level link parent differs.')
            link = self.rtv.observe('List-recipe link', symbol + ':' + ref['recipeId'], self.scope,
                {'id': identity_uuid(ref.get('id'), 'List-recipe link.id')}, 'GET ' + path)
            self.rtv.observe_link('List.link', self.records[symbol], link, 'GET ' + path)
            self.rtv.observe_link('List-recipe link.recipe', link, self.records[expected_recipes[ref['recipeId']]], 'GET ' + path)
        items = body.get('listItems') or []
        require(items, 'Shopping list contains no generated items.')
        expected_foods = {self.objects[f]['id']: f for r in LISTS[symbol] for f in FOODS[r]}
        observed_foods = set(); observed_recipes = set()
        for item in items:
            require(item.get('shoppingListId') == list_id, 'Shopping item parent differs.')
            require(item.get('groupId') == self.scope['group'] and item.get('householdId') == self.scope['household'], 'Shopping item scope differs.')
            food_id = item.get('foodId'); unit_id = item.get('unitId')
            require(food_id in expected_foods, 'Shopping item food is outside the expected fixture.')
            food_symbol = expected_foods[food_id]; unit_symbol = 'Q2' if food_symbol == 'F3' else 'Q1'
            require(unit_id == self.objects[unit_symbol]['id'], 'Shopping item unit differs.')
            observed_foods.add(food_id)
            item_id = identity_uuid(item.get('id'), 'Shopping item.id')
            item_record = self.rtv.observe('Shopping item', symbol + ':' + item_id, self.scope, {'id': item_id}, 'GET ' + path)
            self.rtv.observe_link('List.item', self.records[symbol], item_record, 'GET ' + path)
            self.rtv.observe_link('Shopping item.food', item_record, self.records[food_symbol], 'GET ' + path)
            self.rtv.observe_link('Shopping item.unit', item_record, self.records[unit_symbol], 'GET ' + path)
            item_refs = item.get('recipeReferences') or []
            require(item_refs, 'Shopping item has no observed recipe provenance.')
            for ref in item_refs:
                require(ref.get('shoppingListItemId') == item_id and ref.get('recipeId') in expected_recipes, 'Item-recipe link endpoints differ.')
                observed_recipes.add(ref['recipeId'])
                target = expected_recipes[ref['recipeId']]
                require(food_symbol in FOODS[target], 'Item recipe provenance does not use this food.')
                link = self.rtv.observe('Item-recipe link', symbol + ':' + ref['id'], self.scope,
                    {'id': identity_uuid(ref.get('id'), 'Item-recipe link.id')}, 'GET ' + path)
                self.rtv.observe_link('Shopping item.link', item_record, link, 'GET ' + path)
                self.rtv.observe_link('Item-recipe link.recipe', link, self.records[target], 'GET ' + path)
        require(observed_foods == set(expected_foods), 'Expected shared foods are missing from list items.')
        require(observed_recipes == set(expected_recipes), 'Expected recipe provenance is missing from list items.')

    def run(self):
        for entity, symbols in [('Food', ['F1', 'F2', 'F3']), ('Unit', ['Q1', 'Q2']),
                ('Category', ['C1', 'C2']), ('Tag', ['T1', 'T2'])]:
            for symbol in symbols:
                self.create_collection(entity, symbol)
        for symbol in ('R1', 'R2', 'R3'):
            self.configure_recipe(symbol)
        for symbol, recipes in LISTS.items():
            self.create_collection('Shopping list', symbol)
            for recipe in recipes:
                path = COLLECTIONS['Shopping list'] + '/' + self.objects[symbol]['id'] + '/recipe/' + self.objects[recipe]['id']
                self.client.link_paths.add(path)
                self.client.call('POST', path, {'recipeIncrementQuantity': 1})
            self.inspect_list(symbol)

def previous_identity(root):
    paths = sorted((root / 'runs').glob('identity-*/acceptance.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    require(paths, 'Run identity acceptance first.')
    prior = json.loads(paths[0].read_text(encoding='utf-8-sig'))
    require(prior.get('result') == 'M1_IDENTITY_ACCEPTANCE_PASS', 'Latest identity acceptance did not pass.')
    return prior

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True); parser.add_argument('--username', default='changeme@example.com')
    parser.add_argument('--review-zip', required=True)
    args = parser.parse_args(); root = Path(args.root)
    run_id = 'fixture-' + datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    output = root / 'runs' / run_id; output.mkdir(parents=True)
    report = {'result': 'M3_SERIAL_FIXTURE_NOT_ACCEPTED', 'run_id': run_id, 'reset_replay_validated': False,
        'provengo_executed': False, 'cycle_links_tested': False, 'ready_for_schedule_exploration': False}
    pilot = None; exit_code = 1
    try:
        base, digest = check_contract(root); prior = previous_identity(root)
        require(sys.stdin.isatty(), 'Run in an interactive terminal for hidden password input.')
        client = FixtureClient(base, output)
        password = getpass.getpass('Mealie password (hidden): ')
        try:
            identity_report, runtime = accepted_observations(client, args.username, password, run_id)
        finally:
            password = None
        require(identity_report['scope'] == prior['scope'] and identity_report['user_id'] == prior['user_id'], 'Current actor or scope differs from the accepted identity.')
        prefix = 'mealie-sbt-' + uuid.uuid4().hex[:12]
        report.update({'prefix': prefix, 'contract_sha256': digest, 'base_url': base})
        pilot = Pilot(client, runtime, prefix)
        print('Creating one serial fixture with prefix: ' + prefix)
        pilot.run()
        report.update({'result': 'M3_SERIAL_FIXTURE_ACCEPTANCE_PASS', 'fixtures_validated': True,
            'base_resource_count': len(pilot.objects), 'instance_count': len(pilot.rtv.records),
            'observed_link_count': len(pilot.rtv.edges), 'fixture_request_count': len(client.trace),
            'shared_resource_topology': {'recipe_foods': FOODS, 'recipe_categories': CATEGORIES, 'recipe_tags': TAGS, 'shopping_list_recipes': LISTS}})
        exit_code = 0
    except (AcceptanceError, OSError, ValueError, KeyError, TypeError):
        error = sys.exc_info()[1]
        report['failure'] = str(error) if isinstance(error, AcceptanceError) else 'Fixture configuration or response shape was not accepted. Inspect the trace.'
    finally:
        if pilot is not None:
            (output / 'rtv.json').write_text(json.dumps(pilot.rtv.export(), indent=2) + '\n', encoding='utf-8')
            (output / 'owned-resources.json').write_text(json.dumps({k: {'id': v.get('id'), 'slug': v.get('slug'), 'name': v.get('name')} for k, v in pilot.objects.items()}, indent=2) + '\n', encoding='utf-8')
        (output / 'acceptance.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        review = Path(args.review_zip); review.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(review, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in output.glob('*.json'):
                archive.write(path, path.name)
    print(report['result'])
    if 'failure' in report:
        print(report['failure'])
    print('Review ZIP: ' + str(review))
    print('No automatic retry, rollback, deletion or reset was performed.')
    return exit_code

if __name__ == '__main__':
    sys.exit(main())
