import unittest,tempfile
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag124 import *
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.ks={n:Ed25519PrivateKey.generate() for n in 'HON'};self.keys={n:k.public_key() for n,k in self.ks.items()};self.a=Anchor(Path(self.tmp.name)/'anchor.db','mesh',self.keys);self.addCleanup(self.a.db.close);self.op={'kind':'send','src':0,'dst':1,'q':26,'id':'p'}
 def cert(self,s,op):return {n:k.sign(statement('mesh',s,op,step(s,op))).hex() for n,k in self.ks.items()}
 def go(self,op):s=self.a.head();return self.a.append(s,op,self.cert(s,op))
 def test_conservation(self):self.assertEqual(total(self.go(self.op)),156);self.assertEqual(total(self.go({'kind':'receive','id':'p'})),156)
 def test_graduate(self):s=self.go(self.op);t=self.go({'kind':'graduate'});self.assertEqual(s['pending'],t['pending']);self.assertEqual(t['generation'],2)
 def test_rollback(self):s=self.a.head();t=self.go(self.op);self.assertEqual(self.a.reconcile(s),('ROLLBACK_HOLD',t))
 def test_fork(self):s=genesis();s['balances']=[0,156,0];self.assertEqual(self.a.reconcile(s)[0],'FORK_HOLD')
 def test_stale(self):s=self.a.head();c=self.cert(s,self.op);self.go(self.op);self.assertRaises(ValueError,self.a.append,s,self.op,c)
 def test_missing(self):s=self.a.head();c=self.cert(s,self.op);c.pop('H');self.assertRaises(ValueError,self.a.append,s,self.op,c)
 def test_forgery(self):s=self.a.head();c=self.cert(s,self.op);c['H']='00'*64;self.assertRaises(ValueError,self.a.append,s,self.op,c)
 def test_receipt_replay(self):self.go(self.op);self.go({'kind':'receive','id':'p'});self.assertRaises(ValueError,self.go,{'kind':'receive','id':'p'})
 def test_restart(self):t=self.go(self.op);a=Anchor(Path(self.tmp.name)/'anchor.db','mesh',self.keys);self.assertEqual(a.head(),t);a.db.close()
 def test_scope(self):s=self.a.head();c=self.cert(s,self.op);self.assertRaises(ValueError,verify,self.keys,statement('other',s,self.op,step(s,self.op)),c)
if __name__=='__main__':unittest.main()
