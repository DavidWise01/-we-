import unittest
from wag047 import AssignmentAudit,Subject,Observation,demonstration

class Tests(unittest.TestCase):
 def setUp(self):
  self.g=AssignmentAudit(min_per_arm=2)
  for i in range(4):self.g.register_subject(Subject(f's{i}',i%2))
  self.alloc={'s0':'control','s1':'control','s2':'intervention','s3':'intervention'}
 def freeze(self):return self.g.freeze_assignment(self.alloc)
 def obs(self,i,**changes):
  s=f's{i}';arm=self.alloc[s]
  v=dict(sid=s,assigned=arm,exposed=arm,outcome=1,tick=i+1,packet=f'p{i}',root=f'r{i}')
  v.update(changes);return Observation(**v)
 def test_demo(self):
  g,r=demonstration();self.assertEqual(r['status'],'ASSOCIATION_SUPPORTED_ASSIGNMENT_CHECKS_PASS');self.assertTrue(g.verify())
 def test_demo_numeric(self):
  _,r=demonstration();self.assertAlmostEqual(r['p_value'],.01523826236296518,places=12)
 def test_subject_registration(self):self.assertEqual(len(self.g.subjects),4)
 def test_duplicate_subject(self):
  with self.assertRaises(ValueError):self.g.register_subject(Subject('s0',0))
 def test_binary_covariate(self):
  with self.assertRaises(ValueError):self.g.register_subject(Subject('x',2))
 def test_freeze(self):self.assertEqual(len(self.freeze()),64)
 def test_repeated_freeze(self):
  self.freeze()
  with self.assertRaises(ValueError):self.g.freeze_assignment(self.alloc)
 def test_incomplete_allocation(self):
  with self.assertRaises(ValueError):self.g.freeze_assignment({'s0':'control'})
 def test_insufficient_allocation(self):
  with self.assertRaises(ValueError):self.g.freeze_assignment(dict.fromkeys(self.alloc,'control'))
 def test_no_outcome_before_freeze(self):
  with self.assertRaises(ValueError):self.g.observe(self.obs(0))
 def test_valid_observation(self):
  self.freeze();self.g.observe(self.obs(0));self.assertEqual(len(self.g.records),1)
 def test_replay_subject(self):
  self.freeze();self.g.observe(self.obs(0))
  with self.assertRaises(ValueError):self.g.observe(self.obs(0,packet='extra',root='extra'))
 def test_packet_replay(self):
  self.freeze();self.g.observe(self.obs(0))
  with self.assertRaises(ValueError):self.g.observe(self.obs(1,packet='p0'))
 def test_root_reuse(self):
  self.freeze();self.g.observe(self.obs(0))
  with self.assertRaises(ValueError):self.g.observe(self.obs(1,root='r0'))
 def test_wrong_assignment(self):
  self.freeze()
  with self.assertRaises(ValueError):self.g.observe(self.obs(0,assigned='intervention'))
 def test_invalid_outcome(self):
  self.freeze()
  with self.assertRaises(ValueError):self.g.observe(self.obs(0,outcome=2))
 def test_missing_outcomes(self):
  self.freeze();self.assertEqual(self.g.evaluate()['status'],'HOLD_MISSING_OUTCOMES')
 def test_crossover(self):
  self.freeze()
  for i in range(4):self.g.observe(self.obs(i,exposed='intervention' if i==0 else self.alloc[f's{i}']))
  self.assertEqual(self.g.evaluate()['status'],'HOLD_EXPOSURE_CROSSOVER')
 def test_baseline_imbalance(self):
  g=AssignmentAudit(min_per_arm=2,max_covariate_gap=0)
  for i in range(4):g.register_subject(Subject(f's{i}',int(i>=2)))
  g.freeze_assignment(self.alloc)
  for i in range(4):g.observe(self.obs(i))
  self.assertEqual(g.evaluate()['status'],'HOLD_BASELINE_IMBALANCE')
 def test_null_outcome(self):
  self.freeze()
  for i in range(4):self.g.observe(self.obs(i))
  self.assertEqual(self.g.evaluate()['status'],'UNRESOLVED')
 def test_tamper(self):
  self.freeze();self.g.ledger[2]['payload']['covariate']=3
  self.assertFalse(self.g.verify())
 def test_reject_atomic(self):
  self.freeze();n=len(self.g.ledger)
  with self.assertRaises(ValueError):self.g.observe(self.obs(0,tick=0))
  self.assertEqual(n,len(self.g.ledger))

if __name__=='__main__':unittest.main()
