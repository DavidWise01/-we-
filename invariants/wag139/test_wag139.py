import unittest,tempfile,sqlite3
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from cryptography.exceptions import InvalidSignature
from wag137 import start,propose,replay,enc
from wag138 import Keeper
from wag139 import Anchor,Audit
class Tests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.p=Path(t.name);self.ks={n:K.generate() for n in 'HON'};self.k=K.generate();self.a=K.generate();self.g=start('mesh',{n:k.public_key().public_bytes_raw().hex() for n,k in self.ks.items()},{n:[n] for n in self.ks});self.w=Keeper(self.p/'keeper',self.g,self.k,True);self.x=Anchor(self.p/'anchor',self.g,self.k.public_key(),self.a,True);self.e=[];self.retain();self.add({'kind':'send','src':0,'dst':1,'q':26,'id':'p'});self.retain()
 def add(self,o):
  p=propose(replay(self.g,self.e),o);self.e.append([p,{n:k.sign(enc(['approve',p])).hex() for n,k in self.ks.items()},None])
 def retain(self):return self.x.retain(self.e,self.w.retain(self.e))
 def verify(self,e=None):
  c=Audit(self.g);return c.verify(self.e if e is None else e,self.k.public_key(),self.a.public_key(),self.w.respond(c.nonce),self.x.respond(c.nonce))
 def rollback(self,which):
  with sqlite3.connect(self.p/which) as c:c.execute('DELETE FROM '+('log' if which=='keeper' else 'receipts')+' WHERE n>0')
 def test_current(self):self.assertEqual(self.verify()['seq'],1)
 def test_keeper_rollback(self):self.rollback('keeper');self.assertRaises(ValueError,self.verify,[])
 def test_anchor_rollback(self):self.rollback('anchor');self.assertRaises(ValueError,self.verify)
 def test_common_limit(self):self.rollback('anchor');self.rollback('keeper');self.assertEqual(self.verify([])['seq'],0)
 def test_restart(self):self.x=Anchor(self.p/'anchor',self.g,self.k.public_key(),self.a);self.assertEqual(self.verify()['seq'],1)
 def test_partial(self):self.add({'kind':'receive','id':'p'});self.w.retain(self.e);self.assertRaises(ValueError,self.verify);self.retain();self.assertEqual(self.verify()['q'],[130,26,0])
 def test_replay(self):c,d=Audit(self.g),Audit(self.g);self.assertRaises(ValueError,c.verify,self.e,self.k.public_key(),self.a.public_key(),self.w.respond(d.nonce),self.x.respond(c.nonce))
 def test_tamper(self):c=Audit(self.g);r=self.x.respond(c.nonce);r[0][3][0][2]=0;self.assertRaises(InvalidSignature,c.verify,self.e,self.k.public_key(),self.a.public_key(),self.w.respond(c.nonce),r)
 def test_missing(self):c=Audit(self.g);self.assertRaises(ValueError,c.verify,self.e,self.k.public_key(),self.a.public_key(),None,self.x.respond(c.nonce))
 def test_duplicate(self):self.assertEqual(self.retain(),self.retain())
 def test_truncation(self):self.assertRaises(ValueError,self.verify,[])
if __name__=='__main__':unittest.main(verbosity=2)
