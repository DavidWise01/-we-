import unittest
from wag158 import *
class Tests(unittest.TestCase):
 def setUp(self):self.x=[3,2,1]+[2]*7;self.b=[10]*10;self.p=[True]*10
 def test_short(self):self.assertEqual(relay(self.x,self.b,self.p)[3],((0,1,2),1))
 def test_alternate(self):
    self.p[1]=False;y,b,c,r=relay(self.x,self.b,self.p);self.assertEqual(y,[2]*10);self.assertEqual(c,8);self.assertEqual(r[0],(0,9,8,7,6,5,4,3,2))
 def test_refusal(self):
    self.p[1]=self.p[9]=False;self.assertEqual(relay(self.x,self.b,self.p),(self.x,self.b,0,None))
 def test_receiver_refusal(self):
    self.p[2]=False;self.assertIsNone(relay(self.x,self.b,self.p)[3])
 def test_starved_route(self):
    self.b[1]=0;self.assertEqual(relay(self.x,self.b,self.p)[2],8)
 def test_receipt_replay(self):
    y,b,c,r=relay(self.x,self.b,self.p);self.assertEqual(relay(self.x,self.b,self.p),(y,b,c,r));self.assertEqual(sum(b)+c,sum(self.b))
 def test_partial(self):
    self.b[0]=F(1,2);y,b,c,r=relay(self.x,self.b,self.p);self.assertEqual(y[:3],[F(5,2),2,F(3,2)]);self.assertEqual(c,1)
 def test_sweep(self):
    x=[F(8 if n==-5 else 12 if n==5 else 0) for n in N];b=[F(54)]*10;spent=0
    for k in range(360):
        old=sum((v-2)**2 for v in x);x,b,c,r=relay(x,b,[True]*10);spent+=c
        self.assertEqual(sum(x)+6,26);self.assertEqual(sum(b)+spent,540);self.assertLessEqual(sum((v-2)**2 for v in x),old)
    self.assertEqual(x,[2]*10)
if __name__=='__main__':unittest.main(verbosity=2)
