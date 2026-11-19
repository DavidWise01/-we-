import unittest
from wag157 import *
class Tests(unittest.TestCase):
    def test_relay(self):
        x=[3,2,1]+[2]*7;y,b,c,r=relay(x,[10]*10)
        self.assertEqual(y,[2]*10);self.assertEqual(c,2);self.assertEqual(r,((0,1,2),1))
    def test_starved(self):
        x=[3,2,1]+[2]*7;self.assertEqual(relay(x,[0]*10)[0],x)
    def test_partial(self):
        x=[3,2,1]+[2]*7;y,b,c,r=relay(x,[F(1,2)]*10);self.assertEqual(y[:3],[F(5,2),2,F(3,2)]);self.assertEqual(c,1)
    def test_uniform(self):self.assertIsNone(relay([2]*10,[10]*10)[3])
    def test_invalid(self):self.assertRaises(ValueError,relay,[1]*10,[10]*10)
    def test_convergence(self):
        x=[8,12]+[0]*8;b=[54]*10;spent=0
        for _ in range(360):
            old=sum((v-2)**2 for v in x);x,b,c,r=relay(x,b);spent+=c
            self.assertEqual(sum(x),20);self.assertEqual(sum(b)+spent,540);self.assertLessEqual(sum((v-2)**2 for v in x),old)
        self.assertEqual(x,[2]*10)
if __name__=='__main__':unittest.main(verbosity=2)
