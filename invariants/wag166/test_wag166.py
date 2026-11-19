import unittest
from wag166 import *
class Tests(unittest.TestCase):
    def setUp(self):self.x=list(map(leaf,records(166)));self.a=root(self.x[:165]);self.b=root(self.x);self.p=proof(self.x,165)
    def test_append(self):self.assertTrue(verify(165,166,self.a,self.b,self.p))
    def test_rewrite(self):
        y=self.x[:];y[0]=leaf('rewrite');self.assertFalse(verify(165,166,self.a,root(y),proof(y,165)))
    def test_truncate(self):self.assertFalse(verify(165,166,self.a,self.b,self.p[:-1]))
    def test_extra(self):self.assertFalse(verify(165,166,self.a,self.b,self.p+[bytes(32)]))
    def test_bad_hash(self):self.assertFalse(verify(165,166,self.a,self.b,[bytes(32)]+self.p[1:]))
    def test_reverse(self):self.assertFalse(verify(166,165,self.b,self.a,self.p))
    def test_same(self):self.assertTrue(verify(166,166,self.b,self.b,[]))
    def test_matrix(self):
        for n in range(1,65):
            for m in range(1,n+1):self.assertTrue(verify(m,n,root(self.x[:m]),root(self.x[:n]),proof(self.x[:n],m)))
    def test_conservation(self):
        for r in records(166):self.assertEqual(sum(r['x'])+r['center'],26);self.assertEqual(sum(r['b'])+r['spent'],540)
if __name__=='__main__':unittest.main(verbosity=2)
