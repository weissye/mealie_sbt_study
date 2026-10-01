import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from accept_identity import AcceptanceError, LocalClient, PINNED_HASH, accepted_observations

USER = '12345678-1234-4234-8234-123456789abc'
GROUP = '22345678-1234-4234-8234-123456789abc'
HOUSEHOLD = '32345678-1234-4234-8234-123456789abc'
SECRET = 'must-never-appear-in-evidence'

class FakeClient:
    def __init__(self):
        self.calls = []
        self.bodies = {
            '/api/auth/token': {'access_token': SECRET, 'token_type': 'bearer'},
            '/api/users/self': {'id': USER, 'username': 'actor', 'groupId': GROUP, 'groupSlug': 'home',
                'householdId': HOUSEHOLD, 'householdSlug': 'family', 'tokens': [{'token': SECRET}], 'admin': True},
            '/api/groups/self': {'id': GROUP, 'slug': 'home', 'aiProviderSettings': {'apiKey': SECRET}},
            '/api/households/self': {'id': HOUSEHOLD, 'groupId': GROUP, 'slug': 'family'}}
        self.status = 200

    def request(self, path, **kwargs):
        self.calls.append((path, kwargs))
        return self.status, copy.deepcopy(self.bodies[path])

class IdentityAcceptanceTests(unittest.TestCase):
    def test_four_requests_bind_three_instances_and_observed_links_without_secrets(self):
        client = FakeClient()
        report, runtime = accepted_observations(client, 'login', 'password-secret', 'test-run')
        self.assertEqual('M1_IDENTITY_ACCEPTANCE_PASS', report['result'])
        self.assertEqual(4, len(client.calls))
        self.assertEqual(3, len(runtime['records']))
        self.assertEqual(3, len(runtime['observed_edges']))
        self.assertFalse(report['ready_for_live_pilot'])
        serialized = json.dumps({'report': report, 'runtime': runtime})
        self.assertNotIn(SECRET, serialized)
        self.assertNotIn('password-secret', serialized)
        self.assertNotIn('aiProviderSettings', serialized)
        self.assertEqual('password-secret', client.calls[0][1]['credentials']['password'])
        self.assertTrue(all(call[1]['token'] == SECRET for call in client.calls[1:]))

    def test_scope_mismatch_does_not_create_an_accepted_registry(self):
        client = FakeClient()
        client.bodies['/api/users/self']['groupId'] = USER
        with self.assertRaises(AcceptanceError):
            accepted_observations(client, 'login', 'password', 'run')

    def test_slug_mismatch_is_rejected(self):
        client = FakeClient()
        client.bodies['/api/users/self']['householdSlug'] = 'other'
        with self.assertRaises(AcceptanceError):
            accepted_observations(client, 'login', 'password', 'run')

    def test_failed_authentication_stops_before_identity_reads(self):
        client = FakeClient(); client.status = 401
        with self.assertRaises(AcceptanceError):
            accepted_observations(client, 'login', 'password', 'run')
        self.assertEqual(1, len(client.calls))

    def test_nonlocal_urls_and_credential_urls_are_rejected(self):
        for url in ['http://example.com:9925', 'http://127.0.0.1:9925/path',
                    'http://user:password@127.0.0.1:9925', 'http://127.0.0.1:9925?x=1']:
            with self.subTest(url=url), self.assertRaises(AcceptanceError):
                LocalClient(url)
        LocalClient('http://127.0.0.1:9925')

    def test_reviewed_contract_hash_and_identity_boundary_are_preserved(self):
        raw = (ROOT / 'model/mealie-openapi.v3.28.0.reviewed.json').read_bytes()
        self.assertEqual(PINNED_HASH, hashlib.sha256(raw).hexdigest())
        spec = json.loads(raw)
        self.assertEqual('v3.28.0', spec['info']['version'])
        self.assertEqual('application/x-www-form-urlencoded', next(iter(spec['paths']['/api/auth/token']['post']['requestBody']['content'])))
        for path in ('/api/users/self', '/api/groups/self', '/api/households/self'):
            self.assertIn('get', spec['paths'][path])
        update = spec['paths']['/api/recipes/{slug}']['put']['requestBody']['content']['application/json']['schema']['$ref']
        self.assertEqual('#/components/schemas/Recipe-Input', update)

if __name__ == '__main__':
    unittest.main()
