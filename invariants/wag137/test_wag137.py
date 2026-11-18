import unittest,copy
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from cryptography.exceptions import InvalidSignature
from wag137 import *
class Tests(unittest.TestCase):
 def setUp(self):
  self.a={n:K.generate() for n in 'HON'};self.b={**self.a,'N':K.generate()};self.k=K.generate();self.r={n:[n] for n in 'HON'};self.g=start('mesh',self.members(self.a),self.r);self.e=[]
  self.add({'kind':'send','src':0,'dst':1,'q':26,'id':'p'},self.a);self.add({'kind':'rotate','members':self.members(self.b),'roots':{**self.r,'N':['new-N']}},self.a,self.b);self.add({'kind':'receive','id':'p'},self.b);self.c=bound(self.g,self.e,self.k)
 def members(self,ks):return {n:k.public_key().public_bytes_raw().hex() for n,k in ks.items()}
 def sign(self,ks,p,role):return {n:k.sign(enc([role,p])).hex() for n,k in ks.items()}
 def add(self,o,a,b=None):
  p=propose(replay(self.g,self.e),o);self.e.append([p,self.sign(a,p,'approve'),self.sign(b,p,'accept') if b else None])
 def check(self,e):return check(self.g,e,self.c,self.k.public_key())
 def test_full(self):self.assertEqual(self.check(self.e)['q'],[130,26,0])
 def test_shared(self):self.assertRaises(ValueError,topology,{'H':['A'],'O':['A'],'N':['B']})
 def test_missing(self):self.assertRaises(ValueError,topology,{'H':['A'],'O':['B'],'N':[]})
 def test_tampered(self):self.e[1][0][3]['roots']['N']=['fake'];self.assertRaises(ValueError,self.check,self.e)
 def test_truncate(self):self.assertRaises(ValueError,self.check,self.e[:-1])
 def test_extension(self):self.add({'kind':'send','src':1,'dst':2,'q':1,'id':'q'},self.b);self.assertEqual(self.check(self.e)['seq'],4)
 def test_forged_bound(self):self.c[0][2]=0;self.assertRaises(InvalidSignature,self.check,self.e)
 def test_retired(self):p=self.e[-1][0];self.e[-1][1]=self.sign(self.a,p,'approve');self.assertRaises(InvalidSignature,replay,self.g,self.e)
 def test_old_bound_limit(self):c=bound(self.g,[],self.k);self.assertEqual(check(self.g,[],c,self.k.public_key())['seq'],0)
 def test_wrong_genesis(self):g=copy.deepcopy(self.g);g['mesh']='other';self.assertRaises(ValueError,check,g,self.e,self.c,self.k.public_key())
if __name__=='__main__':unittest.main(verbosity=2)
