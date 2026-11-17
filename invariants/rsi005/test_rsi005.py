import unittest
from rsi005 import Watch,TEAMS,experiment
class Tests(unittest.TestCase):
 def test_roles(self):
  e=Watch();e.step([4]*9,[4]*9);self.assertEqual(e.events[0][1],('UP','REST','REPLAY')*3)
 def test_rotation(self):
  e=Watch()
  for _ in range(3):e.step([4]*9,[4]*9)
  self.assertEqual(sorted(i for x in e.events for i in x[2]),list(range(9)))
 def test_replay(self):
  e=Watch();e.step([8]*9,[8]*9);self.assertEqual(e.events[0][3],{2:4,5:4,8:4})
 def test_three_up(self):
  e=Watch()
  for _ in range(12):e.step([4]*9,[4]*9)
  self.assertTrue(all(len(x[2])==3 for x in e.events))
 def test_baseline(self):
  for x in experiment().values():self.assertEqual(x['watch']['energy'],x['awake']['energy'])
 def test_audit(self):
  for x in experiment().values():self.assertTrue(x['watch']['audit'])
 def test_repeat(self):self.assertEqual(experiment(),experiment())
 def test_geometry(self):self.assertEqual(Watch().geometry,('torroid','box')*4+('torroid',))
if __name__=='__main__':unittest.main()
