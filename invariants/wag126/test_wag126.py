import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from wag125 import genesis,message,enc,replay
from wag126 import issue,check
class Tests(unittest.TestCase):
 def setUp(self):
  self.ks={n:K.generate() for n in 'HON'};self.keys={n:k.public_key() for n,k in self.ks.items()};self.f=K.generate();self.c=[];self.old=self.floor();self.add({'kind':'send','src':0,'dst':1,'q':26,'id':'p'});self.latest=self.floor(self.old)
 def add(self,op):
  m=message('mesh',replay('mesh',self.keys,self.c),op);self.c.append({'message':m,'op':op,'cert':{n:k.sign(enc(m)).hex() for n,k in self.ks.items()}})
 def floor(self,old=None):return issue('mesh',self.keys,[self.c]*3,self.f,old)
 def check(self,chains,floor):return check('mesh',self.keys,chains,self.f.public_key(),floor)[0]
 def test_current(self):self.assertEqual(self.check([self.c]*3,self.latest),'CURRENT')
 def test_common_rollback(self):self.assertEqual(self.check([[]]*3,self.latest),'HOLD_ROLLBACK')
 def test_missing(self):self.assertEqual(self.check([self.c]*3,None),'HOLD_NO_FLOOR')
 def test_tamper(self):self.latest['body'][2]=0;self.assertEqual(self.check([self.c]*3,self.latest),'HOLD_INVALID_FLOOR')
 def test_lag(self):self.assertEqual(self.check([self.c,self.c,[]],self.latest),'HOLD_LAG')
 def test_future(self):self.add({'kind':'graduate'});self.assertEqual(self.check([self.c]*3,self.latest),'CURRENT')
 def test_fork(self):self.c=[];self.add({'kind':'graduate'});self.assertEqual(self.check([self.c]*3,self.latest),'HOLD_FLOOR_FORK')
 def test_issuer_regression(self):self.c=[];self.assertRaises(ValueError,self.floor,self.latest)
 def test_floor_rollback_limit(self):self.assertEqual(self.check([[]]*3,self.old),'CURRENT')
 def test_wrong_key(self):self.assertEqual(check('mesh',self.keys,[self.c]*3,K.generate().public_key(),self.latest)[0],'HOLD_INVALID_FLOOR')
if __name__=='__main__':unittest.main(verbosity=2)
