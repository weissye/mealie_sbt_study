import unittest
from pathlib import Path
from audit_mealie_generator_native import audit_events, native_command

class NativeAcceptanceTests(unittest.TestCase):
    def test_complete_symbolic_worker_is_not_live_proof(self):
        events = [{'name':'SBT:CrudStep','data':{'owner':'x','stage':'create'}},
                  {'name':'SBT:CrudVerified','data':{'owner':'x','stage':'create'}},
                  {'name':'SBT:WorkerFinished','data':{'owner':'x','reason':'complete'}}]
        report = audit_events([events], ['x'])
        self.assertEqual(report['status'], 'NATIVE_SYMBOLIC_WORKERS_COMPLETE')
        self.assertFalse(report['runtime_verifiers_evaluated'])
        self.assertEqual(report['bugs_reproduced'], 0)
    def test_truncated_worker_rejected(self):
        self.assertEqual(audit_events([[]], ['x'])['status'], 'NATIVE_SYMBOLIC_INCOMPLETE')
    def test_verifier_without_action_rejected(self):
        event = {'name':'SBT:CrudVerified','data':{'owner':'x','stage':'create'}}
        self.assertTrue(audit_events([[event]], ['x'])['errors'])
    def test_native_command_cannot_replay(self):
        command = native_command(Path('p.jar'),Path('project'),Path('samples.json'),600)
        self.assertIn('sample', command)
        self.assertNotIn('run', command)
    def test_runtime_token_is_redacted_everywhere(self):
        from run_mealie_generator_live import redact
        log="RTV: setting 'mealie_acceptance_token' to 'secret-token'\nBearer secret-token"
        self.assertNotIn('secret-token',redact(log,[]))

if __name__ == '__main__':
    unittest.main()
