import unittest
from wag164 import *
class Tests(unittest.TestCase):
 def test_order(self):
    g=genesis();a=proposal(g,[0,1,2]);b=proposal(g,[3,4,5]);self.assertEqual(advance(g,[a,b]),advance(g,[b,a]))
 def test_inherit(self):
    g=genesis();a=advance(g,[proposal(g,[0,1,2])]);b=advance(a,[proposal(a,[3,4,5])]);self.assertEqual(b['x'],[2]*10);self.assertEqual(b['spent'],4);self.assertEqual(b['parent'],digest(a))
 def test_stale(self):
    g=genesis();q=proposal(g,[0,1,2]);a=advance(g,[q]);self.assertRaises(ValueError,advance,a,[q])
 def test_overlap(self):
    g=genesis();q=proposal(g,[0,1,2]);self.assertRaises(ValueError,advance,g,[q,q])
 def test_tamper(self):
    g=genesis();q=[proposal(g,[0,1,2])];a=advance(g,q);a['spent']+=1;self.assertRaises(ValueError,verify,[(q,a)])
 def test_replay(self):
    p=genesis();chain=[]
    for n in range(164):
      q=[proposal(p,[0,1,2])] if n==0 else [proposal(p,[3,4,5])] if n==1 else []
      t=advance(p,q);chain.append((q,t));p=t
    self.assertEqual(verify(chain),p);self.assertEqual(p['generation'],164)
 def test_immutable_input(self):
    g=genesis();d=digest(g);advance(g,[proposal(g,[0,1,2])]);self.assertEqual(digest(g),d)
 def test_empty(self):
    g=genesis();a=advance(g,[]);self.assertEqual(a['x'],g['x']);self.assertEqual(a['b'],g['b']);self.assertNotEqual(digest(a),digest(g))
if __name__=='__main__':unittest.main(verbosity=2)
