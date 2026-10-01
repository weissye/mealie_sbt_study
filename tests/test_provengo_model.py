import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from prepare_provengo_model import orders, model_js, prepare
from accept_identity import PINNED_HASH
import test_pilot_fixture as fixture_tests

class ProvengoModelTests(unittest.TestCase):
    def test_seventy_unique_orders_preserve_both_story_orders(self):
        sequences = orders()
        self.assertEqual(70, len(sequences))
        self.assertEqual(70, len({tuple(x) for x in sequences}))
        for sequence in sequences:
            self.assertEqual(['A1', 'A2', 'A3', 'A4'], [x for x in sequence if x.startswith('A')])
            self.assertEqual(['B1', 'B2', 'B3', 'B4'], [x for x in sequence if x.startswith('B')])

    def fixture_files(self, root):
        pilot, _ = fixture_tests.PilotFixtureTests().pilot(); pilot.run()
        folder = root / 'runs' / 'fixture-test'; folder.mkdir(parents=True)
        (root / 'profiles').mkdir()
        (root / 'profiles/mealie-pilot.json').write_bytes((ROOT / 'profiles/mealie-pilot.json').read_bytes())
        (root / 'model').mkdir()
        (root / 'model' / 'mealie-openapi.v3.28.0.reviewed.json').write_bytes((ROOT / 'model' / 'mealie-openapi.v3.28.0.reviewed.json').read_bytes())
        (folder / 'acceptance.json').write_text(json.dumps({'result': 'M3_SERIAL_FIXTURE_ACCEPTANCE_PASS', 'contract_sha256': PINNED_HASH, 'run_id': 'fixture-test'}))
        owned = {k: {'id': v['id'], 'name': v['name'], 'slug': v.get('slug')} for k, v in pilot.objects.items()}
        (folder / 'owned-resources.json').write_text(json.dumps(owned))
        (folder / 'rtv.json').write_text(json.dumps(pilot.rtv.export()))
        return folder

    def test_generated_project_uses_typed_bindings_and_has_no_http_executor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.fixture_files(root); project = prepare(root)
            plan = json.loads((project / 'model-plan.json').read_text())
            self.assertFalse(plan['runtime_executor_implemented'])
            self.assertEqual(70, plan['expected_symbolic_order_count'])
            bindings = plan['stories'][1]['steps'][0]['bindings']
            self.assertEqual('Recipe.id', bindings['recipe_id']['type'])
            self.assertEqual('Recipe.slug', plan['stories'][0]['steps'][0]['bindings']['slug']['type'])
            self.assertNotIn('@provengo summon', (project / 'spec/js/10_stories.js').read_text())
            self.assertEqual(8, model_js().count('SBTInterfaces.invoke('))

    def test_changed_fixture_identity_is_rejected_before_project_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); folder = self.fixture_files(root)
            owned = json.loads((folder / 'owned-resources.json').read_text()); owned['R2']['id'] = owned['R1']['id']
            (folder / 'owned-resources.json').write_text(json.dumps(owned))
            with self.assertRaises(ValueError):
                prepare(root)
            self.assertFalse((root / 'provengo').exists())

if __name__ == '__main__':
    unittest.main()
