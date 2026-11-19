import unittest
from wag165 import *
class Tests(unittest.TestCase):
 def setUp(self):self.rs=records();self.xs=list(map(leaf,self.rs));self.r=root(self.xs)
 def test_all(self):
    for i,v in enumerate(self.rs):self.assertTrue(verify(v,i,165,proof(self.xs,i),self.r))
 def test_tamper(self):self.assertFalse(verify({**self.rs[0],'center':7},0,165,proof(self.xs,0),self.r))
 def test_index(self):self.assertFalse(verify(self.rs[0],1,165,proof(self.xs,0),self.r))
 def test_truncated(self):self.assertFalse(verify(self.rs[0],0,165,proof(self.xs,0)[:-1],self.r))
 def test_extra(self):self.assertFalse(verify(self.rs[0],0,165,proof(self.xs,0)+[bytes(32)],self.r))
 def test_wrong_root(self):self.assertFalse(verify(self.rs[0],0,165,proof(self.xs,0),bytes(32)))
 def test_conservation(self):
    for v in self.rs:self.assertEqual(sum(v['x'])+v['center'],26);self.assertEqual(sum(v['b'])+v['spent'],540)
 def test_links(self):
    for a,b in zip(self.rs,self.rs[1:]):self.assertEqual(b['parent'],leaf(a).hex())
if __name__=='__main__':unittest.main(verbosity=2)
