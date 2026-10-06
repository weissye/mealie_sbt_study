"""Offline architecture checks against the installed, pinned Mealie contract."""
import argparse,sys,unittest
from pathlib import Path
from render_native_dependency_acceptance import render
from run_mealie_generator_live import auth_overlay

ROOT=None
class RendererTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0,str(ROOT/'generic-generator'))
        from generator_v56.pipeline import run_pipeline
        cls.plan=run_pipeline(str(ROOT/'generic-generator/compatibility/contracts/mealie.json'),'mealie','http://127.0.0.1:9925',203).plan
    def model(self):return render(self.plan,'http://127.0.0.1:9925','offline-fixture','api/households/shopping/lists','api/households/shopping/items')
    def test_http_confined_to_interfaces(self):
        interfaces,stories,_=self.model();self.assertNotIn('svc.',stories);self.assertIn('svc.post(',interfaces);self.assertNotIn('/sbt/step/',interfaces)
    def test_workers_and_independent_verifiers(self):
        _,stories,manifest=self.model();self.assertEqual(stories.count('bthread("crud:'),4);self.assertEqual(stories.count('bthread("verify:'),8);self.assertEqual(len(manifest['workers']),4)
    def test_dependency_has_contract_provenance(self):
        _,stories,manifest=self.model();self.assertTrue(manifest['dependency']['provenance']);self.assertEqual(manifest['dependency']['field'],'shoppingListId');self.assertIn('SBT:ChildWaiting',stories);self.assertIn('SBT:DependencyReady',stories)
    def test_unsupported_or_ambiguous_dependency_rejected(self):
        with self.assertRaises(ValueError):render(self.plan,'http://local','fixture','api/organizers/tags','api/households/shopping/items')
    def test_native_runtime_access_only_inside_callbacks(self):
        interfaces,stories,_=self.model();self.assertNotIn('pvg.rtv',stories);self.assertNotIn('depPrepare',interfaces)
    def test_no_delete_and_raw_response_capture(self):
        interfaces,_,_=self.model();self.assertNotIn('svc.delete(',interfaces);self.assertIn('DEPENDENCY_RECEIPT',interfaces);self.assertIn('Parent membership readback mismatch',interfaces)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args();ROOT=args.root.resolve();unittest.main(argv=[sys.argv[0]])
