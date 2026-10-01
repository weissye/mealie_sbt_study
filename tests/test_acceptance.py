import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from compile_maps import compile_contract, components
from rtv import RTV, IdentityConflict

SCOPE={'group':'G1','household':'H1'}
UUID='12345678-1234-4234-8234-123456789abc'

class RuntimeTests(unittest.TestCase):
    def test_coobserved_user_names_resolve_to_one_instance(self):
        r=RTV('run-1');u=r.observe('User','user_A',SCOPE,{'id':UUID,'username':'alice'},'GET self')
        v=r.observe('User','user_in_comment',SCOPE,{'id':UUID.upper()},'GET comment')
        self.assertEqual(u,v);self.assertEqual(r.resolve('User',SCOPE,'username','alice'),u)

    def test_equal_wire_uuid_does_not_merge_business_types(self):
        r=RTV('run-1');a=r.observe('User','u',SCOPE,{'id':UUID},'GET user');b=r.observe('Food','f',SCOPE,{'id':UUID},'GET food')
        self.assertNotEqual(a,b)

    def test_equal_aliases_in_different_scopes_do_not_merge(self):
        r=RTV('run-1');a=r.observe('User','u',SCOPE,{'username':'alice'},'GET user');b=r.observe('User','u',{'group':'G2','household':'H2'},{'username':'alice'},'GET user')
        self.assertNotEqual(a,b)

    def test_conflicting_primary_identity_is_transactionally_rejected(self):
        r=RTV('run-1');r.observe('User','u',SCOPE,{'id':UUID},'GET user');before=r.export()
        with self.assertRaises(IdentityConflict): r.observe('User','u',SCOPE,{'id':'22345678-1234-4234-8234-123456789abc'},'GET user')
        self.assertEqual(before,r.export())

    def test_failed_create_cannot_bind(self):
        r=RTV('run-1')
        with self.assertRaises(ValueError): r.observe('Recipe','r',SCOPE,{'id':UUID},'POST recipe',status=400)
        self.assertEqual({},r.records)

    def test_alias_rename_retires_old_alias(self):
        r=RTV('run-1');a=r.observe('User','u',SCOPE,{'id':UUID,'username':'alice'},'GET self')
        r.observe('User','u',SCOPE,{'id':UUID,'username':'alice2'},'GET self')
        self.assertEqual(a,r.resolve('User',SCOPE,'username','alice2'))
        with self.assertRaises(KeyError): r.resolve('User',SCOPE,'username','alice')

    def test_delete_invalidates_binding_but_does_not_invent_cascade(self):
        r=RTV('run-1');a=r.observe('Recipe','r',SCOPE,{'id':UUID},'GET recipe');b=r.observe('Shopping list','l',SCOPE,{'id':'list-1'},'GET list')
        r.observe_link('list-recipe',b,a,'GET list');r.mark_deleted(a,'DELETE recipe',204)
        with self.assertRaises(KeyError): r.resolve('Recipe',SCOPE,'id',UUID)
        self.assertEqual('STALE_AFTER_DELETE',r.edges[0]['state'])

class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=(ROOT/'model/mealie-openapi.reference.json').read_bytes()
        cls.spec=json.loads(cls.raw);cls.profile=json.loads((ROOT/'profiles/mealie.json').read_text())
        cls.maps=compile_contract(cls.spec,cls.profile,cls.raw)

    def test_all_schemas_operations_and_explicit_refs_preserved(self):
        m=self.maps['manifest.json'];self.assertEqual(259,m['schema_count']);self.assertEqual(266,m['operation_count']);self.assertEqual(212,m['schema_reference_count'])

    def test_release_contract_is_not_labeled_nightly_or_live_validated(self):
        release=copy.deepcopy(self.spec);release['info']['version']='v3.28.0'
        manifest=compile_contract(release,self.profile,self.raw)['manifest.json']
        self.assertNotIn('nightly',manifest['warning'].lower())
        self.assertFalse(manifest['live_server_validated'])
        self.assertEqual(0,manifest['runtime_bindings_observed'])
        self.assertIn('nightly',self.maps['manifest.json']['warning'].lower())

    def test_user_views_and_fields_have_business_types(self):
        cat=self.maps['resource_catalog.json'];self.assertEqual('User',cat['schema_aliases']['UserOut']);self.assertEqual('User',cat['schema_aliases']['UserSummary'])
        slots={(s['schema'],s['field']):s for s in cat['identity_slots']}
        self.assertEqual('User.id',slots[('UserOut','id')]['business_type']);self.assertEqual('User.id',slots[('Recipe-Output','userId')]['business_type'])

    def test_nested_user_and_recipe_identifiers_are_not_confused(self):
        op=next(o for o in self.maps['02_operation_map.json']['operations'] if o['path']=='/api/users/{id}/ratings/{slug}' and o['method']=='POST')
        slots={p['name']:p.get('business_type') for p in op['parameters']}
        self.assertEqual('User.id',slots['id']);self.assertEqual('Recipe.slug',slots['slug'])

    def test_recursive_recipe_schema_does_not_create_execution_cycle(self):
        cycles=self.maps['cycle_report.json']['components']
        cycle=next(c for c in cycles if 'Recipe-Output' in c['members'])
        self.assertFalse(cycle['mandatory_creation_cycle_proven'])
        field=next(f for f in cycle['fields'] if f['schema']=='RecipeIngredient-Output' and f['field']=='referencedRecipe')
        self.assertIn('omit optional property',field['contract_allowed_breaks']);self.assertIn('choose explicit null alternative',field['contract_allowed_breaks'])

    def test_relationship_templates_are_not_runtime_facts(self):
        m=self.maps['03_relationship_map.json'];self.assertEqual([],m['instances']);self.assertEqual([],m['observed_edges'])
        self.assertTrue(all(not x['is_creation_precondition'] and not x['is_database_fk'] for x in m['templates']))

    def test_tarjan_finds_cycle_and_ignores_acyclic_chain(self):
        self.assertEqual([['A','B']],components(['A','B','C'],[('A','B'),('B','A'),('B','C')]))

if __name__=='__main__': unittest.main()
