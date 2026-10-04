"""Generic opt-in route migration with native alias and referrer checks."""
import json,os,shutil,socket,subprocess,tempfile,unittest,copy
from pathlib import Path
from generator_v56.pipeline import run_pipeline
from tools.relationship_execution import audit_samples,find_receipt
from tools.route_receipts import validate_route_receipts
ROOT=Path(__file__).resolve().parents[1]
def generate(mode='rename',runtime=None,base='http://127.0.0.1:9925'):
 return run_pipeline(str(ROOT/'compatibility/contracts/mealie.json'),'native',base,220,story_profile='parallel-crud',compile_relationship_model=True,relationship_profile=json.loads((ROOT/f'profiles/mealie-route-{mode}-scope.json').read_text()),relationship_runtime=runtime or json.loads((ROOT/f'profiles/mealie-route-{mode}-runtime.json').read_text()))
class RouteConfigurationTests(unittest.TestCase):
 def test_deterministic_interfaces_only_and_three_modes(self):
  for mode in ['control','rename','reuse']:
   a=generate(mode);b=generate(mode);self.assertEqual(a.interfaces_js,b.interfaces_js);self.assertEqual(a.stories_js,b.stories_js);self.assertNotRegex(a.stories_js,r'\bsvc\.')
 def test_identity_and_timestamp_exclusions_rejected(self):
  base=json.loads((ROOT/'profiles/mealie-route-rename-runtime.json').read_text())
  for key,value in [('route_field','id'),('timestamp_fields',['createdAt']),('mode','unknown')]:
   cfg=copy.deepcopy(base);cfg['route_identity'][key]=value
   with self.assertRaises(ValueError):generate(runtime=cfg)
@unittest.skipUnless(os.environ.get('PROVENGO_TEST_JAR') and shutil.which('java'),'Native jar required')
class RouteNativeTests(unittest.TestCase):
 def test_native_aliases_referrers_and_faults(self):
  command=['java','-Xmx512m','-jar',str(Path(os.environ['PROVENGO_TEST_JAR']).resolve())]
  for mode in ['control','rename','reuse']:
   with tempfile.TemporaryDirectory() as folder:
    project=Path(folder)
    with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
    result=generate(mode,base=f'http://127.0.0.1:{port}');plan=result.resource_maps['relationship_scenario_plan'];(project/'spec/js').mkdir(parents=True);(project/'config').mkdir();(project/'config/provengo.yml').write_text('version: 2\n');(project/'spec/js/interfaces.native.js').write_text(result.interfaces_js);(project/'spec/js/stories.native.js').write_text(result.stories_js);(project/'relationship_scenario_plan.json').write_text(json.dumps(plan))
    sample=subprocess.run(command+['sample','--size','2','--max-length','700','-o','samples.json',str(project)],capture_output=True,text=True,timeout=60);self.assertEqual(sample.returncode,0,sample.stdout+sample.stderr);audit_samples(json.loads((project/'samples.json').read_text()),plan)
    faults=['','']+(['route-id-changed','route-old-retained','route-quantity','route-stale-view','route-new-missing'] if mode=='rename' else (['route-reference-migrated'] if mode=='reuse' else []))
    for i,fault in enumerate(faults):
     env=dict(os.environ,NATIVE_MOCK_PORT=str(port),NATIVE_MOCK_FAULT=fault,SBT_REL_USERNAME='local',SBT_REL_PASSWORD='local');server=subprocess.Popen(['node',str(ROOT/'tests/native_http_mock.js'),str(project)],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
     try:
      self.assertEqual(server.stdout.readline().strip(),'READY');run=subprocess.run(command+['--batch-mode','run','--run-source','samples.json','--run-id',str(2 if i==1 else 1),str(project)],env=env,capture_output=True,text=True,timeout=60);output=run.stdout+run.stderr;receipt=find_receipt(output)
      if fault:self.assertNotEqual(run.returncode,0,fault);self.assertIsNone(receipt);self.assertIn('Route identity mismatch:',output)
      else:
       self.assertEqual(run.returncode,0,'\n'.join(l for l in output.splitlines() if 'WARN [' in l or 'ERR [' in l));validate_route_receipts(receipt,plan);self.assertEqual(receipt['response_count'],result.resource_maps['relationship_compilation']['http_requests_per_complete_schedule'])
       forged=copy.deepcopy(receipt);phase=forged['route_identities'][0]['phases'][0];phase['checks'][0]['observed']['recipeIngredient'][0]['quantity']=999
       with self.assertRaises(ValueError):validate_route_receipts(forged,plan)
     finally:server.terminate();server.communicate(timeout=10)
