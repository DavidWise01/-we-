import unittest,tempfile,concurrent.futures
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from cryptography.exceptions import InvalidSignature
from wag135 import *
class Tests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.path=Path(t.name)/'db';self.a={n:K.generate() for n in 'HON'};self.b={**self.a,'N':K.generate()};self.g=Gate(self.path,'mesh',self.members(self.a));self.send={'kind':'send','src':0,'dst':1,'q':26,'id':'p'};self.rotate={'kind':'rotate','members':self.members(self.b)}
 def members(self,ks):return {n:k.public_key().public_bytes_raw().hex() for n,k in ks.items()}
 def sign(self,ks,p,role='approve'):return {n:k.sign(enc([role,p])).hex() for n,k in ks.items()}
 def submit(self,o,ks=None,new=None):
  p=proposal(self.g.head(),o);return self.g.commit(p,self.sign(ks or self.a,p),self.sign(new,p,'accept') if new else None)
 def test_rotation(self):self.assertEqual(self.submit(self.rotate,new=self.b)['epoch'],1)
 def test_pending(self):self.submit(self.send);s=self.submit(self.rotate,new=self.b);self.assertEqual(s['pending']['p'],[1,26]);self.assertEqual(self.submit({'kind':'receive','id':'p'},self.b)['q'],[130,26,0])
 def test_race(self):
  s=self.g.head();p=proposal(s,self.send);r=proposal(s,self.rotate);args=[(p,self.sign(self.a,p),None),(r,self.sign(self.a,r),self.sign(self.b,r,'accept'))]
  def run(a):
   try:self.g.commit(*a);return 1
   except ValueError:return 0
  with concurrent.futures.ThreadPoolExecutor(2) as ex:self.assertEqual(sum(ex.map(run,args)),1)
 def test_stale(self):p=proposal(self.g.head(),self.send);self.submit(self.rotate,new=self.b);self.assertRaises(ValueError,self.g.commit,p,self.sign(self.a,p))
 def test_retired(self):self.submit(self.rotate,new=self.b);self.assertRaises(ValueError,self.submit,{'kind':'rotate','members':self.members(self.a)},self.b,self.a)
 def test_alias(self):m=self.members(self.a);m['N']=m['H'].upper();self.assertRaises(ValueError,validate,m)
 def test_missing_accept(self):self.assertRaises(ValueError,self.submit,self.rotate);self.assertEqual(self.g.head()['seq'],0)
 def test_old_key(self):self.submit(self.rotate,new=self.b);self.assertRaises(InvalidSignature,self.submit,self.send)
 def test_restart(self):s=self.submit(self.rotate,new=self.b);self.assertEqual(Gate(self.path,'mesh',self.members(self.a)).head(),s)
 def test_wrong_role(self):p=proposal(self.g.head(),self.rotate);self.assertRaises(InvalidSignature,self.g.commit,p,self.sign(self.a,p),self.sign(self.b,p))
if __name__=='__main__':unittest.main(verbosity=2)
