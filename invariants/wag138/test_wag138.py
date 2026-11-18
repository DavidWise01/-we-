import unittest,tempfile,sqlite3
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from wag137 import start,propose,replay,enc
from wag138 import Keeper,Challenge
class Tests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.path=Path(t.name)/'keeper';self.ks={n:K.generate() for n in 'HON'};self.k=K.generate();self.g=start('mesh',{n:k.public_key().public_bytes_raw().hex() for n,k in self.ks.items()},{n:[n] for n in self.ks});self.w=Keeper(self.path,self.g,self.k,True);self.e=[];self.add({'kind':'send','src':0,'dst':1,'q':26,'id':'p'});self.w.retain(self.e)
 def add(self,o):
  p=propose(replay(self.g,self.e),o);self.e.append([p,{n:k.sign(enc(['approve',p])).hex() for n,k in self.ks.items()},None])
 def verify(self,e=None):
  c=Challenge(self.g);return c.verify(self.e if e is None else e,self.k.public_key(),self.w.respond(c.nonce))
 def test_current(self):self.assertEqual(self.verify()['seq'],1)
 def test_regression(self):self.assertRaises(ValueError,self.w.retain,[])
 def test_restart(self):self.w=Keeper(self.path,self.g,self.k);self.assertEqual(self.verify()['seq'],1)
 def test_replay(self):a,b=Challenge(self.g),Challenge(self.g);self.assertRaises(ValueError,b.verify,self.e,self.k.public_key(),self.w.respond(a.nonce))
 def test_extension(self):self.add({'kind':'receive','id':'p'});self.assertRaises(ValueError,self.verify);self.w.retain(self.e);self.assertEqual(self.verify()['q'],[130,26,0])
 def test_fork(self):self.e=[];self.add({'kind':'send','src':0,'dst':1,'q':1,'id':'q'});self.assertRaises(ValueError,self.w.retain,self.e)
 def test_expiry(self):n=[0];c=Challenge(self.g,clock=lambda:n[0]);n[0]=6;self.assertRaises(ValueError,c.verify,self.e,self.k.public_key(),self.w.respond(c.nonce))
 def test_used(self):c=Challenge(self.g);r=self.w.respond(c.nonce);c.verify(self.e,self.k.public_key(),r);self.assertRaises(ValueError,c.verify,self.e,self.k.public_key(),r)
 def test_missing(self):c=Challenge(self.g);self.assertRaises(ValueError,c.verify,self.e,self.k.public_key(),None)
 def test_rollback_limit(self):
  with sqlite3.connect(self.path) as c:c.execute('DELETE FROM log WHERE n>0')
  self.assertEqual(self.verify([])['seq'],0)
if __name__=='__main__':unittest.main(verbosity=2)
