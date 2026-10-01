import copy
import json
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from accept_identity import accepted_observations, AcceptanceError
from create_pilot_fixture import Pilot, FixtureClient, scrub
from test_identity_acceptance import FakeClient as IdentityClient

class FixtureSimulator:
    def __init__(self, runtime):
        self.owned_paths = set(); self.link_paths = set(); self.trace = []; self.data = {}
        user = next(r for r in runtime['records'].values() if r['entity_type'] == 'User')
        self.scope = user['scope']; self.user = user['identifiers']['id']

    def call(self, method, path, payload=None):
        self.trace.append({'method': method, 'path': path})
        if method == 'GET':
            return copy.deepcopy(self.data[path])
        if method == 'PUT':
            self.data[path].update(copy.deepcopy(payload))
            return copy.deepcopy(self.data[path])
        if path == '/api/recipes':
            slug = payload['name'].lower()
            self.data[path + '/' + slug] = {'id': str(uuid.uuid4()), 'name': payload['name'], 'slug': slug,
                'groupId': self.scope['group'], 'householdId': self.scope['household'], 'userId': self.user}
            return slug
        if '/recipe/' in path:
            list_path, recipe_id = path.split('/recipe/')
            listing = self.data[list_path]
            recipe = next(v for k, v in self.data.items() if k.startswith('/api/recipes/') and v['id'] == recipe_id)
            listing['recipeReferences'].append({'id': str(uuid.uuid4()), 'shoppingListId': listing['id'], 'recipeId': recipe_id})
            for ingredient in recipe['recipeIngredient']:
                existing = next((x for x in listing['listItems'] if x['foodId'] == ingredient['food']['id'] and x['unitId'] == ingredient['unit']['id']), None)
                if existing is None:
                    existing = {'id': str(uuid.uuid4()), 'shoppingListId': listing['id'], 'groupId': self.scope['group'],
                        'householdId': self.scope['household'], 'foodId': ingredient['food']['id'],
                        'unitId': ingredient['unit']['id'], 'recipeReferences': []}
                    listing['listItems'].append(existing)
                existing['recipeReferences'].append({'id': str(uuid.uuid4()), 'shoppingListItemId': existing['id'], 'recipeId': recipe_id})
            return copy.deepcopy(listing)
        body = {'id': str(uuid.uuid4()), 'name': payload['name'], 'groupId': self.scope['group']}
        if path.endswith(('/categories', '/tags')):
            body['slug'] = payload['name'].lower()
        if path.endswith('/lists'):
            body.update({'householdId': self.scope['household'], 'userId': self.user, 'recipeReferences': [], 'listItems': []})
        self.data[path + '/' + body['id']] = body
        return copy.deepcopy(body)

class PilotFixtureTests(unittest.TestCase):
    def pilot(self):
        _, runtime = accepted_observations(IdentityClient(), 'login', 'password', 'fixture-test')
        client = FixtureSimulator(runtime)
        return Pilot(client, runtime, 'mealie-sbt-test'), client

    def test_serial_fixture_preserves_many_to_many_and_distinct_ingredient_occurrences(self):
        pilot, client = self.pilot(); pilot.run()
        self.assertEqual(14, len(pilot.objects))
        self.assertEqual(40, len(client.trace))
        runtime = pilot.rtv.export()
        ingredients = [r for r in runtime['records'].values() if r['entity_type'] == 'Recipe ingredient']
        self.assertEqual(6, len(ingredients))
        self.assertEqual(6, len({r['identifiers']['referenceId'] for r in ingredients}))
        food_incoming = [e for e in runtime['observed_edges'] if e['relation'] == 'Ingredient.food' and e['target'] == pilot.records['F1']]
        self.assertEqual(2, len(food_incoming))
        list_links = [e for e in runtime['observed_edges'] if e['relation'] == 'List-recipe link.recipe' and e['target'] == pilot.records['R2']]
        self.assertEqual(2, len(list_links))
        self.assertTrue(any(r['entity_type'] == 'Item-recipe link' for r in runtime['records'].values()))
        self.assertEqual(pilot.objects['R2']['slug'], runtime['records'][pilot.records['R2']]['identifiers']['slug'])

    def test_wrong_ingredient_binding_is_rejected_on_independent_read(self):
        pilot, client = self.pilot(); original = client.call
        def corrupt(method, path, payload=None):
            body = original(method, path, payload)
            if method == 'GET' and path.startswith('/api/recipes/') and body.get('recipeIngredient'):
                body['recipeIngredient'][0]['unit']['id'] = str(uuid.uuid4())
            return body
        client.call = corrupt
        with self.assertRaises(AcceptanceError):
            pilot.run()

    def test_missing_item_provenance_is_not_a_successful_fixture(self):
        pilot, client = self.pilot(); original = client.call
        def corrupt(method, path, payload=None):
            body = original(method, path, payload)
            if method == 'GET' and '/shopping/lists/' in path and body['listItems']:
                body['listItems'][0]['recipeReferences'] = []
            return body
        client.call = corrupt
        with self.assertRaises(AcceptanceError):
            pilot.run()

    def test_budget_and_owned_route_guards_stop_before_network_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            client = FixtureClient('http://127.0.0.1:9925', Path(directory))
            with self.assertRaises(AcceptanceError):
                client.call('DELETE', '/api/foods/unknown')
            client.owned_paths.add('/api/foods/owned'); client.trace = [{}] * 64
            with self.assertRaises(AcceptanceError):
                client.call('GET', '/api/foods/owned')

    def test_nested_secret_fields_are_excluded_from_saved_trace(self):
        body = {'id': 'keep', 'extras': {'apiKey': 'secret', 'nested': [{'password': 'secret'}]}, 'tokens': ['secret']}
        self.assertNotIn('secret', json.dumps(scrub(body)))
        self.assertEqual('keep', scrub(body)['id'])

if __name__ == '__main__':
    unittest.main()
