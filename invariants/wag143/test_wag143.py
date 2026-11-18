import unittest
from itertools import combinations
from wag143 import *
class Test(unittest.TestCase):
 def test_cut(self):self.assertEqual(cut((4,3,2),5),2)
 def test_zero(self):self.assertEqual(cut((4,),0),0)
 def test_infeasible(self):self.assertIsNone(optimize(13,20))
 def test_full(self):self.assertEqual(optimize(13,39)['r'],(13,5,5))
 def test_budget(self):self.assertTrue(all(x['cost']<=25 for x in placements(13,25)))
 def test_capacity(self):self.assertTrue(all(max(x['sizes'])<=4 for x in placements(13,39)))
 def test_conservation(self):self.assertTrue(all(sum(x['sizes'])==13 for x in placements(13,39)))
 def test_monotonic(self):
  best=[min(optimize(13,b)['r']) for b in range(21,40)];self.assertEqual(best,sorted(best))
 def test_exhaustive_cut(self):
  for x in placements(8,24):
   s=x['sizes'];t=8-x['q']+1
   self.assertEqual(x['r'][1],min(len(c) for k in range(1,len(s)+1) for c in combinations(s,k) if sum(c)>=t))
 def test_optimal(self):
  for b in range(21,40):self.assertEqual(min(optimize(13,b)['r']),max(min(x['r']) for x in placements(13,b)))
if __name__=='__main__':unittest.main(verbosity=2)
