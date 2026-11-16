import unittest
from fractions import Fraction
from wag087 import *

def new():return CoverageLedger(17,{'W1':'A','W2':'B','W3':'C'})
def report(host='W1',rd='r1',challenge='n1',pos=(1,4,8),result='PASS',anc='A'):
    return AuditRecord(rd,challenge,host,anc,17,pos,result)
class Tests(unittest.TestCase):
 def setUp(self):self.l=new()
 def test_zero_missing(self):self.assertEqual(detection_fraction(17,0,3),(0,1))
 def test_all_missing(self):self.assertEqual(detection_fraction(17,17,3),(1,1))
 def test_zero_sample(self):self.assertEqual(detection_fraction(17,3,0),(0,1))
 def test_complete_sample(self):self.assertEqual(detection_fraction(17,1,17),(1,1))
 def test_one_draw(self):self.assertEqual(detection_fraction(10,2,1),(1,5))
 def test_two_draw(self):self.assertEqual(detection_fraction(10,2,2),(17,45))
 def test_full_risk(self):self.assertEqual(detection_probability(17,17,2),1)
 def test_fraction_reduced(self):self.assertEqual(detection_fraction(4,1,2),(1,2))
 def test_invalid_n(self):
  with self.assertRaises(ValueError):detection_fraction(0,0,0)
 def test_invalid_missing(self):
  with self.assertRaises(ValueError):detection_fraction(5,6,1)
 def test_invalid_k(self):
  with self.assertRaises(ValueError):detection_fraction(5,1,6)
 def test_bool_invalid(self):
  with self.assertRaises(ValueError):detection_fraction(True,1,1)
 def test_seed_deterministic(self):self.assertEqual(sample_indices(17,3,b'abcdef0123456789'),sample_indices(17,3,b'abcdef0123456789'))
 def test_seed_unique(self):self.assertEqual(len(set(sample_indices(17,10,b'abcdef0123456789'))),10)
 def test_seed_in_range(self):self.assertTrue(all(0<=i<17 for i in sample_indices(17,17,b'abcdef0123456789')))
 def test_seed_short(self):
  with self.assertRaises(ValueError):sample_indices(17,3,b'short')
 def test_seed_bad_size(self):
  with self.assertRaises(ValueError):sample_indices(17,18,b'abcdef0123456789')
 def test_empty_ledger(self):self.assertEqual(self.l.coverage('W1'),(0,17))
 def test_genesis_verify(self):self.assertTrue(self.l.verify_log())
 def test_one_audit(self):self.l.audit(report());self.assertEqual(self.l.coverage('W1'),(3,17))
 def test_repeated_positions_not_double(self):
  self.l.audit(report());self.l.audit(report(rd='r2',challenge='n2'));self.assertEqual(self.l.coverage('W1'),(3,17))
 def test_nonoverlap_coverage(self):
  self.l.audit(report());self.l.audit(report(rd='r2',challenge='n2',pos=(0,2,3)));self.assertEqual(self.l.coverage('W1'),(6,17))
 def test_cross_host_same_positions(self):
  self.l.audit(report());self.l.audit(report('W2',anc='B'));self.assertEqual(len(self.l.cross_host_union()),3)
 def test_two_host_ancestry(self):
  self.l.audit(report());self.l.audit(report('W2',anc='B'));self.assertEqual(self.l.distinct_ancestor_count(),2)
 def test_three_ancestry(self):
  for h,a in (('W1','A'),('W2','B'),('W3','C')):self.l.audit(report(h,anc=a))
  self.assertEqual(self.l.distinct_ancestor_count(),3)
 def test_wrong_root(self):
  with self.assertRaises(ValueError):self.l.audit(report(anc='X'))
 def test_unknown_host(self):
  with self.assertRaises(ValueError):self.l.audit(report(host='W9'))
 def test_invalid_positions(self):
  with self.assertRaises(ValueError):self.l.audit(report(pos=(1,1,3)))
 def test_negative_position(self):
  with self.assertRaises(ValueError):self.l.audit(report(pos=(-1,2)))
 def test_outside_position(self):
  with self.assertRaises(ValueError):self.l.audit(report(pos=(17,)))
 def test_empty_positions(self):
  with self.assertRaises(ValueError):self.l.audit(report(pos=()))
 def test_invalid_outcome(self):
  with self.assertRaises(ValueError):self.l.audit(report(result='UNKNOWN'))
 def test_failed_excluded_from_pass_coverage(self):self.l.audit(report(result='FAIL'));self.assertEqual(self.l.coverage('W1'),(0,17))
 def test_replay_challenge(self):
  self.l.audit(report())
  with self.assertRaises(ValueError):self.l.audit(report(rd='r2'))
 def test_same_round_mismatch_challenge(self):
  self.l.audit(report())
  with self.assertRaises(ValueError):self.l.audit(report('W2',challenge='n2',anc='B'))
 def test_same_round_mismatch_positions(self):
  self.l.audit(report())
  with self.assertRaises(ValueError):self.l.audit(report('W2',pos=(2,4,8),anc='B'))
 def test_same_round_same_host(self):
  self.l.audit(report())
  with self.assertRaises(ValueError):self.l.audit(report(challenge='n2'))
 def test_invalid_atomicity(self):
  before=len(self.l.log)
  with self.assertRaises(ValueError):self.l.audit(report(pos=(1,1)))
  self.assertEqual(before,len(self.l.log))
 def test_cumulative_none(self):self.assertEqual(self.l.cumulative_detection_bound('W1',3),(0,1))
 def test_cumulative_one(self):
  self.l.audit(report());self.assertEqual(self.l.cumulative_detection_bound('W1',3),detection_fraction(17,3,3))
 def test_cumulative_two(self):
  self.l.audit(report());self.l.audit(report(rd='r2',challenge='n2'))
  p=Fraction(*detection_fraction(17,3,3));q=Fraction(*self.l.cumulative_detection_bound('W1',3))
  self.assertEqual(q,1-(1-p)**2)
 def test_cumulative_failed_excluded(self):self.l.audit(report(result='FAIL'));self.assertEqual(self.l.cumulative_detection_bound('W1',3),(0,1))
 def test_cumulative_invalid_host(self):
  with self.assertRaises(ValueError):self.l.cumulative_detection_bound('W9',1)
 def test_cumulative_invalid_missing(self):
  with self.assertRaises(ValueError):self.l.cumulative_detection_bound('W1',18)
 def test_tamper_audit(self):self.l.audit(report());self.l.log[1]['payload']['host']='fake';self.assertFalse(self.l.verify_log())
 def test_demo(self):self.assertTrue(demonstration()[1]['audit_valid'])
 def test_demo_records(self):self.assertEqual(demonstration()[1]['audit_records'],7)
 def test_demo_two_rounds(self):self.assertEqual(demonstration()[1]['rounds'],2)
 def test_duplicate_host_ancestor_declared_allowed(self):
  l=CoverageLedger(5,{'W1':'A','W2':'A'});self.assertEqual(len(set(l.ancestors.values())),1)
 def test_bad_population(self):
  with self.assertRaises(ValueError):CoverageLedger(0,{'W1':'A'})
 def test_bad_hosts(self):
  with self.assertRaises(ValueError):CoverageLedger(5,{})
if __name__=='__main__':unittest.main()
