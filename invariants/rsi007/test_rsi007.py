import unittest
from rsi007 import *
class Tests(unittest.TestCase):
 def test_axis(self):self.assertEqual(set(AXIS),set(range(-5,6)))
 def test_rotation(self):self.assertEqual({i for t in range(3) for i,r in frame(t,[4]*9,[4]*9)['roles'].items() if r['duty']=='UP'},set(range(9)))
 def test_ephemeral(self):self.assertFalse(valid(frame(0,[4]*9,[4]*9),1))
 def test_peripheral(self):self.assertEqual(frame(0,[4,8,4]+[4]*6,[4]*9)['alerts'],[0])
 def test_normal(self):self.assertEqual(frame(0,[4]*9,[4]*9)['work'],93)
 def test_local(self):self.assertEqual(frame(0,[4,8,4]+[4]*6,[4]*9)['work'],143)
 def test_handoff(self):self.assertEqual(frame(0,[4]*9,[4]*9,(0,))['roles'][1]['duty'],'UP')
 def test_geometry(self):self.assertEqual(frame(0,[4]*9,[4]*9)['roles'][1]['geometry'],'box')
 def test_unique(self):
  for t in range(33):
   r=frame(t,[4]*9,[4]*9)['roles'];self.assertEqual(len({(x['rank'],x['file']) for x in r.values()}),9)
if __name__=='__main__':unittest.main()
