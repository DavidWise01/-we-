import unittest
from wag146 import *
class Tests(unittest.TestCase):
 def test_erasure(self):self.assertEqual(search(model(),13,9,4,(1,))[0],2)
 def test_availability(self):self.assertEqual(search(model(),13,9,4,(2,))[0],1)
 def test_forgery(self):self.assertEqual(search(model(),13,9,4,(3,))[0],1)
 def test_incompatible(self):self.assertIsNone(search(model(),13,9,4,(2,3)))
 def test_all_simultaneous(self):self.assertIsNone(search(model(),13,9,4,(1,2,3)))
 def test_all_temporal(self):self.assertEqual(search(model(),13,9,4,(1,2,3),True)[0],3)
 def test_recovery(self):self.assertEqual(evaluate([(0,1,'a',range(9))],13,9,2),[(0,False,True,False),(1,False,False,False)])
 def test_offline_keys(self):self.assertFalse(evaluate([(0,1,'a',range(4)),(0,1,'f',range(5))],13,9,1)[0][3])
 def test_exact_boundary(self):self.assertTrue(evaluate([(0,1,'f',range(5))],13,9,1)[0][3])
 def test_invalid(self):self.assertRaises(ValueError,evaluate,[(0,0,'a',[0])],13,9,1)
if __name__=='__main__':unittest.main(verbosity=2)
