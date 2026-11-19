import unittest
from wag154 import *

class Tests(unittest.TestCase):
    def test_sweep(self):
        s=Ledger()
        for a in range(360):
            s,i,p,m=step(s,a)
            self.assertEqual(s.total(),540)
            self.assertEqual(p,m)
            self.assertGreaterEqual(min(s.external,s.reserve,s.dissipated),0)
        self.assertEqual(s,Ledger(F(0),F(0),F(540)))
    def test_empty(self):self.assertEqual(step(Ledger(F(0)),180)[1:],(0,0,0))
    def test_partial(self):self.assertEqual(step(Ledger(F(1,3)),180)[0],Ledger(F(0),F(0),F(1,3)))
    def test_no_absorption(self):self.assertEqual(step(Ledger(),0,F(0))[0],Ledger())
    def test_stored(self):self.assertEqual(step(Ledger(F(0),F(3)),180)[0],Ledger(F(0),F(1),F(2)))
    def test_dissipation_not_recycled(self):self.assertEqual(step(Ledger(F(0),F(0),F(540)),180)[0],Ledger(F(0),F(0),F(540)))
    def test_invalid(self):self.assertRaises(ValueError,step,Ledger(),360)
    def test_negative(self):self.assertRaises(ValueError,step,Ledger(),0,F(-1))
    def test_all_phases(self):
        for a in range(360):
            s,i,p,m=step(Ledger(),a)
            self.assertEqual(p+m,s.dissipated)
            self.assertEqual(s.external,538)
    def test_zero_net(self):self.assertEqual(step(Ledger(),180)[2:],(1,1))

if __name__=='__main__':unittest.main(verbosity=2)
