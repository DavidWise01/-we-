import tempfile,unittest,os
from wag097 import Pair,Gate,head,gossip,root
class TestGossip(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
  self.log=Pair();self.ws={n:Pair() for n in ('W1','W2','W3')}
  self.p=os.path.join(self.t.name,'test.db')
  self.g=Gate(self.p,self.log.public,{n:w.public for n,w in self.ws.items()})
  self.x=[b'A',b'B',b'C']
 def observe(self,name='W1',items=None,**kw):
  items=self.x if items is None else items
  h=head(self.log,'registry-a',97,items)
  return self.g.observe(name,items,h,gossip(self.ws[name],name,h),**kw)
 def test_one(self):self.assertEqual(self.observe(),'HOLD_INCOMPLETE_GOSSIP')
 def test_three(self):
  for n in self.ws:result=self.observe(n)
  self.assertEqual(result,'LOCAL_AGREEMENT')
 def test_fork(self):
  for n in self.ws:self.observe(n)
  self.assertEqual(self.observe('W3',[b'A',b'X',b'C']),'QUARANTINE_SPLIT_VIEW')
 def test_fork_survives_restart(self):
  self.observe();self.observe('W2');self.observe('W3');self.observe('W3',[b'A',b'X',b'C'])
  self.assertEqual(Gate(self.p,self.log.public,{n:w.public for n,w in self.ws.items()}).decision(),'QUARANTINE_SPLIT_VIEW')
 def test_prefix(self):
  for n in self.ws:self.observe(n)
  old=head(self.log,'registry-a',97,self.x)
  self.assertEqual(self.observe('W1',self.x+[b'D'],old_items=self.x,old_head=old),'HOLD_INCOMPLETE_GOSSIP')
 def test_rewrite(self):
  old=head(self.log,'registry-a',97,self.x)
  self.assertEqual(self.observe('W1',[b'X',b'B',b'C',b'D'],old_items=self.x,old_head=old),'QUARANTINE_PREFIX_REWRITE')
 def test_unproven(self):
  self.observe()
  self.assertEqual(self.observe('W2',self.x+[b'D']),'HOLD_UNPROVEN_CONTINUITY')
 def test_unknown(self):
  with self.assertRaises(ValueError):self.g.observe('W4',[],{}, {})
 def test_root(self):self.assertNotEqual(root([b'A',b'B']),root([b'B',b'A']))
if __name__=='__main__':unittest.main()
