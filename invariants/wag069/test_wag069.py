import unittest
from wag069 import RecoveryGate,Witness,demo
def make():
 ws=(Witness('W1','A','opA','fdA','router-a'),Witness('W2','B','opB','fdB','router-b'),Witness('W3','C','opC','fdC','router-c'))
 g={'power-y':(), 'network-x':('power-y',),'router-a':('network-x',),'router-b':('network-x',),'power-z':(), 'router-c':('power-z',)}
 return RecoveryGate(ws,g)
class TestRecovery(unittest.TestCase):
 def setUp(self):self.a=make()
 def fail(self):self.a.fail('power-y')
 def restore(self):
  self.fail()
  for n in ('power-y','network-x','router-a','router-b'):
   self.a.repair(n);self.a.verify(n,'verify-'+n)
 def test_01_initial_hold(self):self.assertEqual(self.a.status(),'HOLD_FRESH_ATTESTATIONS')
 def test_02_initial_alive(self):self.assertEqual(len(self.a.available_witnesses()),3)
 def test_03_cascade(self):self.assertEqual(self.a.dependent_closure({'power-y'}),{'power-y','network-x','router-a','router-b'})
 def test_04_other_cascade(self):self.assertEqual(self.a.dependent_closure({'power-z'}),{'power-z','router-c'})
 def test_05_fail_hold(self):self.fail();self.assertEqual(self.a.status(),'HOLD_UPSTREAM_OR_NODE_FAILURE')
 def test_06_fail_survivor(self):self.fail();self.assertEqual(self.a.available_witnesses(),{'W3'})
 def test_07_fail_count(self):self.fail();self.assertEqual(len(self.a.broken),4)
 def test_08_bad_early_router(self):
  self.fail()
  with self.assertRaises(ValueError):self.a.repair('router-a')
 def test_09_bad_early_network(self):
  self.fail()
  with self.assertRaises(ValueError):self.a.repair('network-x')
 def test_10_upstream_verify_first(self):
  self.fail();self.a.repair('power-y')
  with self.assertRaises(ValueError):self.a.repair('network-x')
 def test_11_verify_failed(self):
  self.fail()
  with self.assertRaises(ValueError):self.a.verify('network-x','x')
 def test_12_bad_evidence(self):
  self.fail();self.a.repair('power-y')
  with self.assertRaises(ValueError):self.a.verify('power-y','')
 def test_13_verify_power(self):self.fail();self.a.repair('power-y');self.a.verify('power-y','x');self.assertIn('power-y',self.a.verified)
 def test_14_restore_hold(self):self.restore();self.assertEqual(self.a.status(),'HOLD_FRESH_ATTESTATIONS')
 def test_15_restore_survivors(self):self.restore();self.assertEqual(len(self.a.available_witnesses()),3)
 def test_16_attest_too_early(self):
  self.fail()
  with self.assertRaises(ValueError):self.a.attest('W1','x')
 def test_17_one_receipt_hold(self):self.restore();self.a.attest('W1','x');self.assertEqual(self.a.status(),'HOLD_FRESH_ATTESTATIONS')
 def test_18_three_receipts(self):
  self.restore()
  for w in ('W1','W2','W3'):self.a.attest(w,w)
  self.assertEqual(self.a.status(),'LOCAL_DECLARED_QUORUM_ACCEPTED')
 def test_19_duplicate_receipt(self):
  self.restore();self.a.attest('W1','same')
  with self.assertRaises(ValueError):self.a.attest('W2','same')
 def test_20_duplicate_witness(self):
  self.restore();self.a.attest('W1','a')
  with self.assertRaises(ValueError):self.a.attest('W1','b')
 def test_21_unknown_witness(self):
  self.restore()
  with self.assertRaises(ValueError):self.a.attest('no','x')
 def test_22_new_failure_invalidates_receipts(self):
  self.restore()
  for w in ('W1','W2','W3'):self.a.attest(w,w)
  self.a.fail('power-z');self.assertEqual(self.a.receipts,{})
 def test_23_topological_order(self):self.assertLess(self.a.order.index('power-y'),self.a.order.index('router-a'))
 def test_24_cycle(self):
  with self.assertRaises(ValueError):RecoveryGate(self.a.witnesses,{'router-a':('router-b',),'router-b':('router-a',),'router-c':()})
 def test_25_missing_dependency(self):
  with self.assertRaises(ValueError):RecoveryGate(self.a.witnesses,{'router-a':('missing',),'router-b':(),'router-c':()})
 def test_26_duplicate_ancestor(self):
  ws=list(self.a.witnesses);ws[1]=Witness('W2','A','opB','fdB','router-b')
  with self.assertRaises(ValueError):RecoveryGate(ws,self.a.dependencies)
 def test_27_duplicate_domain(self):
  ws=list(self.a.witnesses);ws[1]=Witness('W2','B','opB','fdA','router-b')
  with self.assertRaises(ValueError):RecoveryGate(ws,self.a.dependencies)
 def test_28_unknown_failure(self):
  with self.assertRaises(ValueError):self.a.fail('unknown')
 def test_29_duplicate_failure(self):
  self.fail()
  with self.assertRaises(ValueError):self.a.fail('power-y')
 def test_30_bad_repair(self):
  with self.assertRaises(ValueError):self.a.repair('router-a')
 def test_31_tamper(self):self.fail();self.a.ledger[1]['data']['origin']='tampered';self.assertFalse(self.a.audit_ok())
 def test_32_demo_valid(self):self.assertTrue(demo()[1]['valid'])
 def test_33_demo_records(self):self.assertEqual(demo()[1]['records'],13)
 def test_34_demo_final(self):self.assertEqual(demo()[1]['final'],'LOCAL_DECLARED_QUORUM_ACCEPTED')
 def test_35_ancestors_kept(self):self.fail();self.assertEqual({w.ancestor for w in self.a.witnesses},{'A','B','C'})
 def test_36_atomic_rejection(self):
  self.fail();n=len(self.a.ledger)
  with self.assertRaises(ValueError):self.a.repair('router-a')
  self.assertEqual(len(self.a.ledger),n)
if __name__=='__main__':unittest.main()
