import unittest
from wag052 import CensoringAuditor,Attempt,fisher_two_sided,demonstration

class Tests(unittest.TestCase):
 def setUp(self):self.g=CensoringAuditor()
 def a(self,i,completed=True,outcome=1,reason='withheld'):
  return Attempt(f'a{i}',f'r{i}',completed,outcome,i,'' if completed else reason)
 def fill(self):
  for i in range(1,6):self.g.add(self.a(i,True,1))
  for i in range(6,11):self.g.add(self.a(i,False,0))
 def test_demo(self):
  g,r=demonstration();self.assertTrue(g.verify());self.assertEqual(r['status'],'SELECTION_ASSOCIATION_FLAG')
 def test_exact_p(self):
  _,r=demonstration();self.assertAlmostEqual(r['p_value'],0.00041407867494824016)
 def test_counts(self):
  _,r=demonstration();self.assertEqual((r['attempts'],r['completed'],r['aborted']),(30,20,10))
 def test_rates(self):
  _,r=demonstration();self.assertAlmostEqual(r['completed_rate'],.8);self.assertAlmostEqual(r['overall_rate'],17/30)
 def test_valid_attempt(self):self.g.add(self.a(1));self.assertEqual(len(self.g.attempts),1)
 def test_duplicate_id(self):
  self.g.add(self.a(1))
  with self.assertRaises(ValueError):self.g.add(Attempt('a1','new',True,1,2))
 def test_duplicate_root(self):
  self.g.add(self.a(1))
  with self.assertRaises(ValueError):self.g.add(Attempt('new','r1',True,1,2))
 def test_nonmonotonic(self):
  self.g.add(self.a(2))
  with self.assertRaises(ValueError):self.g.add(self.a(1))
 def test_missing_completed_outcome(self):
  with self.assertRaises(ValueError):self.g.add(self.a(1,outcome=None))
 def test_missing_abort_reason(self):
  with self.assertRaises(ValueError):self.g.add(self.a(1,False,0,''))
 def test_unknown_abort_allowed(self):self.g.add(self.a(1,False,None));self.assertEqual(len(self.g.attempts),1)
 def test_missing_bounds(self):
  self.g.add(self.a(1,True,1));self.g.add(self.a(2,False,None))
  r=self.g.evaluate();self.assertEqual(r['status'],'UNRESOLVED_MISSING_OUTCOMES');self.assertEqual(r['overall_rate_bounds'],[.5,1.])
 def test_no_abort(self):
  for i in range(1,6):self.g.add(self.a(i))
  self.assertEqual(self.g.evaluate()['status'],'UNRESOLVED_MISSING_OUTCOMES')
 def test_no_complete(self):self.assertEqual(self.g.evaluate()['status'],'UNRESOLVED_INSUFFICIENT')
 def test_empty_fisher(self):
  with self.assertRaises(ValueError):fisher_two_sided(0,0,1,1)
 def test_bad_fisher(self):
  with self.assertRaises(ValueError):fisher_two_sided(-1,2,2,2)
 def test_null(self):
  for i in range(1,6):self.g.add(self.a(i,True,1))
  for i in range(6,11):self.g.add(self.a(i,False,1))
  self.assertEqual(self.g.evaluate()['status'],'UNRESOLVED_NO_FLAG')
 def test_flag(self):self.fill();self.assertEqual(self.g.evaluate()['status'],'SELECTION_ASSOCIATION_FLAG')
 def test_evaluate_once(self):
  self.g.evaluate()
  with self.assertRaises(ValueError):self.g.evaluate()
 def test_no_append_after_close(self):
  self.g.evaluate()
  with self.assertRaises(ValueError):self.g.add(self.a(1))
 def test_invalid_policy(self):
  with self.assertRaises(ValueError):CensoringAuditor(alpha=2)
 def test_insufficient_policy(self):
  with self.assertRaises(ValueError):CensoringAuditor(min_per_group=1)
 def test_tamper(self):
  self.g.add(self.a(1));self.g.events[1]['payload']['outcome']=0;self.assertFalse(self.g.verify())
 def test_rejected_atomic(self):
  n=len(self.g.events)
  with self.assertRaises(ValueError):self.g.add(self.a(1,outcome=7))
  self.assertEqual(n,len(self.g.events))

if __name__=='__main__':unittest.main()