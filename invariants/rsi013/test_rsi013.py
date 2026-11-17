import unittest
from rsi013 import *
class Tests(unittest.TestCase):
 def setUp(self):self.x=[leaf(str(i).encode()) for i in range(130)]
 def test_all_pairs(self):
  for end in range(1,65):
   for start in range(end+1):
    n,f=frontier(self.x[:start]);self.assertTrue(verify(n,f,end,tree(self.x[:end]),proof(self.x[:end],start)))
 def test_root(self):
  for n in range(1,131):self.assertEqual(root(*frontier(self.x[:n])),tree(self.x[:n]))
 def test_fork(self):
  n,f=frontier(self.x[:8]);y=list(self.x);y[0]=leaf(b'fork');self.assertFalse(verify(n,f,len(y),tree(y),proof(y,n)))
 def test_tamper(self):
  n,f=frontier(self.x[:7]);p=proof(self.x,n);p[0]=(p[0][0],leaf(b'bad'));self.assertFalse(verify(n,f,len(self.x),tree(self.x),p))
 def test_missing(self):
  n,f=frontier(self.x[:7]);self.assertFalse(verify(n,f,len(self.x),tree(self.x),proof(self.x,n)[:-1]))
 def test_extra(self):
  n,f=frontier(self.x);self.assertFalse(verify(n,f,n,tree(self.x),[(0,self.x[0])]))
 def test_rollback(self):
  n,f=frontier(self.x);self.assertFalse(verify(n,f,1,self.x[0],[]))
 def test_shape(self):self.assertFalse(verify(7,{},8,tree(self.x[:8]),[]))
 def test_archive(self):
  before=self.x[:];proof(self.x,7);self.assertEqual(before,self.x)
 def test_empty(self):self.assertTrue(verify(0,{},0,sha256(b'').digest(),[]))
if __name__=='__main__':unittest.main()
