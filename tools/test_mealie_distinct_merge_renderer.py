"""Contract/renderer acceptance without server requests or a native JAR."""
import json,os,sys,unittest
from pathlib import Path
ROOT=Path(os.environ.get('MEALIE_TEST_ROOT',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(ROOT/'generic-generator'))
from generator_v56.pipeline import run_pipeline
from render_native_distinct_merge import render

class RendererTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract=ROOT/'generic-generator/compatibility/contracts/mealie.json'
        cls.doc=json.loads(cls.contract.read_text(encoding='utf-8-sig'))
        cls.plan=run_pipeline(str(cls.contract),'mealie','http://127.0.0.1:9925',123,include_resource_maps=True).plan
        cls.policy=json.loads((ROOT/'profiles/mealie-native-merge-policy.json').read_text(encoding='utf-8-sig'))
    def model(self,scenario,policy=None):
        return render(self.plan,self.doc,'http://127.0.0.1:9925','sbt-test','api/households/shopping/lists','api/households/shopping/items',['api/foods','api/units'],policy or self.policy,scenario)
    def test_distinct_ready_parents(self):
        interfaces,stories,manifest=self.model('distinct')
        self.assertIn('multi.data.parents[0]',stories);self.assertIn('multi.data.parents[1]',stories)
        self.assertIn('parents.length<2',stories);self.assertNotIn('function depMergeAdd',interfaces)
        self.assertEqual(len(manifest['workers']),6)
    def test_http_only_in_interfaces(self):
        interfaces,stories,_=self.model('merge')
        self.assertNotIn('svc.',stories);self.assertNotIn('new RESTSession',stories)
        self.assertNotIn('pvg.rtv.get',stories)
        self.assertIn('function depMergeReadback',interfaces)
    def test_merge_waits_final_verification(self):
        interfaces,stories,manifest=self.model('merge')
        self.assertIn('e.name==="SBT:FinalVerified"',stories)
        self.assertIn('MERGE_PERSISTED_STATE_MISMATCH',interfaces)
        self.assertIn('MERGE_PARENT_VIEW_MISMATCH',interfaces)
        self.assertIn('depVerifychild2update();depMembershipchild2();',stories)
        self.assertEqual(manifest['merge_policy']['added_quantity'],2)
    def test_policy_contract_guard(self):
        policy=dict(self.policy,quantity_field='unknownQuantity')
        with self.assertRaises(ValueError):self.model('merge',policy)

if __name__=='__main__':unittest.main()
