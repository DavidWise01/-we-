import unittest
from wag063 import Witness,PinchAudit,demo
W=(Witness("W1","A",0),Witness("W2","B",120),Witness("W3","C",240))
class Tests(unittest.TestCase):
 def setUp(self):self.a=PinchAudit(W)
 def test_demo(self):self.assertTrue(demo().verify())
 def test_six_stages(self):self.assertEqual(len(demo().stages),6)
 def test_three_origins(self):self.assertEqual(len({w.ancestry for w in self.a.witnesses}),3)
 def test_duplicate_witness(self):
  with self.assertRaises(ValueError):PinchAudit((W[0],W[0],W[2]))
 def test_duplicate_ancestry(self):
  with self.assertRaises(ValueError):PinchAudit((W[0],Witness("W2","A",120),W[2]))
 def test_two_witnesses(self):
  with self.assertRaises(ValueError):PinchAudit(W[:2])
 def test_wrong_angles(self):
  with self.assertRaises(ValueError):PinchAudit((W[0],Witness("W2","B",110),W[2]))
 def test_rotation(self):PinchAudit((Witness("W1","A",60),Witness("W2","B",180),Witness("W3","C",300)))
 def test_torus_genus(self):self.assertEqual(self.a.step(.4).genus,1)
 def test_hole_radius(self):self.assertAlmostEqual(self.a.step(.5).hole_radius,.5)
 def test_singularity(self):self.assertIsNone(self.a.step(1).genus)
 def test_surgery_requires_pinch(self):
  with self.assertRaises(ValueError):self.a.close()
 def test_close_genus(self):self.a.step(1);self.assertEqual(self.a.close().genus,0)
 def test_no_repeat_surgery(self):
  self.a.step(1);self.a.close()
  with self.assertRaises(ValueError):self.a.close()
 def test_no_retrograde(self):
  self.a.step(.6)
  with self.assertRaises(ValueError):self.a.step(.5)
 def test_no_duplicate_step(self):
  self.a.step(.6)
  with self.assertRaises(ValueError):self.a.step(.6)
 def test_invalid_pinch(self):
  with self.assertRaises(ValueError):self.a.step(2)
 def test_nan_pinch(self):
  with self.assertRaises(ValueError):self.a.step(float("nan"))
 def test_bool_pinch(self):
  with self.assertRaises(ValueError):self.a.step(True)
 def test_invalid_radius(self):
  with self.assertRaises(ValueError):PinchAudit(W,hole_radius=0)
 def test_ancestry(self):self.assertTrue(demo().ancestry_preserved())
 def test_ledger_count(self):self.assertEqual(len(demo().ledger),7)
 def test_history_tampering(self):
  a=demo();a.ledger[1]["data"]["pinch"]=.99;self.assertFalse(a.verify())
 def test_rejection_atomic(self):
  n=len(self.a.ledger)
  with self.assertRaises(ValueError):self.a.step(-1)
  self.assertEqual(n,len(self.a.ledger))
if __name__=="__main__":unittest.main()
