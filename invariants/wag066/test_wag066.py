import unittest
from wag066 import Witness,VertexQuorumAudit,demonstration
def make():return VertexQuorumAudit((Witness('W1','A','opA','fdA'),Witness('W2','B','opB','fdB'),Witness('W3','C','opC','fdC')))
class Tests(unittest.TestCase):
 def setUp(self):self.a=make()
 def test_demo(self):self.assertTrue(demonstration()[1]['verified'])
 def test_initial(self):self.assertEqual(self.a.status(),'ELIGIBLE_FOR_FRESH_ATTESTATION')
 def test_kappa(self):self.assertEqual(self.a.vertex_connectivity(),2)
 def test_single_connected(self):self.a.fail('W1');self.assertTrue(self.a.connected())
 def test_single_hold(self):self.a.fail('W1');self.assertEqual(self.a.status(),'HOLD_QUORUM_LOSS')
 def test_double_hold(self):self.a.fail('W1');self.a.fail('W2');self.assertEqual(self.a.status(),'HOLD_QUORUM_LOSS')
 def test_all_failed(self):
  for n in ('W1','W2','W3'):self.a.fail(n)
  self.assertFalse(self.a.connected())
 def test_all_single_losses(self):
  for n in ('W1','W2','W3'):
   a=make();a.fail(n);self.assertTrue(a.connected());self.assertEqual(a.status(),'HOLD_QUORUM_LOSS')
 def test_restore(self):self.a.fail('W1');self.a.restore('W1');self.assertEqual(self.a.status(),'ELIGIBLE_FOR_FRESH_ATTESTATION')
 def test_incomplete_attest(self):
  with self.assertRaises(ValueError):self.a.certify({'W1':'a','W2':'b'})
 def test_certify(self):self.assertEqual(self.a.certify({'W1':'a','W2':'b','W3':'c'}),'LOCAL_DECLARED_QUORUM_ACCEPTED')
 def test_certify_after_failure(self):
  self.a.fail('W1')
  with self.assertRaises(ValueError):self.a.certify({'W1':'a','W2':'b','W3':'c'})
 def test_duplicate_receipt(self):
  with self.assertRaises(ValueError):self.a.certify({'W1':'a','W2':'a','W3':'c'})
 def test_empty_receipt(self):
  with self.assertRaises(ValueError):self.a.certify({'W1':'a','W2':'','W3':'c'})
 def test_duplicate_ancestor(self):
  with self.assertRaises(ValueError):VertexQuorumAudit((Witness('W1','A','o1','d1'),Witness('W2','A','o2','d2'),Witness('W3','C','o3','d3')))
 def test_duplicate_operator(self):
  with self.assertRaises(ValueError):VertexQuorumAudit((Witness('W1','A','o1','d1'),Witness('W2','B','o1','d2'),Witness('W3','C','o3','d3')))
 def test_duplicate_domain(self):
  with self.assertRaises(ValueError):VertexQuorumAudit((Witness('W1','A','o1','d1'),Witness('W2','B','o2','d1'),Witness('W3','C','o3','d3')))
 def test_duplicate_name(self):
  with self.assertRaises(ValueError):VertexQuorumAudit((Witness('W1','A','o1','d1'),Witness('W1','B','o2','d2'),Witness('W3','C','o3','d3')))
 def test_policy(self):
  with self.assertRaises(ValueError):VertexQuorumAudit(make().witnesses,quorum=2)
 def test_unknown_fail(self):
  with self.assertRaises(ValueError):self.a.fail('W9')
 def test_repeat_fail(self):
  self.a.fail('W1')
  with self.assertRaises(ValueError):self.a.fail('W1')
 def test_bad_restore(self):
  with self.assertRaises(ValueError):self.a.restore('W1')
 def test_four_records(self):self.assertEqual(demonstration()[1]['records'],4)
 def test_tamper(self):self.a.fail('W1');self.a.ledger[1]['data']['name']='fake';self.assertFalse(self.a.verify_ledger())
 def test_failure_atomic(self):
  n=len(self.a.ledger)
  with self.assertRaises(ValueError):self.a.certify({})
  self.assertEqual(len(self.a.ledger),n)
 def test_ancestors_preserved(self):self.a.fail('W1');self.assertEqual({w.ancestor for w in self.a.witnesses},{'A','B','C'})
if __name__=='__main__':unittest.main()
