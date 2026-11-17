import unittest,tempfile,sqlite3
from rsi010 import Continuity,canonical
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=self.tmp.name+'/db';self.sk={str(i):Ed25519PrivateKey.generate() for i in range(9)};self.w={str(i):Ed25519PrivateKey.generate() for i in range(3)};self.pk={i:k.public_key().public_bytes_raw() for i,k in self.sk.items()};self.wp={i:k.public_key().public_bytes_raw() for i,k in self.w.items()};self.b=Continuity(self.path,self.pk,self.wp,'jane-test')
 def tearDown(self):self.b.close();self.tmp.cleanup()
 def add(self):
  f=self.b.advance([4]*9,[4]*9);i=f['tick']%3;p=self.b.payload(f,i,4);self.b.append(p,self.sk[str(i)].sign(canonical(p).encode()).hex());return p
 def seal(self):
  h=self.b.snapshot();return h,{i:k.sign(canonical(h).encode()).hex() for i,k in self.w.items()}
 def check(self,h,s):return self.b.checked_recall(0,h,s)
 def test_exact(self):p=self.add();self.assertEqual(self.check(*self.seal()),[p])
 def test_missing_suffix(self):self.add();h,s=self.seal();self.b.db.execute('DELETE FROM signed');self.assertTrue(self.b.verify());self.assertRaises(ValueError,self.check,h,s)
 def test_missing_frame(self):self.add();self.b.advance([4]*9,[4]*9);h,s=self.seal();self.b.db.execute('DELETE FROM frames WHERE t=1');self.assertRaises(ValueError,self.check,h,s)
 def test_stale(self):self.add();h,s=self.seal();self.add();self.assertRaises(ValueError,self.check,h,s)
 def test_forged(self):self.add();h,s=self.seal();s['0']=s['1'];self.assertRaises(InvalidSignature,self.check,h,s)
 def test_quorum(self):self.add();h,s=self.seal();s.pop('0');self.assertRaises(ValueError,self.check,h,s)
 def test_stream(self):self.add();h,s=self.seal();h['stream']='other';self.assertRaises(InvalidSignature,self.check,h,s)
 def test_restart(self):p=self.add();h,s=self.seal();self.b.close();self.b=Continuity(self.path,self.pk,self.wp,'jane-test');self.assertEqual(self.check(h,s),[p])
 def test_tamper(self):self.add();h,s=self.seal();self.b.db.execute("UPDATE signed SET body='{}'");self.assertRaises(ValueError,self.check,h,s)
 def test_unsigned_recall(self):self.assertRaises(ValueError,self.b.recall,0)
 def test_empty(self):self.assertEqual(self.check(*self.seal()),[])
 def test_rollback_and_old_anchor_limit(self):self.add();old=self.seal();self.add();new=self.seal();self.b.db.execute('DELETE FROM signed WHERE seq=1');self.b.db.execute('DELETE FROM frames WHERE t=1');self.assertRaises(ValueError,self.check,*new);self.assertEqual(len(self.check(*old)),1)
if __name__=='__main__':unittest.main()
