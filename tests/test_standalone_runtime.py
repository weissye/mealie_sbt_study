import copy
import json
import sys
import tempfile
import unittest
from unittest.mock import MagicMock
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from accept_identity import AcceptanceError, accepted_observations
from create_pilot_fixture import Pilot
from mealie_runtime_adapters import MealieAdapter, canonical_list
from run_mealie_standalone import StandaloneExecution, accepted_fixture
from sbt_generator.pipeline import compile_model
from sbt_generator.json_payload import project
from sbt_generator.runtime import TypedBindings, BoundedTransport, OperationInterfaces, load_project, verify_live_contract
from prepare_provengo_model import prepare, enumerate_orders
import test_pilot_fixture as fixture_tests
import test_provengo_model as model_tests
from test_identity_acceptance import FakeClient as IdentityClient

class FunctionalSimulator(fixture_tests.FixtureSimulator):
    def enrich(self):
        for path, listing in self.data.items():
            if '/shopping/lists/' not in path:
                continue
            for ref in listing['recipeReferences']:
                ref.update(recipeQuantity=1)
            for item in listing['listItems']:
                item.update(quantity=len(item['recipeReferences']), checked=False, note='', position=0, extras={})
                for ref in item['recipeReferences']:
                    ref.update(recipeQuantity=1, recipeScale=1, recipeNote=None)

    def call(self, method, path, payload=None):
        if method == 'POST' and path.endswith('/delete'):
            self.trace.append({'method': method, 'path': path})
            parent, recipe = path[:-len('/delete')].split('/recipe/')
            listing = self.data[parent]
            listing['recipeReferences'] = [r for r in listing['recipeReferences'] if r['recipeId'] != recipe]
            for item in listing['listItems']:
                item['recipeReferences'] = [r for r in item['recipeReferences'] if r['recipeId'] != recipe]
            listing['listItems'] = [item for item in listing['listItems'] if item['recipeReferences']]
            self.enrich()
            return copy.deepcopy(listing)
        result = super().call(method, path, payload)
        if method == 'POST' and '/recipe/' in path:
            self.enrich()
            return copy.deepcopy(self.data[path.split('/recipe/')[0]])
        return result

def generated_samples(model):
    events = {step['id']: {'name': 'SBT:Step', 'data': {**step, 'story': story['name'], 'actor': 'U1', 'mode': 'SYMBOLIC_ONLY'}}
              for story in model['stories'] for step in story['steps']}
    return [[copy.deepcopy(events[identifier]) for identifier in order] for order in enumerate_orders(model['stories'])]

class StandaloneRuntimeTests(unittest.TestCase):
    def setup_runtime(self):
        _, identity = accepted_observations(IdentityClient(), 'login', 'password', 'standalone-test')
        client = FunctionalSimulator(identity)
        pilot = Pilot(client, identity, 'mealie-sbt-test'); pilot.run(); client.enrich(); client.trace = []
        owned = {symbol: {'id': body['id'], 'name': body['name'], 'slug': body.get('slug')} for symbol, body in pilot.objects.items()}
        model = compile_model(ROOT / 'model/mealie-openapi.v3.28.0.reviewed.json', ROOT / 'profiles/mealie-pilot.json')
        contract = json.loads((ROOT / 'model/mealie-openapi.v3.28.0.reviewed.json').read_text())
        bindings = TypedBindings(identity, owned, pilot.rtv.export())
        transport = BoundedTransport(client, [])
        adapter = MealieAdapter(model, contract, owned, bindings, transport, 'standalone-test')
        link = adapter.paths['L1'] + '/recipe/' + owned['R2']['id']
        transport.allowed_pairs = {('GET', path) for path in adapter.paths.values()} | {('PUT', adapter.paths['R2']), ('POST', link), ('POST', link + '/delete')}
        interfaces = OperationInterfaces(model, bindings, transport)
        execution = StandaloneExecution(model, generated_samples(model), interfaces, adapter)
        return execution, client, adapter, bindings

    def test_generated_events_restore_semantics_refresh_ids_and_preserve_other_parent(self):
        execution, client, adapter, bindings = self.setup_runtime()
        before_ids = {item['id'] for item in client.data[adapter.paths['L1']]['listItems']}
        execution.run()
        self.assertEqual(['recipe_description', 'list_recipe_membership'], execution.accepted)
        self.assertEqual(8, len(execution.interfaces.events))
        self.assertEqual(51, len(client.trace))
        self.assertEqual(47, sum(x['method'] == 'GET' for x in client.trace))
        self.assertEqual(adapter.baseline, adapter.checkpoints[-1]['state'])
        self.assertNotEqual(before_ids, {item['id'] for item in client.data[adapter.paths['L1']]['listItems']})
        self.assertEqual(41, sum(r['state'] == 'OBSERVED' for r in bindings.rtv.records.values()))
        self.assertEqual(71, sum(e['state'] == 'OBSERVED' for e in bindings.rtv.edges))
        self.assertTrue(any(r['state'] == 'STALE_AFTER_REFRESH' for r in bindings.rtv.records.values()))

    def test_wrong_baseline_quantity_stops_before_any_mutation(self):
        execution, client, adapter, _ = self.setup_runtime()
        client.data[adapter.paths['L1']]['listItems'][0]['quantity'] = 99
        with self.assertRaisesRegex(AcceptanceError, 'baseline quantities'):
            execution.run()
        self.assertTrue(all(call['method'] == 'GET' for call in client.trace))

    def test_description_readback_mismatch_stops_without_restore_retry(self):
        execution, client, adapter, _ = self.setup_runtime()
        original = client.call
        def broken(method, path, payload=None):
            body = original(method, path, payload)
            if method == 'PUT':
                client.data[path]['description'] = 'ignored update'
            return body
        client.call = broken
        with self.assertRaisesRegex(AcceptanceError, 'Recipe readback'):
            execution.run()
        self.assertEqual(1, sum(x['method'] == 'PUT' for x in client.trace))
        self.assertEqual([], execution.accepted)

    def test_unlink_affecting_other_parent_is_detected_before_relink(self):
        execution, client, adapter, _ = self.setup_runtime()
        original = client.call
        def broken(method, path, payload=None):
            body = original(method, path, payload)
            if path.endswith('/delete'):
                client.data[adapter.paths['L2']]['listItems'][0]['quantity'] = 99
            return body
        client.call = broken
        with self.assertRaisesRegex(AcceptanceError, 'other parent L2'):
            execution.run()
        self.assertEqual(['recipe_description'], execution.accepted)
        self.assertEqual(1, sum(x['method'] == 'POST' for x in client.trace))

    def test_outside_operation_is_rejected_before_transport(self):
        _, client, _, _ = self.setup_runtime()
        transport = BoundedTransport(client, [])
        with self.assertRaises(AcceptanceError):
            transport.call('POST', '/api/recipes', {'name': 'unowned'})
        self.assertEqual([], client.trace)

    def test_historical_bindings_are_not_used_as_fresh_runtime_bindings(self):
        _, _, _, bindings = self.setup_runtime()
        with self.assertRaisesRegex(AcceptanceError, 'No fresh typed'):
            bindings.resolve({'symbol': 'R2', 'type': 'Recipe.slug'})

    def test_json_projection_handles_refs_unions_and_removes_output_properties(self):
        contract = {'components': {'schemas': {'Item': {'type': 'object', 'required': ['name'], 'properties': {'name': {'type': 'string'}, 'value': {'anyOf': [{'type': 'number'}, {'type': 'null'}]}}}}}}
        schema = {'$ref': '#/components/schemas/Item'}
        self.assertEqual({'name': 'owned', 'value': None}, project({'name': 'owned', 'value': None, 'outputOnly': 'discard'}, schema, contract))
        with self.assertRaises(AcceptanceError):
            project({'name': 7}, schema, contract)
        with self.assertRaises(AcceptanceError):
            project({'value': 2}, schema, contract)

    def sampled_project(self, root):
        model_tests.ProvengoModelTests().fixture_files(root)
        folder = prepare(root)
        model = compile_model(root / 'model/mealie-openapi.v3.28.0.reviewed.json', root / 'profiles/mealie-pilot.json')
        (folder / 'samples.json').write_text(json.dumps(generated_samples(model)))
        (folder / 'readiness.json').write_text(json.dumps({'sampleExitCode': 0}))
        return folder

    def test_sampled_source_and_complete_unique_coverage_are_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.sampled_project(root)
            _, _, registry, samples = load_project(root)
            accepted_fixture(root, registry)
            self.assertEqual(70, len(samples))

    def test_duplicate_sample_is_rejected_before_authentication(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); folder = self.sampled_project(root)
            samples = json.loads((folder / 'samples.json').read_text()); samples[1] = samples[0]
            (folder / 'samples.json').write_text(json.dumps(samples))
            with self.assertRaisesRegex(AcceptanceError, 'coverage'):
                load_project(root)

    def test_sampled_source_edit_is_rejected_before_authentication(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); folder = self.sampled_project(root)
            (folder / 'spec/js/10_stories.js').write_text('// changed')
            with self.assertRaisesRegex(AcceptanceError, 'JavaScript differs'):
                load_project(root)

    def test_live_contract_mismatch_is_rejected_without_authentication_headers(self):
        import hashlib
        client = MagicMock(); client.base = 'http://127.0.0.1:9925'
        response = client.opener.open.return_value.__enter__.return_value
        response.status = 200; response.read.return_value = b'{}'
        with self.assertRaisesRegex(AcceptanceError, 'Live server contract differs'):
            verify_live_contract(client, 'wrong')
        request = client.opener.open.call_args[0][0]
        self.assertEqual('/openapi.json', request.selector)
        self.assertIsNone(request.get_header('Authorization'))
        accepted = verify_live_contract(client, hashlib.sha256(b'{}').hexdigest())
        self.assertEqual(200, accepted['status'])

if __name__ == '__main__':
    unittest.main()
