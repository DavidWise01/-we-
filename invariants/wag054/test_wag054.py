import unittest
from wag054 import Source,Ledger,demo
class Tests(unittest.TestCase):
 def setUp(self):
  self.a=Ledger()
  for i in range(3):self.a.source(Source('E'+str(i),('r'+str(i),),'op'+str(i),'infra'+str(i),'d'+str(i)))
  self.a.source(Source('R',('new',),'opR','infraR','domainR'))
 def abort(self):
  self.a.start('C0',('E0','E1','E2'));self.a.abort('C0','withheld')
 def test_demo(self):
  a,r=demo();self.assertEqual(r,'RECOVERY_OPEN');self.assertEqual(len(a.records),9)
 def test_chain(self):self.assertTrue(demo()[0].verify())
 def test_terminal(self):self.assertTrue(demo()[0].terminal('C1'))
 def test_initial_retained(self):
  self.abort();self.a.recover('C0','C1','R');self.assertEqual(self.a.ceremonies['C0']['state'],'ABORTED')
 def test_recovery(self):
  self.abort();self.assertEqual(self.a.recover('C0','C1','R'),'RECOVERY_OPEN')
 def test_shared_origin(self):
  self.a.source(Source('B',('r0',),'x','y','z'));self.abort();self.assertEqual(self.a.recover('C0','C1','B'),'HOLD')
 def test_shared_operator(self):
  self.a.source(Source('B',('new2',),'op0','y','z'));self.abort();self.assertEqual(self.a.recover('C0','C1','B'),'HOLD')
 def test_shared_infrastructure(self):
  self.a.source(Source('B',('new2',),'x','infra0','z'));self.abort();self.assertEqual(self.a.recover('C0','C1','B'),'HOLD')
 def test_shared_domain(self):
  self.a.source(Source('B',('new2',),'x','y','d0'));self.abort();self.assertEqual(self.a.recover('C0','C1','B'),'HOLD')
 def test_reused_source(self):
  self.abort();self.assertEqual(self.a.recover('C0','C1','E0'),'HOLD')
 def test_missing_parent(self):
  with self.assertRaises(ValueError):self.a.recover('bad','C1','R')
 def test_missing_fallback(self):
  self.abort()
  with self.assertRaises(ValueError):self.a.recover('C0','C1','bad')
 def test_no_recovery_from_open(self):
  self.a.start('C0',('E0',))
  with self.assertRaises(ValueError):self.a.recover('C0','C1','R')
 def test_no_repeat_recovery(self):
  self.abort();self.a.recover('C0','C1','R')
  with self.assertRaises(ValueError):self.a.recover('C0','C2','R')
 def test_no_recursive_recovery(self):
  self.abort();self.a.recover('C0','C1','R');self.a.abort('C1','bad')
  with self.assertRaises(ValueError):self.a.recover('C1','C2','R')
 def test_failed_terminal(self):
  self.abort();self.a.recover('C0','C1','R');self.a.close('C1',False,'unavailable');self.assertTrue(self.a.terminal('C1'))
 def test_no_double_close(self):
  self.abort();self.a.recover('C0','C1','R');self.a.close('C1',True)
  with self.assertRaises(ValueError):self.a.close('C1',True)
 def test_open_not_terminal(self):
  self.abort();self.a.recover('C0','C1','R');self.assertFalse(self.a.terminal('C1'))
 def test_duplicate_source(self):
  with self.assertRaises(ValueError):self.a.source(Source('E0',('new',),'a','b','c'))
 def test_bad_source(self):
  with self.assertRaises(ValueError):self.a.source(Source('X',(),'a','b','c'))
 def test_duplicate_start(self):
  self.a.start('C0',('E0',))
  with self.assertRaises(ValueError):self.a.start('C0',('E0',))
 def test_invalid_abort(self):
  self.a.start('C0',('E0',))
  with self.assertRaises(ValueError):self.a.abort('C0','')
 def test_atomic_rejection(self):
  n=len(self.a.records)
  with self.assertRaises(ValueError):self.a.recover('bad','C1','R')
  self.assertEqual(len(self.a.records),n)
 def test_tamper(self):
  self.a.records[1]['data']['name']='tamper';self.assertFalse(self.a.verify())
if __name__=='__main__':unittest.main()
