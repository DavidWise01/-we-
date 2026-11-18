import unittest,itertools
from wag132 import audit,blast_radius
class Tests(unittest.TestCase):
 def setUp(self):
  self.w=['H','O','N'];self.r={'A','B','C'};self.g={'H':['A'],'O':['B'],'N':['C'],'A':[],'B':[],'C':[]}
 def check(self):return audit(self.g,self.w,self.r)[0]
 def test_separate(self):self.assertEqual(self.check(),'DISJOINT_DECLARED_ROOTS')
 def test_admin(self):self.g['O'].append('A');self.assertEqual(self.check(),'HOLD_SHARED_ROOT')
 def test_recovery(self):self.g.update({'H':['h'],'O':['o'],'h':['A'],'o':['A']});self.assertEqual(self.check(),'HOLD_SHARED_ROOT')
 def test_missing(self):del self.g['B'];self.assertEqual(self.check(),'HOLD_ANCESTRY')
 def test_cycle(self):self.g['B']=['O'];self.assertEqual(self.check(),'HOLD_ANCESTRY')
 def test_unknown(self):self.r.remove('B');self.assertEqual(self.check(),'HOLD_ANCESTRY')
 def test_duplicate(self):self.assertEqual(audit(self.g,['H','H','N'],self.r)[0],'HOLD_MEMBERSHIP')
 def test_blast(self):self.g['O'].append('A');self.assertEqual(blast_radius(self.g,self.w,'A'),('H','O'))
 def test_exhaustive(self):
  for assignment in itertools.product('ABC',repeat=3):
   for w,r in zip(self.w,assignment):self.g[w]=[r]
   self.assertEqual(self.check()=='DISJOINT_DECLARED_ROOTS',len(set(assignment))==3)
 def test_hidden_root_limit(self):
  self.assertEqual(self.check(),'DISJOINT_DECLARED_ROOTS');self.g['A']=['X'];self.g['B']=['X'];self.g['X']=[];self.r={'X','C'};self.assertEqual(self.check(),'HOLD_SHARED_ROOT')
if __name__=='__main__':unittest.main(verbosity=2)
