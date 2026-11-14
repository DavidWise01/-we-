import unittest
from wag045 import BoundaryAuditor,Trial,demonstration

class Tests(unittest.TestCase):
    def setUp(self):
        self.a=BoundaryAuditor(('sensor','calibration'),min_per_group=2,min_gap=.4)
    def add(self,phase,calib,s,idx):
        self.a.add(Trial('p'+str(idx),'r'+str(idx),phase,('S100',calib),s))
    def train(self):
        for i in range(4):self.add('discovery','old',1,10+i)
        for i in range(4):self.add('discovery','new',0,20+i)
        self.a.discover()
    def test_demo(self):
        a,d=demonstration()
        self.assertEqual(d,'BOUNDARY_SUPPORTED')
        self.assertEqual(a.frozen['fields'],('calibration',))
        self.assertTrue(a.verify())
    def test_freeze(self):
        self.train();self.assertEqual(self.a.frozen['fields'],('calibration',))
    def test_no_holdout_before_freeze(self):
        with self.assertRaises(ValueError):self.add('holdout','old',1,1)
    def test_no_discovery_after_freeze(self):
        self.train()
        with self.assertRaises(ValueError):self.add('discovery','old',1,99)
    def test_validate_support(self):
        self.train()
        for i in range(4):
            self.add('holdout','old',1,30+i)
            self.add('holdout','new',0,40+i)
        self.assertEqual(self.a.validate(),'BOUNDARY_SUPPORTED')
    def test_validate_unresolved(self):
        self.train()
        for i in range(4):
            self.add('holdout','old',1,30+i)
            self.add('holdout','new',1,40+i)
        self.assertEqual(self.a.validate(),'UNRESOLVED')
    def test_no_holdout_data(self):
        self.train();self.assertEqual(self.a.validate(),'UNRESOLVED')
    def test_duplicate_packet(self):
        self.add('discovery','old',1,1)
        with self.assertRaises(ValueError):
            self.a.add(Trial('p1','other','discovery',('S100','new'),0))
    def test_reused_root(self):
        self.add('discovery','old',1,1)
        with self.assertRaises(ValueError):
            self.a.add(Trial('other','r1','discovery',('S100','new'),0))
    def test_invalid_binary(self):
        with self.assertRaises(ValueError):self.add('discovery','old',2,1)
    def test_invalid_context(self):
        with self.assertRaises(ValueError):
            self.a.add(Trial('p','r','discovery',('S100',),1))
    def test_invalid_phase(self):
        with self.assertRaises(ValueError):
            self.a.add(Trial('p','r','future',('S100','old'),1))
    def test_empty_feature(self):
        with self.assertRaises(ValueError):BoundaryAuditor(())
    def test_invalid_gap(self):
        with self.assertRaises(ValueError):BoundaryAuditor(('a',),min_gap=2)
    def test_invalid_samples(self):
        with self.assertRaises(ValueError):BoundaryAuditor(('a',),min_per_group=1)
    def test_no_feature(self):
        self.assertIsNone(self.a.discover())
    def test_repeat_freeze(self):
        self.train()
        with self.assertRaises(ValueError):self.a.discover()
    def test_rejected_atomic(self):
        n=len(self.a.ledger)
        with self.assertRaises(ValueError):self.add('holdout','old',1,1)
        self.assertEqual(n,len(self.a.ledger))
    def test_tamper(self):
        self.add('discovery','old',1,1)
        self.a.ledger[1]['data']['success']=0
        self.assertFalse(self.a.verify())
    def test_preserves_trials(self):
        a,d=demonstration()
        self.assertEqual(len(a.trials),48)
    def test_bounded_search(self):
        a=BoundaryAuditor(('a','b'),min_per_group=2,max_candidates=1)
        for i in range(4):
            a.add(Trial('p'+str(i),'r'+str(i),'discovery',('same',str(i%2)),i%2))
        self.assertIsNone(a.discover())
    def test_no_causal_claim(self):
        a,d=demonstration()
        self.assertNotIn('CAUSE',d)

if __name__=='__main__':
    unittest.main()
