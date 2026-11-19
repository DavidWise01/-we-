import unittest,tempfile,concurrent.futures
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from cryptography.exceptions import InvalidSignature
from wag159 import *
class Tests(unittest.TestCase):
 def setUp(self):
    t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.path=Path(t.name)/'db';self.k=[K.generate() for _ in range(10)];self.pub=[k.public_key() for k in self.k];self.g=Gate(self.path,'mesh',self.pub);self.s=self.g.head();self.p=proposal(self.s,[0,1,2],1)
 def sign(self,p,role='YES'):return {i:self.k[i].sign(enc([role,i,p])) for i in p[3]}
 def test_success(self):
    t=self.g.commit(self.p,self.sign(self.p));self.assertEqual(t['x'],[2]*10);self.assertEqual(t['spent'],2);self.assertEqual(sum(t['b'])+t['spent'],540)
 def test_missing(self):
    a=self.sign(self.p);del a[1];self.assertRaises(ValueError,self.g.commit,self.p,a);self.assertEqual(self.g.head(),self.s)
 def test_no(self):self.assertRaises(InvalidSignature,self.g.commit,self.p,self.sign(self.p,'NO'));self.assertEqual(self.g.head(),self.s)
 def test_amount(self):
    a=self.sign(self.p);self.p[4]=2;self.assertRaises(ValueError,self.g.commit,self.p,a)
 def test_route(self):
    a=self.sign(self.p);p=proposal(self.s,[0,9,8,7,6,5,4,3,2],1);self.assertRaises(ValueError,self.g.commit,p,a)
 def test_alternate(self):
    p=proposal(self.s,[0,9,8,7,6,5,4,3,2],1);self.assertEqual(self.g.commit(p,self.sign(p))['spent'],8)
 def test_replay(self):
    a=self.sign(self.p);self.g.commit(self.p,a);self.assertRaises(ValueError,self.g.commit,self.p,a)
 def test_restart(self):
    a=self.sign(self.p);t=self.g.commit(self.p,a);g=Gate(self.path,'mesh',self.pub);self.assertEqual(g.head(),t);self.assertRaises(ValueError,g.commit,self.p,a)
 def test_race(self):
    a=self.sign(self.p)
    def tryit(_):
        try:self.g.commit(self.p,a);return 1
        except ValueError:return 0
    with concurrent.futures.ThreadPoolExecutor(2) as e:self.assertEqual(sum(e.map(tryit,range(2))),1)
 def test_wrong_signer(self):
    a=self.sign(self.p);a[1]=self.k[0].sign(enc(['YES',1,self.p]));self.assertRaises(InvalidSignature,self.g.commit,self.p,a)
if __name__=='__main__':unittest.main(verbosity=2)
