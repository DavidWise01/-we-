import tempfile,unittest
import test_rsi010
from rsi011 import Anchor,canonical
from cryptography.exceptions import InvalidSignature
class Tests(unittest.TestCase):
 def setUp(self):
  self.b=test_rsi010.Tests();self.b.setUp();self.path=self.b.tmp.name+'/anchor';self.a=Anchor(self.path,'jane-test',self.b.wp)
 def tearDown(self):self.a.close();self.b.tearDown()
 def seal(self):self.b.add();h,s=self.b.seal();self.a.publish(h,s);return h,s
 def test_recall(self):self.seal();self.assertEqual(len(self.a.recall(self.b.b,0)),1)
 def test_stale(self):old=self.seal();self.seal();self.assertRaises(ValueError,self.a.publish,*old)
 def test_forgery(self):h,s=self.seal();s['0']=s['1'];self.assertRaises(InvalidSignature,self.a.publish,h,s)
 def test_missing_anchor(self):self.assertRaises(ValueError,self.a.recall,self.b.b,0)
 def test_rollback_hold(self):
  self.seal();self.seal();self.b.b.db.execute('DELETE FROM signed WHERE seq=1');self.b.b.db.execute('DELETE FROM frames WHERE t=1');self.assertRaises(ValueError,self.a.recall,self.b.b,0);self.assertTrue(self.a.held())
 def test_restart_hold(self):
  self.test_rollback_hold();self.a.close();self.a=Anchor(self.path,'jane-test',self.b.wp);self.assertTrue(self.a.held());self.assertRaises(ValueError,self.a.recall,self.b.b,0)
 def test_hold_publish(self):self.test_rollback_hold();self.assertRaises(ValueError,self.a.publish,*self.b.seal())
 def test_same_height_fork(self):
  h,s=self.seal();h['frames'][1]='f'*64;s={i:k.sign(canonical(h).encode()).hex() for i,k in self.b.w.items()};self.assertRaises(ValueError,self.a.publish,h,s)
 def test_idempotent(self):h,s=self.seal();self.a.publish(h,s);self.assertFalse(self.a.held())
 def test_pin(self):self.assertRaises(ValueError,Anchor,self.path,'other',self.b.wp)
if __name__=='__main__':unittest.main()
