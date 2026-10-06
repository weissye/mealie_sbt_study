"""Reference inference must reject ambiguity and follow schema evidence, not app names."""
import copy,json,sys,unittest
from pathlib import Path
from infer_native_schema_links import infer_links

class SchemaLinksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parents[1]
        # Release lives in the study root; local tests use the supplied fixture root.
        root=Path(__import__('os').environ.get('MEALIE_TEST_ROOT',root))
        sys.path.insert(0,str(root/'generic-generator'))
        from generator_v56.pipeline import run_pipeline
        file=root/'generic-generator/compatibility/contracts/mealie.json'
        cls.doc=json.loads(file.read_text(encoding='utf-8-sig'))
        cls.plan=run_pipeline(str(file),'mealie','http://fixture',203,include_resource_maps=True).plan
    def infer(self,doc):return infer_links(doc,self.plan,'api/households/shopping/items',['api/foods','api/units'])
    def test_two_reference_backed_optional_bindings(self):
        links=self.infer(self.doc)
        self.assertEqual([x['field'] for x in links],['foodId','unitId'])
        self.assertTrue(all(x['optional'] for x in links))
    def test_field_renaming_uses_schema_not_food_keyword(self):
        doc=copy.deepcopy(self.doc);props=doc['components']['schemas']['ShoppingListItemCreate']['properties']
        props['component']=props.pop('food');props['componentId']=props.pop('foodId')
        self.assertEqual(self.infer(doc)[0]['field'],'componentId')
    def test_duplicate_reference_binding_rejected(self):
        doc=copy.deepcopy(self.doc);props=doc['components']['schemas']['ShoppingListItemCreate']['properties']
        props['other']=copy.deepcopy(props['food']);props['otherId']=copy.deepcopy(props['foodId'])
        with self.assertRaises(ValueError):self.infer(doc)
    def test_identity_format_mismatch_rejected(self):
        doc=copy.deepcopy(self.doc);doc['components']['schemas']['ShoppingListItemCreate']['properties']['unitId']['anyOf'][0]['format']='unrelated-format'
        with self.assertRaises(ValueError):self.infer(doc)
if __name__=='__main__':unittest.main()
