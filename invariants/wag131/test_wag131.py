import unittest,tempfile,sqlite3
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from wag129 import Gate,replay
from wag131 import *
class Tests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.p=Path(t.name);self.ks={n:K.generate() for n in 'HON'};self.keys={n:k.public_key() for n,k in self.ks.items()};self.k=K.generate();self.g=Gate(self.p/'gate','mesh',self.k,self.keys);self.rs=[Retainer(self.p/n,'mesh',n,k,self.keys,self.k.public_key(),True) for n,k in self.ks.items()];self.old=self.bound([]);self.add({'kind':'send','src':0,'dst':1,'q':26,'id':'p'});self.e=self.g.export()[0];self.b=self.bound(self.e)
  for r in self.rs:r.retain(self.e,self.b)
 def add(self,o):
  p=self.g.proposal(o);self.g.commit(p,{n:k.sign(enc(p)).hex() for n,k in self.ks.items()})
 def bound(self,e):return issue('mesh',e,self.ks,lambda e:replay('mesh',self.keys,self.k.public_key(),e))
 def answers(self,c):return {r.name:r.respond(c.nonce) for r in self.rs}
 def verify(self,c,e=None,a=None):return c.verify(self.e if e is None else e,self.keys,self.k.public_key(),self.answers(c) if a is None else a)
 def test_valid(self):self.assertEqual(self.verify(Challenge('mesh')),'VERIFIED_THROUGH_LIVE_BOUND')
 def test_truncated(self):self.assertEqual(self.verify(Challenge('mesh'),[]),'HOLD_TRUNCATED')
 def test_replay(self):self.assertEqual(self.verify(Challenge('mesh'),a=self.answers(Challenge('mesh'))),'HOLD_RESPONSE')
 def test_missing(self):c=Challenge('mesh');a=self.answers(c);del a['H'];self.assertEqual(self.verify(c,a=a),'HOLD_MISSING')
 def test_used(self):c=Challenge('mesh');self.verify(c);self.assertEqual(self.verify(c),'HOLD_USED')
 def test_expired(self):n=[0];c=Challenge('mesh',clock=lambda:n[0]);n[0]=6;self.assertEqual(self.verify(c),'HOLD_EXPIRED')
 def test_regression(self):self.assertRaises(ValueError,self.rs[0].retain,[],self.old)
 def test_restart(self):self.rs[0]=Retainer(self.p/'H','mesh','H',self.ks['H'],self.keys,self.k.public_key());self.assertEqual(self.verify(Challenge('mesh')),'VERIFIED_THROUGH_LIVE_BOUND')
 def test_extension(self):self.add({'kind':'graduate'});self.assertEqual(self.verify(Challenge('mesh'),self.g.export()[0]),'HOLD_UNRETAINED_EXTENSION')
 def test_disagreement(self):self.add({'kind':'graduate'});e=self.g.export()[0];self.rs[0].retain(e,self.bound(e));self.assertEqual(self.verify(Challenge('mesh'),e),'HOLD_DISAGREEMENT')
 def test_common_rollback_limit(self):
  for r in self.rs:
   with sqlite3.connect(r.path) as db:db.execute('UPDATE retained SET body=?',(enc(self.old).decode(),))
  self.assertEqual(self.verify(Challenge('mesh'),[]),'VERIFIED_THROUGH_LIVE_BOUND')
if __name__=='__main__':unittest.main(verbosity=2)
