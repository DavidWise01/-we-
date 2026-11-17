import unittest,tempfile,sqlite3
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from wag125 import genesis,message,enc
from wag127 import LiveFloor,Challenge
class Tests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.path=Path(t.name)/'floor.db';self.ks={n:K.generate() for n in 'HON'};self.keys={n:k.public_key() for n,k in self.ks.items()};self.k=K.generate();self.w=LiveFloor(self.path,'mesh',self.k,self.keys,True);m=message('mesh',genesis(),{'kind':'graduate'});self.chain=[{'message':m,'op':{'kind':'graduate'},'cert':{n:k.sign(enc(m)).hex() for n,k in self.ks.items()}}];self.w.advance([self.chain]*3)
 def verify(self,c,chains=None,r=None):return c.verify(self.k.public_key(),self.keys,[self.chain]*3 if chains is None else chains,self.w.respond(c.nonce) if r is None else r)
 def test_current(self):self.assertEqual(self.verify(Challenge('mesh')),'CURRENT')
 def test_replay(self):a=Challenge('mesh');b=Challenge('mesh');self.assertEqual(self.verify(b,r=self.w.respond(a.nonce)),'HOLD_INVALID')
 def test_single_use(self):c=Challenge('mesh');self.assertEqual(self.verify(c),'CURRENT');self.assertEqual(self.verify(c),'HOLD_USED')
 def test_common_rollback(self):self.assertEqual(self.verify(Challenge('mesh'),[[]]*3),'HOLD_ROLLBACK')
 def test_restart(self):self.w=LiveFloor(self.path,'mesh',self.k,self.keys);self.assertEqual(self.verify(Challenge('mesh'),[[]]*3),'HOLD_ROLLBACK')
 def test_regression(self):self.assertRaises(ValueError,self.w.advance,[[]]*3)
 def test_missing(self):c=Challenge('mesh');self.assertEqual(c.verify(self.k.public_key(),self.keys,[self.chain]*3,None),'HOLD_UNAVAILABLE')
 def test_expired(self):now=[0];c=Challenge('mesh',clock=lambda:now[0]);now[0]=6;self.assertEqual(self.verify(c),'HOLD_EXPIRED')
 def test_tamper(self):c=Challenge('mesh');r=self.w.respond(c.nonce);r[0][3]=0;self.assertEqual(self.verify(c,r=r),'HOLD_INVALID')
 def test_scope(self):self.assertEqual(self.verify(Challenge('other')),'HOLD_INVALID')
 def test_witness_rollback_limit(self):
  from wag125 import root
  with sqlite3.connect(self.path) as c:c.execute('UPDATE floor SET g=0,h=?',(root(genesis()),))
  self.assertEqual(self.verify(Challenge('mesh'),[[]]*3),'CURRENT')
if __name__=='__main__':unittest.main(verbosity=2)
