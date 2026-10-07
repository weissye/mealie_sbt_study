import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from generator_v56.render.context_observation import generate

ROOT = Path(__file__).resolve().parents[1]


class GenerationTests(unittest.TestCase):
    def test_regeneration_and_partition(self):
        with tempfile.TemporaryDirectory() as temp:
            a = Path(temp) / 'a/spec/js'
            b = Path(temp) / 'b/spec/js'
            for out in (a, b):
                generate(ROOT / 'model/fixture-openapi.json', out, 'http://127.0.0.1:1')
            for name in ('dal.js', 'stories.observation.js', 'interfaces.observation.js', 'generation_report.json'):
                self.assertEqual((a / name).read_bytes(), (b / name).read_bytes())
            stories = (a / 'stories.observation.js').read_text()
            self.assertNotIn('RESTSession', stories)
            self.assertIn('ctx.bthread', stories)
            self.assertIn('waitFor(verifiedEvent(2))', stories)
            self.assertIn('Observation.Pending', stories)
            interfaces = (a / 'interfaces.observation.js').read_text()
            self.assertIn("pvg.rtv.get('BASELINE')", interfaces)
            self.assertIn('response.code', interfaces)

    def test_contract_response_and_example_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'spec/js'
            document = json.loads((ROOT / 'model/fixture-openapi.json').read_text())
            document['paths']['/resources']['post']['responses'] = {'202': {'description': 'Accepted'}}
            document['paths']['/resources']['post']['requestBody']['content']['application/json']['example'] = {'name': 'different'}
            contract = Path(temp) / 'contract.json'
            contract.write_text(json.dumps(document))
            generate(contract, out, 'http://127.0.0.1:1')
            plan = json.loads((out / 'generation_report.json').read_text())['plan']
            self.assertEqual(plan['create']['codes'], [202])
            self.assertEqual(plan['initial'], {'name': 'different'})

    def test_existing_output_and_external_target_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'spec/js'
            generate(ROOT / 'model/fixture-openapi.json', out, 'http://127.0.0.1:1')
            with self.assertRaises(ValueError):
                generate(ROOT / 'model/fixture-openapi.json', out, 'http://127.0.0.1:1')
            with self.assertRaises(ValueError):
                generate(ROOT / 'model/fixture-openapi.json', Path(temp) / 'other/spec/js', 'https://example.com')


if __name__ == '__main__':
    unittest.main()
