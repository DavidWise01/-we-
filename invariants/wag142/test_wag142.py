import unittest
from wag142 import *
class Tests(unittest.TestCase):
 def test_three(self):self.assertEqual(vector(3,3,{a:independent(3) for a in 'eaf'}),(3,1,3))
 def test_modes(self):self.assertEqual(vector(5,4,example(5)),(5,1,3))
 def test_shared_signing(self):self.assertEqual(vector(3,3,{'e':independent(3),'a':independent(3),'f':{'admin':{0,1,2}}}),(3,1,1))
 def test_zero_intersection(self):self.assertEqual(vector(8,4,example(8)),(8,1,0))
 def test_overlap(self):self.assertEqual(cut(3,{'a':{0,1},'b':{1,2}},3),2)
 def test_missing(self):self.assertRaises(ValueError,cut,3,{'a':{0}},2)
 def test_unknown(self):self.assertRaises(ValueError,cut,3,{'a':{0,1,2,3}},2)
 def test_frontier(self):self.assertEqual(frontier(3,example(3)),[(3,(3,1,3))])
 def test_fibonacci(self):
  for n in (3,5,8,13):
   for q in range(1,n+1):self.assertEqual(vector(n,q,{a:independent(n) for a in 'eaf'}),(n,n-q+1,max(0,2*q-n)))
 def test_balanced(self):
  for n,q,r in [(3,2,1),(5,4,2),(8,6,3),(13,9,5)]:
   self.assertEqual(max(min(n-j+1,max(0,2*j-n)) for j in range(1,n+1)),r)
   self.assertEqual(min(n-q+1,max(0,2*q-n)),r)
if __name__=='__main__':unittest.main(verbosity=2)
