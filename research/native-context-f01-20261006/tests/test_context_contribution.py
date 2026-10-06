import copy,json,tempfile,unittest,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from generator_v56.render.context_model import build_model,generate_context_model
from generator_v56.render.context_contribution import infer_contribution
paths=['/api/foods','/api/units','/api/recipes','/api/households/shopping/lists','/api/households/shopping/items']
raw=json.loads((root/'model/mealie-openapi.v3.28.0.json').read_text())
class ContributionTests(unittest.TestCase):
 def test_plan_is_contract_mapped(self):
  c,entities=build_model(raw,paths,1,1);p=infer_contribution(c,entities)
  self.assertEqual(p['increment_field'],'recipeIncrementQuantity');self.assertEqual(p['child_key'],'shoppingListItemId');self.assertEqual(p['reference_scale'],'recipeScale');self.assertEqual(p['scales'],[1,0.5]);self.assertTrue(p['sources'])
 def test_ambiguous_operation_rejected(self):
  data=copy.deepcopy(raw);path='/api/households/shopping/lists/{item_id}/recipe'
  data['paths'][path+'-alternative']=copy.deepcopy(data['paths'][path]);c,e=build_model(data,paths,1,1)
  with self.assertRaisesRegex(ValueError,'unambiguous'):infer_contribution(c,e)
 def test_deterministic_new_generated_files(self):
  with tempfile.TemporaryDirectory() as tmp:
   outputs=[]
   for name in ('a','b'):
    out=Path(tmp)/name/'spec/js';generate_context_model(root/'model/mealie-openapi.v3.28.0.json',out,'mealie','http://127.0.0.1:9925',paths,1,20261006,True);outputs.append(out)
   for file in ('stories.mealie.js','interfaces.mealie.js','dal.js'):
    self.assertEqual((outputs[0]/file).read_bytes(),(outputs[1]/file).read_bytes())
   s=(outputs[0]/'stories.mealie.js').read_text();self.assertIn('whole then partial source contribution',s);self.assertNotIn('lifecycle ShoppingListItemOut_1',s)
   self.assertNotIn('requestRest(',s);self.assertIn('waitForResource("Recipe_1",3)',s);self.assertIn('Contribution.Pending',s)
   d=(outputs[0]/'dal.js').read_text();self.assertIn('amount+=q*scale',d);self.assertNotIn('response.body',d)
 def test_multiple_instances_rejected_for_bounded_pilot(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaisesRegex(ValueError,'one instance'):generate_context_model(root/'model/mealie-openapi.v3.28.0.json',Path(tmp)/'spec/js','mealie','http://127.0.0.1:9925',paths,2,1,True)
if __name__=='__main__':unittest.main()
