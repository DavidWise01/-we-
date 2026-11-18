import unittest,tempfile,copy,sqlite3
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from cryptography.exceptions import InvalidSignature
from wag135 import Gate
from wag136 import *
class Tests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.g=Gate(Path(t.name)/'db','mesh',self.members(a:={n:K.generate() for n in 'HON'}));self.a=a;self.b={**a,'N':K.generate()};self.c={**self.b,'H':K.generate()}
  self.go({'kind':'send','src':0,'dst':1,'q':26,'id':'p'},a);self.go({'kind':'rotate','members':self.members(self.b)},a,self.b);self.go({'kind':'rotate','members':self.members(self.c)},self.b,self.c);self.go({'kind':'receive','id':'p'},self.c);self.h=root(self.g.head());self.e,self.s=export(self.g,self.h)
 def members(self,ks):return {n:k.public_key().public_bytes_raw().hex() for n,k in ks.items()}
 def sign(self,ks,p,role):return {n:k.sign(enc([role,p])).hex() for n,k in ks.items()}
 def go(self,o,a,b=None):
  p=proposal(self.g.head(),o);self.g.commit(p,self.sign(a,p,'approve'),self.sign(b,p,'accept') if b else None)
 def audit(self,e):return replay(self.g.genesis,e,self.h)
 def test_full(self):self.assertEqual(self.audit(self.e),self.s);self.assertEqual(self.s['q'],[130,26,0]);self.assertEqual(self.s['epoch'],2)
 def test_missing(self):self.assertRaises(ValueError,self.audit,self.e[:-1])
 def test_middle(self):self.assertRaises(ValueError,self.audit,self.e[:1]+self.e[2:])
 def test_reorder(self):self.assertRaises(ValueError,self.audit,self.e[::-1])
 def test_retired(self):p,a,b=self.e[-1];self.e[-1][1]=self.sign(self.a,p,'approve');self.assertRaises(InvalidSignature,self.audit,self.e)
 def test_accept(self):self.e[1][2].pop('N');self.assertRaises(ValueError,self.audit,self.e)
 def test_no_pin(self):self.assertRaises(ValueError,replay,self.g.genesis,self.e,None)
 def test_tamper(self):self.e[0][0][3]['q']=1;self.assertRaises(ValueError,self.audit,self.e)
 def test_gap(self):
  with sqlite3.connect(self.g.path) as c:c.execute('DELETE FROM journal WHERE seq=2')
  self.assertRaises(ValueError,export,self.g,self.h)
 def test_rollback_limit(self):
  old=replay(self.g.genesis,[],root(self.g.genesis));self.assertEqual(old['seq'],0)
if __name__=='__main__':unittest.main(verbosity=2)
