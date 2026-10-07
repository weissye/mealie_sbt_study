import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from generator_v56.render.context_model import build_model,generate_context_model
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/'model/mealie-openapi.v3.28.0.json'
SCOPE=['/api/foods','/api/units','/api/recipes','/api/households/shopping/lists','/api/households/shopping/items']
class ContextTests(unittest.TestCase):
 def test_actual_contract_all_item_dependencies(self):
  c,e=build_model(json.loads(CONTRACT.read_text()),SCOPE,1,1)
  item=e[-1];self.assertEqual({d['target'] for d in item['dependencies']},{'IngredientFood','IngredientUnit','Recipe','ShoppingListOut'})
  self.assertEqual(item['body'].keys(),{'note'})
  self.assertEqual(e[2]['identity_mode'],'primitive-route')
  self.assertEqual(len(e[2]['nested']),1)
  self.assertFalse(e[3]['nested'])
 def test_deterministic_generation_and_syntax_for_one_and_two_instances(self):
  for instances in (1,2):
   with tempfile.TemporaryDirectory() as t:
    a,b=Path(t)/'a',Path(t)/'b'
    for out in (a,b):generate_context_model(CONTRACT,out,'mealie','http://127.0.0.1:9925',SCOPE,instances,1)
    for filename in ('interfaces.mealie.js','dal.js','stories.mealie.js','generation_report.json'):
     self.assertEqual((a/filename).read_bytes(),(b/filename).read_bytes())
     if filename.endswith('.js'):subprocess.run(['node','--check',str(a/filename)],check=True,capture_output=True)
    stories=(a/'stories.mealie.js').read_text()
    self.assertNotIn('/api/',stories);self.assertNotIn('sbtExecuteAction',stories)
    self.assertEqual(stories.count('bthread("lifecycle '),instances*5)
 def test_ambiguous_route_is_rejected(self):
  raw=json.loads(CONTRACT.read_text());raw['paths']['/api/foods/{other}']=raw['paths']['/api/foods/{item_id}']
  with self.assertRaisesRegex(ValueError,'Ambiguous'):build_model(raw,SCOPE,1,1)
 def test_generic_renamed_resource_uses_no_application_branch(self):
  schema={'type':'object','title':'Widget','properties':{'id':{'type':'string'},'label':{'type':'string'}}}
  response={'content':{'application/json':{'schema':schema}}}
  body={'content':{'application/json':{'schema':{'type':'object','properties':{'label':{'type':'string'}},'required':['label']}}}}
  raw={'info':{'title':'Other'},'paths':{'/widgets':{'post':{'requestBody':body,'responses':{'201':response}}},'/widgets/{id}':{'get':{'responses':{'200':response}}}}}

  _,entities=build_model(raw,['/widgets'],1,1);self.assertEqual(entities[0]['name'],'Widget')
 def test_refuses_overwriting_nonempty_output(self):
  with tempfile.TemporaryDirectory() as t:
   (Path(t)/'keep').write_text('original')
   with self.assertRaisesRegex(ValueError,'empty'):generate_context_model(CONTRACT,t,'mealie','http://127.0.0.1:9925',SCOPE,1,1)
   self.assertEqual((Path(t)/'keep').read_text(),'original')
if __name__=='__main__':unittest.main()
