import unittest
from wag046 import InterventionGate,Trial,demonstration

class Tests(unittest.TestCase):
 def setUp(self):
  self.g=InterventionGate();self.g.freeze()
 def trial(self,i,arm='control',success=1,context='fixed'):
  return Trial('p'+str(i),'r'+str(i),arm,success,context,1)
 def test_demo(self):
  g,r=demonstration();self.assertEqual(r['decision'],'INTERVENTION_SUPPORTED');self.assertTrue(g.verify())
 def test_24_trials(self):
  g,r=demonstration();self.assertEqual(len(g.trials),24)
 def test_fisher_value(self):
  g,r=demonstration();self.assertAlmostEqual(r['p'],0.006864988558352403,places=6)
 def test_budget(self):
  with self.assertRaises(ValueError):InterventionGate(alpha=1)
 def test_factor(self):
  with self.assertRaises(ValueError):InterventionGate(factor='')
 def test_distinct_arms(self):
  with self.assertRaises(ValueError):InterventionGate(control='v1',treatment='v1')
 def test_invalid_direction(self):
  with self.assertRaises(ValueError):InterventionGate(expected_direction='none')
 def test_minimum(self):
  with self.assertRaises(ValueError):InterventionGate(minimum=1)
 def test_no_trials_before_freeze(self):
  g=InterventionGate()
  with self.assertRaises(ValueError):g.add(self.trial(1))
 def test_no_second_freeze(self):
  with self.assertRaises(ValueError):self.g.freeze()
 def test_add_valid(self):
  self.g.add(self.trial(1));self.assertEqual(len(self.g.trials),1)
 def test_replay(self):
  self.g.add(self.trial(1))
  with self.assertRaises(ValueError):self.g.add(self.trial(1))
 def test_reused_root(self):
  self.g.add(self.trial(1))
  with self.assertRaises(ValueError):self.g.add(Trial('p2','r1','control',1,'fixed',1))
 def test_bad_arm(self):
  with self.assertRaises(ValueError):self.g.add(self.trial(1,arm='other'))
 def test_bad_binary(self):
  with self.assertRaises(ValueError):self.g.add(self.trial(1,success=2))
 def test_bad_context(self):
  with self.assertRaises(ValueError):self.g.add(self.trial(1,context='uncontrolled'))
 def test_bad_epoch(self):
  with self.assertRaises(ValueError):self.g.add(Trial('p1','r1','control',1,'fixed',-1))
 def test_insufficient(self):
  self.assertEqual(self.g.evaluate()['decision'],'HOLD_INSUFFICIENT')
 def test_no_effect(self):
  for i in range(12):
   self.g.add(self.trial(i,arm='control',success=1))
   self.g.add(self.trial(i+20,arm='treatment',success=1))
  self.assertEqual(self.g.evaluate()['decision'],'UNRESOLVED')
 def test_reverse(self):
  g=InterventionGate(expected_direction='increase');g.freeze()
  for i in range(12):
   g.add(Trial('a'+str(i),'ar'+str(i),'control',0,'fixed',1))
   g.add(Trial('b'+str(i),'br'+str(i),'treatment',1,'fixed',1))
  self.assertEqual(g.evaluate()['decision'],'INTERVENTION_SUPPORTED')
 def test_tamper(self):
  self.g.add(self.trial(1));self.g.ledger[2]['data']['success']=0;self.assertFalse(self.g.verify())
 def test_failed_atomic(self):
  n=len(self.g.ledger)
  with self.assertRaises(ValueError):self.g.add(self.trial(1,context='wrong'))
  self.assertEqual(n,len(self.g.ledger))

if __name__=='__main__':unittest.main()
