import unittest
from wag064 import Witness,RoutingGate,demonstration
class Tests(unittest.TestCase):
 def setUp(self):
  self.g=RoutingGate([Witness('W1','a','a'),Witness('W2','b','b'),Witness('W3','c','c')])
  self.full=[list(e) for e in self.g.frozen_edges]
 def pinched(self):self.g.pinch([('W1','W2'),('W1','W3')])
 def repaired(self):self.pinched();self.g.repair([('W1','W2'),('W1','W3')])
 def test_demo(self):
  g,r=demonstration();self.assertEqual(r,'RECERTIFIED_DECLARED_WITNESSES');self.assertTrue(g.verify())
 def test_initial_connected(self):self.assertTrue(self.g.connected())
 def test_three_edges(self):self.assertEqual(len(self.g.edges),3)
 def test_cannot_certify_initial(self):
  with self.assertRaises(ValueError):self.g.certify()
 def test_distinct_ancestors(self):
  with self.assertRaises(ValueError):RoutingGate([Witness('1','a','x'),Witness('2','a','y'),Witness('3','c','z')])
 def test_distinct_domains(self):
  with self.assertRaises(ValueError):RoutingGate([Witness('1','a','x'),Witness('2','b','x'),Witness('3','c','z')])
 def test_only_three(self):
  with self.assertRaises(ValueError):RoutingGate([Witness('1','a','x')])
 def test_pinch_disconnects(self):self.pinched();self.assertFalse(self.g.connected())
 def test_pinch_holds(self):self.assertEqual(self.g.pinch([('W1','W2')])['trust'],'HOLD_SINGULAR')
 def test_double_pinch(self):
  self.pinched()
  with self.assertRaises(ValueError):self.g.pinch([('W1','W2')])
 def test_invalid_cut(self):
  with self.assertRaises(ValueError):self.g.pinch([('W1','X')])
 def test_duplicate_cut(self):
  with self.assertRaises(ValueError):self.g.pinch([('W1','W2'),('W2','W1')])
 def test_early_repair(self):
  with self.assertRaises(ValueError):self.g.repair(self.full)
 def test_partial_repair(self):
  self.pinched()
  with self.assertRaises(ValueError):self.g.repair([('W1','W2')])
 def test_repair_holds(self):self.repaired();self.assertEqual(self.g.certify(),'HOLD_QUORUM_OR_PATH')
 def test_repair_connected(self):self.repaired();self.assertTrue(self.g.connected())
 def test_duplicate_attestation(self):
  self.repaired();self.g.attest('W1',self.full,'p1')
  with self.assertRaises(ValueError):self.g.attest('W1',self.full,'p2')
 def test_duplicate_packet(self):
  self.repaired();self.g.attest('W1',self.full,'p1')
  with self.assertRaises(ValueError):self.g.attest('W2',self.full,'p1')
 def test_conflicting_edges(self):
  self.repaired()
  with self.assertRaises(ValueError):self.g.attest('W1',[('W1','W2')],'p1')
 def test_three_fresh(self):
  self.repaired()
  for i in range(1,4):self.g.attest(f'W{i}',self.full,f'p{i}')
  self.assertEqual(self.g.certify(),'RECERTIFIED_DECLARED_WITNESSES')
 def test_history(self):
  g,_=demonstration();self.assertEqual(g.events[1]['kind'],'pinch');self.assertEqual(g.events[2]['kind'],'repair')
 def test_no_recertify_twice(self):
  g,_=demonstration()
  with self.assertRaises(ValueError):g.certify()
 def test_tampering(self):
  self.pinched();self.g.events[1]['data']['connected']=True;self.assertFalse(self.g.verify())
 def test_atomic(self):
  n=len(self.g.events)
  with self.assertRaises(ValueError):self.g.pinch([('W1','X')])
  self.assertEqual(len(self.g.events),n)
if __name__=='__main__':unittest.main()
