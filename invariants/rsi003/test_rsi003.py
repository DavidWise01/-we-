import unittest
from rsi003 import trial,experiment
class TestTransfer(unittest.TestCase):
 def test_repeatable(self): self.assertEqual(experiment(),experiment())
 def test_empty_equal_budget(self): self.assertEqual(trial([],True)[0],trial([],False)[0])
 def test_audits(self):
  for r in experiment().values():
   for energies,verified in r.values(): self.assertTrue(verified)
 def test_bounds(self):
  for r in experiment().values():
   for energies,_ in r.values(): self.assertEqual(len(energies),9);self.assertTrue(all(0<=x<=100 for x in energies))
 def test_equal_parity(self):
  for r in experiment().values():
   for e,_ in r.values(): self.assertEqual(len(set(e[::2])),1);self.assertEqual(len(set(e[1::2])),1)
 def test_invalid(self):
  with self.assertRaises(ValueError): trial([9],True)
if __name__=='__main__': unittest.main()
