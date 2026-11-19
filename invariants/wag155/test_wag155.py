import unittest
from wag155 import *
class Tests(unittest.TestCase):
    def test_sweep(self):
        s=initial()
        for a in range(360):
            s=step(s,a);self.assertEqual(sum(s.x)+6,26);self.assertEqual(sum(s.b)+s.external+s.spent,540);self.assertGreaterEqual(min(*s.x,*s.b),0)
    def test_empty(self):
        s=State(initial().x,(F(0),)*10,F(0),F(540));self.assertEqual(step(s,0),s)
    def test_recover(self):
        s=State((F(0),)*9+(F(20),),(F(8),)+(F(0),)*9,F(0),F(0));t=step(s,0);self.assertGreater(t.x[0],0);self.assertGreater(t.spent,0)
    def test_equilibrium(self):
        s=State((F(2),)*10,(F(10),)*10,F(0),F(0));t=step(s,180);self.assertEqual(t.x,s.x);self.assertEqual(t.spent,2)
    def test_partial_input(self):
        s=State(initial().x,(F(0),)*10,F(1,3),F(0));t=step(s,0);self.assertEqual(t.external,0);self.assertEqual(sum(t.b)+t.spent,F(1,3))
    def test_invalid(self):self.assertRaises(ValueError,step,initial(),360)
    def test_no_creation(self):
        s=initial();t=step(s,0,F(0));self.assertEqual(t,s)
if __name__=='__main__':unittest.main(verbosity=2)
