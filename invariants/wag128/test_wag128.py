import unittest,tempfile,concurrent.futures,sqlite3
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from wag128 import *
class Tests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.path=Path(self.t.name)/'gate';self.k=K.generate();self.ks={n:K.generate() for n in 'HON'};self.keys={n:k.public_key() for n,k in self.ks.items()};self.a=Gate(self.path,'mesh',self.k,self.keys);self.op={'kind':'send','src':0,'dst':1,'q':26,'id':'p'}
 def sign(self,p):return {n:k.sign(enc(p)).hex() for n,k in self.ks.items()}
 def go(self,o):p=self.a.proposal(o);return self.a.commit(p,self.sign(p))
 def test_transfer(self):self.go(self.op);self.go({'kind':'receive','id':'p'});self.assertEqual(self.a.head()['q'],[130,26,0])
 def test_compete(self):
  ps=[self.a.proposal(self.op),self.a.proposal({'kind':'graduate'})];cs=[self.sign(p) for p in ps]
  def run(i):
   try:self.a.commit(ps[i],cs[i]);return 1
   except ValueError:return 0
  with concurrent.futures.ThreadPoolExecutor(2) as e:self.assertEqual(sum(e.map(run,range(2))),1)
  self.assertEqual(self.a.head()['g'],1)
 def test_retry(self):p=self.a.proposal(self.op);c=self.sign(p);r=self.a.commit(p,c);self.assertEqual(self.a.commit(p,c),r);self.assertEqual(self.a.head()['g'],1)
 def test_restart(self):p=self.a.proposal(self.op);c=self.sign(p);r=self.a.commit(p,c);self.a=Gate(self.path,'mesh',self.k,self.keys);self.assertEqual(self.a.commit(p,c),r)
 def test_tamper(self):p=self.a.proposal(self.op);c=self.sign(p);p[4]['q']=1;self.assertRaises(InvalidSignature,self.a.commit,p,c)
 def test_missing(self):p=self.a.proposal(self.op);c=self.sign(p);del c['H'];self.assertRaises(ValueError,self.a.commit,p,c)
 def test_nonce_conflict(self):p=self.a.proposal(self.op);self.a.commit(p,self.sign(p));q=self.a.proposal({'kind':'graduate'});q[2]=p[2];self.assertRaises(ValueError,self.a.commit,q,self.sign(q))
 def test_wrong_result(self):p=self.a.proposal(self.op);p[5]='bad';self.assertRaises(ValueError,self.a.commit,p,self.sign(p))
 def test_scope(self):p=self.a.proposal(self.op);p[1]='other';self.assertRaises(ValueError,self.a.commit,p,self.sign(p))
 def test_pending_graduation(self):self.go(self.op);self.go({'kind':'graduate'});self.assertEqual(self.a.head()['pending']['p'],[1,26])
 def test_receipt_signature(self):r=self.go(self.op);self.k.public_key().verify(bytes.fromhex(r[1]),enc(r[0]))
if __name__=='__main__':unittest.main(verbosity=2)
