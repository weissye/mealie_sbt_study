"""Ensure selection requires real HTTP ordering, not merely delayed lifecycle markers."""
import unittest
from run_mealie_interleaved_dependencies import interleaving_witness

READY={'name':'SBT:DependencyReady','data':{'owner':'parent:1','identity_variable':'dep_parent1_id'}}
POST={'name':'POST','data':{'body':'{"parent":"@{dep_parent1_id}"}'}}
PUT={'name':'PUT','data':{'url':'http://fixture/parents/@{dep_parent1_id}'}}
class WitnessTests(unittest.TestCase):
    def test_actual_create_between_ready_and_update(self):
        self.assertIsNotNone(interleaving_witness([READY,POST,PUT]))
    def test_delayed_crud_step_does_not_fake_interleaving(self):
        self.assertIsNone(interleaving_witness([READY,PUT,POST,{'name':'SBT:CrudStep','data':{'owner':'child:1','stage':'create'}}]))
    def test_other_parent_does_not_satisfy_witness(self):
        other={'name':'POST','data':{'body':'{"parent":"@{dep_parent2_id}"}'}}
        self.assertIsNone(interleaving_witness([READY,other,PUT]))
    def test_incomplete_schedule_has_no_witness(self):
        self.assertIsNone(interleaving_witness([READY,POST]))
if __name__=='__main__':unittest.main()
