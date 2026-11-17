import unittest
from rsi006 import Handoff,experiment
class Tests(unittest.TestCase):
 def test_normal(self):
  a=Handoff();a.step([4]*9,[4]*9);self.assertEqual(len(a.events[-1][2]),3);self.assertEqual(a.work,87)
 def test_local_wake(self):
  a=Handoff();a.step([8]*3+[4]*6,[8]*3+[4]*6);self.assertEqual(len(a.events[-1][2]),5)
 def test_global_wake(self):
  a=Handoff();a.step([8]*9,[8]*9);self.assertEqual(len(a.events[-1][2]),9)
 def test_calm(self):
  a=Handoff()
  for _ in range(3):a.step([8]*9,[8]*9)
  self.assertEqual(len(a.events[-1][2]),3)
 def test_handoff(self):
  a=Handoff();a.step([4]*9,[4]*9,unavailable=(0,));self.assertIn(1,a.events[-1][2]);self.assertNotIn(0,a.events[-1][2])
 def test_audit(self):self.assertTrue(all(r['audit'] for r in experiment().values()))
 def test_repeat(self):self.assertEqual(experiment(),experiment())
 def test_bad_input(self):
  with self.assertRaises(ValueError):Handoff().step([4],[4])
if __name__=='__main__':unittest.main()
