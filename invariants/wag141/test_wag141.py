import unittest,itertools
from wag141 import resistance
class Tests(unittest.TestCase):
 def r(self,w,d,q):return tuple(x[0] for x in resistance(w,d,q))
 def test_unanimous(self):self.assertEqual(self.r('HON',{x:{x} for x in 'HON'},3),(3,1,3))
 def test_majority(self):self.assertEqual(self.r('HON',{x:{x} for x in 'HON'},2),(3,2,1))
 def test_single(self):self.assertEqual(self.r('HON',{x:{x} for x in 'HON'},1),(3,3,0))
 def test_shared(self):self.assertEqual(self.r('HON',{'host':set('HON')},3),(1,1,1))
 def test_overlap(self):self.assertEqual(self.r('HON',{'a':set('HO'),'b':set('ON')},2),(2,1,1))
 def test_four(self):self.assertEqual(self.r('ABCD',{x:{x} for x in 'ABCD'},3),(4,2,2))
 def test_invalid(self):self.assertRaises(ValueError,resistance,'HON',{'a':{'H'}},2)
 def test_quorum(self):self.assertRaises(ValueError,resistance,'HON',{'a':set('HON')},4)
 def test_intersection(self):
  for n in range(1,9):
   for q in range(1,n+1):
    qs=list(map(set,itertools.combinations(range(n),q)))
    self.assertEqual(min(len(a&b) for a in qs for b in qs),max(0,2*q-n))
 def test_cut_witnesses(self):self.assertEqual(resistance('HON',{'a':set('HO'),'b':{'N'}},3)[0],(2,[('a','b')]))
if __name__=='__main__':unittest.main(verbosity=2)
