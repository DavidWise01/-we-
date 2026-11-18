import unittest
from wag145 import joint,model
class Tests(unittest.TestCase):
    def test_independent(self):self.assertEqual([joint(13,9,model(),a)[0] for a in ('e','a','f','af','eaf')],[13,5,5,5,13])
    def test_overlap(self):self.assertEqual([joint(13,9,model(True),a)[0] for a in ('e','a','f','af','eaf')],[2,1,1,2,3])
    def test_same_domain(self):self.assertEqual(joint(3,3,{'x':{'e':{0,1,2},'a':{0,1,2},'f':{0,1,2}}})[0],1)
    def test_disjoint_quorum(self):self.assertEqual(joint(4,2,{},'f'),(0,[()]))
    def test_unreachable(self):self.assertEqual(joint(3,3,{},'e'),(None,[]))
    def test_invalid(self):self.assertRaises(ValueError,joint,3,3,{'x':{'e':{3}}})
    def test_invalid_axis(self):self.assertRaises(ValueError,joint,3,3,{},'x')
    def test_invalid_quorum(self):self.assertRaises(ValueError,joint,3,4,{})
    def test_joint_lower_bound(self):
        d=model(True)
        self.assertGreaterEqual(joint(13,9,d)[0],max(joint(13,9,d,a)[0] for a in 'eaf'))
    def test_exact_witness(self):self.assertIn(('backup','provider','recovery'),joint(13,9,model(True))[1])
if __name__=='__main__':unittest.main(verbosity=2)
