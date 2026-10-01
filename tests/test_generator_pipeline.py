import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from sbt_generator.pipeline import compile_model, render_interfaces, render_stories

class GeneratorPipelineTests(unittest.TestCase):
    def compile(self, contract=None, profile=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'contract.json').write_text(json.dumps(contract or self.contract))
            (root / 'profile.json').write_text(json.dumps(profile or self.profile))
            return compile_model(root / 'contract.json', root / 'profile.json')

    def setUp(self):
        self.contract = json.loads((ROOT / 'model/mealie-openapi.v3.28.0.reviewed.json').read_text())
        self.profile = json.loads((ROOT / 'profiles/mealie-pilot.json').read_text())

    def test_all_contract_operations_and_schemas_survive_normalization(self):
        model = self.compile()
        self.assertEqual(266, len(model['operations']))
        self.assertEqual(255, len(model['schemas']))
        op = model['operations'][self.profile['stories'][0]['operations']['update']['operation']]
        self.assertTrue(op['request_body']['variants'])
        self.assertTrue(op['responses'])
        self.assertTrue(op['security'])
        self.assertTrue(op['pointer'].startswith('#/paths/'))

    def test_contract_path_change_reaches_interface_without_story_http_details(self):
        contract = copy.deepcopy(self.contract)
        contract['paths']['/changed/recipes/{slug}'] = contract['paths'].pop('/api/recipes/{slug}')
        model = self.compile(contract=contract)
        self.assertIn('/changed/recipes/{slug}', render_interfaces(model))
        stories = render_stories(model)
        self.assertNotIn('/api/', stories)
        self.assertNotIn('/changed/', stories)
        self.assertNotIn('"method"', stories)
        self.assertEqual(8, stories.count('SBTInterfaces.invoke('))

    def test_missing_operation_is_rejected(self):
        profile = copy.deepcopy(self.profile)
        profile['stories'][0]['operations']['read']['operation'] = 'missing_operation'
        with self.assertRaisesRegex(ValueError, 'absent from OpenAPI'):
            self.compile(profile=profile)

    def test_unbound_path_parameter_is_rejected(self):
        profile = copy.deepcopy(self.profile)
        profile['stories'][0]['operations']['read']['bindings'] = {}
        with self.assertRaisesRegex(ValueError, 'path parameters'):
            self.compile(profile=profile)

    def test_new_story_uses_template_without_generator_changes(self):
        profile = copy.deepcopy(self.profile)
        added = copy.deepcopy(profile['stories'][0])
        added.update(name='another_owned_recipe', id_prefix='C')
        for role in added['operations'].values():
            role['bindings']['slug']['symbol'] = 'R3'
        profile['stories'].append(added)
        model = self.compile(profile=profile)
        self.assertEqual(12, sum(len(s['steps']) for s in model['stories']))
        self.assertEqual('R3', model['stories'][2]['steps'][0]['bindings']['slug']['symbol'])
