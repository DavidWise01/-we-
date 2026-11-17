import unittest,tempfile,sqlite3
from rsi009 import ExperienceBook,canonical
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=self.tmp.name+'/db';self.sk={str(i):Ed25519PrivateKey.generate() for i in range(9)};self.pk={i:k.public_key().public_bytes_raw() for i,k in self.sk.items()};self.b=ExperienceBook(self.path,self.pk)
 def tearDown(self):self.b.close();self.tmp.cleanup()
 def tick(self):return self.b.advance([4]*9,[4]*9)
 def sign(self,p,i):return self.sk[str(i)].sign(canonical(p).encode()).hex()
 def add(self):
  p=self.b.payload(self.tick(),0,{'signal':4});s=self.sign(p,0);self.b.append(p,s);return p,s
 def test_recall(self):p,s=self.add();self.tick();self.assertEqual(self.b.recall(0),[p])
 def test_restart(self):p,s=self.add();self.b.close();self.b=ExperienceBook(self.path,self.pk);self.assertEqual(self.b.recall(0),[p])
 def test_replay(self):p,s=self.add();self.assertRaises(sqlite3.IntegrityError,self.b.append,p,s)
 def test_stale(self):p,s=self.add();self.tick();self.assertRaises(ValueError,self.b.append,p,s)
 def test_forged(self):p=self.b.payload(self.tick(),0,4);self.assertRaises(InvalidSignature,self.b.append,p,self.sign(p,1))
 def test_rest(self):p=self.b.payload(self.tick(),1,4);self.assertRaises(ValueError,self.b.append,p,self.sign(p,1))
 def test_tamper(self):self.add();self.b.db.execute("UPDATE signed SET body='{}'");self.assertFalse(self.b.verify())
 def test_key_pin(self):bad=dict(self.pk);bad['0']=Ed25519PrivateKey.generate().public_key().public_bytes_raw();self.assertRaises(ValueError,ExperienceBook,self.path,bad)
 def test_unsigned(self):self.assertRaises(ValueError,self.b.record,{},4)
 def test_other_identity(self):self.add();self.assertEqual(self.b.recall(1),[])
 def test_chain(self):self.add();p=self.b.payload(self.tick(),1,5);self.b.append(p,self.sign(p,1));self.assertTrue(self.b.verify())
 def test_observation_edit(self):p,s=self.add();p['observation']=8;self.assertRaises(InvalidSignature,self.b.append,p,s)
if __name__=='__main__':unittest.main()
