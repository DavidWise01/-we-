import unittest
import test_rsi010
from rsi012 import Lineage,canonical
from cryptography.exceptions import InvalidSignature
class Tests(unittest.TestCase):
 def setUp(self):
  self.b=test_rsi010.Tests();self.b.setUp();self.a=Lineage(self.b.tmp.name+'/anchor','jane-test',self.b.wp)
 def tearDown(self):self.a.close();self.b.tearDown()
 def publish(self):
  h,s=self.b.seal();self.a.publish(h,s,self.b.b);return h,s
 def test_extend(self):self.b.add();self.publish();self.b.add();self.publish();self.assertEqual(len(self.a.recall(self.b.b,0)),1)
 def test_idempotent(self):self.b.add();h,s=self.publish();self.a.publish(h,s,self.b.b)
 def test_stale(self):self.b.add();h,s=self.publish();self.b.add();self.assertRaises(ValueError,self.a.publish,h,s,self.b.b)
 def test_higher_fork(self):
  self.b.add();old,_=self.publish();db=self.b.b.db;db.execute('DELETE FROM signed');db.execute('DELETE FROM frames');f=self.b.b.advance([8]*9,[4]*9);p=self.b.b.payload(f,0,8);self.b.b.append(p,self.b.sk['0'].sign(canonical(p).encode()).hex());self.b.add();h,s=self.b.seal();self.assertGreater(h['frames'][0],old['frames'][0]);self.assertTrue(self.b.b.verify());self.assertRaises(ValueError,self.a.publish,h,s,self.b.b)
 def test_experience_fork(self):
  self.b.add();self.publish();db=self.b.b.db;db.execute('DELETE FROM signed');f=__import__('json').loads(db.execute('SELECT body FROM frames WHERE t=0').fetchone()[0]);p=self.b.b.payload(f,0,9);self.b.b.append(p,self.b.sk['0'].sign(canonical(p).encode()).hex());self.b.add();self.assertRaises(ValueError,self.publish)
 def test_forged(self):
  self.b.add();h,s=self.b.seal();s['0']=s['1'];self.assertRaises(InvalidSignature,self.a.publish,h,s,self.b.b)
 def test_hold(self):
  self.b.add();self.publish();self.b.add();self.assertRaises(ValueError,self.a.recall,self.b.b,0);self.assertRaises(ValueError,self.publish)
 def test_empty_genesis(self):self.publish();self.b.add();self.publish()
if __name__=='__main__':unittest.main()
