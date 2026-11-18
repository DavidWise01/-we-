import unittest,itertools
from wag140 import *
class Tests(unittest.TestCase):
 def test_shared(self): self.assertEqual(resistance('HON',{'host':set('HON')}),1)
 def test_independent(self): self.assertEqual(resistance('HON',{x:{x} for x in 'HON'}),3)
 def test_overlap(self): self.assertEqual(resistance('HON',{'a':set('HO'),'b':set('ON')}),2)
 def test_shared_admin(self): self.assertEqual(resistance('HON',{**{x:{x} for x in 'HON'},'admin':set('HON')}),1)
 def test_incomplete(self): self.assertRaises(ValueError,cuts,'HON',{'a':{'H'}})
 def test_unknown(self): self.assertRaises(ValueError,cuts,'HON',{'a':set('HONX')})
 def test_empty(self): self.assertRaises(ValueError,cuts,[],{})
 def test_minimal(self): self.assertEqual(cuts('HON',{'a':set('HON'),'b':{'H'},'c':set('ON')}),(('a',),('b','c')))
 def test_availability(self): self.assertEqual(availability_cut('HON',{x:{x} for x in 'HON'}),1)
 def test_exhaustive(self):
  subsets=[set(x for i,x in enumerate('HON') if mask>>i&1) for mask in range(1,8)]
  count=0
  for vs in itertools.product(subsets,repeat=3):
   if set.union(*vs)!=set('HON'):continue
   d=dict(zip('ABC',vs)); expected=min(len(c) for n in range(1,4) for c in itertools.combinations(d,n) if set.union(*(d[k] for k in c))==set('HON'))
   self.assertEqual(resistance('HON',d),expected);count+=1
  self.assertEqual(count,265)
if __name__=='__main__':unittest.main(verbosity=2)
