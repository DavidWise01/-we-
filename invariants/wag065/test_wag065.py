import unittest
from wag065 import CutAudit,Witness,demo
def new():return CutAudit([Witness('W1','A'),Witness('W2','B'),Witness('W3','C')])
class Tests(unittest.TestCase):
 def setUp(self):self.a=new()
 def test_demo(self):self.assertEqual(demo()[1][-1],'CONNECTED_REDUNDANT')
 def test_ledger(self):self.assertTrue(demo()[0].verify())
 def test_five_records(self):self.assertEqual(len(demo()[0].events),5)
 def test_three_edges(self):self.assertEqual(len(self.a.edges),3)
 def test_cut_number(self):self.assertEqual(self.a.minimum_edge_cut(),2)
 def test_initial_paths(self):self.assertEqual(len(self.a.paths('W1','W2')),2)
 def test_one_cut_connected(self):self.a.cut('W1','W2');self.assertTrue(self.a.connected())
 def test_one_cut_state(self):self.a.cut('W1','W2');self.assertEqual(self.a.state(),'CONNECTED_DEGRADED')
 def test_one_cut_single_path(self):self.a.cut('W1','W2');self.assertEqual(len(self.a.paths('W1','W2')),1)
 def test_two_cut_disconnected(self):self.a.cut('W1','W2');self.a.cut('W1','W3');self.assertFalse(self.a.connected())
 def test_two_cut_hold(self):self.a.cut('W1','W2');self.a.cut('W1','W3');self.assertEqual(self.a.state(),'HOLD_DISCONNECTED')
 def test_two_cut_no_path(self):self.a.cut('W1','W2');self.a.cut('W1','W3');self.assertEqual(self.a.paths('W1','W2'),[])
 def test_repair(self):self.a.cut('W1','W2');self.a.repair('W1','W2');self.assertEqual(self.a.state(),'CONNECTED_REDUNDANT')
 def test_no_root_loss(self):self.a.cut('W1','W2');self.assertEqual({w.root for w in self.a.ws},{'A','B','C'})
 def test_dup_root(self):
  with self.assertRaises(ValueError):CutAudit([Witness('W1','A'),Witness('W2','A'),Witness('W3','C')])
 def test_dup_witness(self):
  with self.assertRaises(ValueError):CutAudit([Witness('W1','A'),Witness('W1','B'),Witness('W3','C')])
 def test_too_few(self):
  with self.assertRaises(ValueError):CutAudit([Witness('W1','A'),Witness('W2','B')])
 def test_unknown_endpoint(self):
  with self.assertRaises(ValueError):self.a.cut('W1','W4')
 def test_self_link(self):
  with self.assertRaises(ValueError):self.a.cut('W1','W1')
 def test_duplicate_cut(self):
  self.a.cut('W1','W2')
  with self.assertRaises(ValueError):self.a.cut('W1','W2')
 def test_duplicate_repair(self):
  with self.assertRaises(ValueError):self.a.repair('W1','W2')
 def test_atomic_failure(self):
  n=len(self.a.events)
  with self.assertRaises(ValueError):self.a.cut('W1','unknown')
  self.assertEqual(n,len(self.a.events))
 def test_tampering(self):
  self.a.cut('W1','W2');self.a.events[1]['data'][0]='fake';self.assertFalse(self.a.verify())
 def test_each_two_cut_disconnects(self):
  from itertools import combinations
  for pair in combinations(self.a.full,2):self.assertFalse(self.a.connected(self.a.full.difference(pair)))
if __name__=='__main__':unittest.main()
