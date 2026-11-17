import unittest,tempfile,sqlite3
from rsi008 import LeaseBook
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=self.tmp.name+'/db';self.b=LeaseBook(self.path)
 def tearDown(self):self.b.close();self.tmp.cleanup()
 def tick(self):return self.b.advance([4]*9,[4]*9)
 def test_first(self):self.assertEqual(self.tick()['tick'],0)
 def test_rotation(self):self.tick();self.assertEqual(self.tick()['roles']['1']['duty'],'UP')
 def test_record(self):f=self.tick();self.b.record(self.b.receipt(f,0),{'signal':4});self.assertEqual(self.b.db.execute('SELECT count(*) FROM experience').fetchone()[0],1)
 def test_replay(self):f=self.tick();r=self.b.receipt(f,0);self.b.record(r,4);self.assertRaises(sqlite3.IntegrityError,self.b.record,r,4)
 def test_expired(self):f=self.tick();self.tick();self.assertRaises(ValueError,self.b.record,self.b.receipt(f,0),4)
 def test_rest(self):f=self.tick();self.assertRaises(ValueError,self.b.record,self.b.receipt(f,1),4)
 def test_tamper(self):f=self.tick();r=self.b.receipt(f,0);r['assignment']['rank']=99;self.assertRaises(ValueError,self.b.record,r,4)
 def test_restart(self):f=self.tick();self.b.record(self.b.receipt(f,0),4);self.b.close();self.b=LeaseBook(self.path);self.assertEqual(self.tick()['tick'],1);self.assertEqual(self.b.db.execute('SELECT count(*) FROM experience').fetchone()[0],1)
 def test_bad_advance(self):self.tick();self.assertRaises(ValueError,self.b.advance,[],[]);self.assertEqual(self.tick()['tick'],1)
 def test_alert(self):f=self.b.advance([4,8,4]+[4]*6,[4]*9);self.assertEqual(f['roles']['1']['duty'],'UP');self.b.record(self.b.receipt(f,1),8)
 def test_chain(self):[self.tick() for _ in range(33)];self.assertTrue(self.b.verify())
 def test_chain_tamper(self):self.tick();self.b.db.execute("UPDATE frames SET hash='bad'");self.assertFalse(self.b.verify())
if __name__=='__main__':unittest.main()
