import unittest
from wag144 import *
class Tests(unittest.TestCase):
    def test_cut(self):self.assertEqual(cut((4,3,2),5),2)
    def test_zero(self):self.assertEqual(cut((4,),0),0)
    def test_infeasible(self):self.assertIsNone(optimize(13,20))
    def test_full(self):self.assertEqual(optimize(13,39)[4],(13,5,5))
    def test_budget(self):self.assertTrue(all(x[3]<=29 for x in designs(13,29)))
    def test_capacity(self):self.assertTrue(all(sum(x[0])==13 and max(x[0])<=4 for x in designs(13,39)))
    def test_monotone(self):
        a=[min(optimize(13,b)[4]) for b in range(21,40)];self.assertEqual(a,sorted(a))
    def test_correlated(self):
        x=next(x for x in designs(13,39) if x[:3]==((2,2,2,2,2,1,1,1),0,9));self.assertEqual(x[4],(8,3,3))
    def test_isolated(self):
        x=next(x for x in designs(13,39) if x[:3]==((2,2,2,2,2,1,1,1),31,9));self.assertEqual(x[4],(8,3,5));self.assertEqual(x[3],39)
    def test_symmetry(self):
        a=list(designs(13,39));self.assertEqual(len(a),len(set(a)))
if __name__=='__main__':unittest.main(verbosity=2)
