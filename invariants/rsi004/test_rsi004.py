import unittest
from rsi004 import CyclicEngine,SCHEDULE,experiment,trial
class Test(unittest.TestCase):
 def test_cycle(self):self.assertEqual(len(SCHEDULE),28);self.assertEqual(SCHEDULE[-1],'REM')
 def test_replay(self):
  e=CyclicEngine();[e.step([4]*9,[4]*9) for _ in range(28)];self.assertEqual(e.replay,[21,22,23,24])
 def test_control(self):self.assertEqual(trial([4]*28,False)['replays'],0)
 def test_audit(self):
  for x in experiment().values():
   for y in x.values():self.assertTrue(y['audit'])
 def test_no_free_sleep(self):
  e=CyclicEngine();[e.step([4]*9,[4]*9) for _ in range(28)];self.assertTrue(all(s.energy<=72 for s in e.memory.archive[-1][0].states))
 def test_repeat(self):self.assertEqual(experiment(),experiment())
 def test_identity(self):self.assertEqual(CyclicEngine().geometry,CyclicEngine(False).geometry)
 def test_same_input(self):
  a,b=CyclicEngine(),CyclicEngine(False)
  for i in range(28):a.step([i%9]*9,[i%9]*9);b.step([i%9]*9,[i%9]*9)
  self.assertEqual([x[3] for x in a.events],[x[3] for x in b.events])
