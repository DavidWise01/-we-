import unittest
from wag163 import *
class Tests(unittest.TestCase):
 def setUp(self):
    self.a=branch([0,1,2]);self.b=branch([3,4,5]);self.q=[self.a,self.b];self.k=[Ed25519PrivateKey.generate() for _ in range(3)];self.r={str(i):(str(i),k.public_key()) for i,k in enumerate(self.k)};self.d=h(join(self.q))
 def obs(self):return [(str(i),self.d,k.sign(enc(['WAG163',str(i),self.r[str(i)][0],self.d]))) for i,k in enumerate(self.k)]
 def test_order(self):self.assertEqual(join(self.q),join(self.q[::-1]))
 def test_conservation(self):
    s=join(self.q)['state'];self.assertEqual(s['x'],[2]*10);self.assertEqual(s['spent'],4);self.assertEqual(sum(s['b']),536)
 def test_overlap(self):self.assertRaises(ValueError,join,[self.a,self.a])
 def test_stale(self):self.assertRaises(ValueError,join,[{**self.a,'parent':'bad'}])
 def test_three(self):self.assertEqual(certify(self.q,self.r,self.obs()),join(self.q))
 def test_two(self):self.assertRaises(ValueError,certify,self.q,self.r,self.obs()[:2])
 def test_shared_root(self):
    self.r['2']=('1',self.k[2].public_key());self.assertRaises(ValueError,certify,self.q,self.r,self.obs())
 def test_shared_key(self):
    self.k[2]=self.k[1];self.r['2']=('2',self.k[1].public_key());self.assertRaises(ValueError,certify,self.q,self.r,self.obs())
 def test_wrong_checkpoint(self):
    o=self.obs();o[0]=('0','bad',o[0][2]);self.assertRaises(ValueError,certify,self.q,self.r,o)
 def test_observe_only(self):
    before=enc(G);certify(self.q,self.r,self.obs());self.assertEqual(enc(G),before)
if __name__=='__main__':unittest.main(verbosity=2)
