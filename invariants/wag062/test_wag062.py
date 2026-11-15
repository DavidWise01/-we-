import unittest
from math import pi
from wag062 import Witness,Surface,GeometricGate,demo
class Tests(unittest.TestCase):
 def w(self):return [Witness(str(i),f'origin{i}',2*pi*i/3) for i in range(3)]
 def test_demo(self):self.assertTrue(demo()[0].verify())
 def test_three(self):
  with self.assertRaises(ValueError):GeometricGate(self.w()[:2])
 def test_shared_identity(self):
  w=self.w();w[2]=Witness(w[1].identity,'other',4*pi/3)
  with self.assertRaises(ValueError):GeometricGate(w)
 def test_shared_ancestor(self):
  w=self.w();w[2]=Witness('2',w[0].ancestor,4*pi/3)
  with self.assertRaises(ValueError):GeometricGate(w)
 def test_angles(self):
  w=self.w();w[2]=Witness('2','origin2',pi)
  with self.assertRaises(ValueError):GeometricGate(w)
 def test_torus_distinct(self):self.assertEqual(GeometricGate(self.w()).deform(Surface(2,2,1,1))['topology'],'torus')
 def test_sphere_topology(self):self.assertEqual(GeometricGate(self.w()).deform(Surface(2,2,2,0))['topology'],'sphere-like')
 def test_sphere_shape(self):self.assertEqual(GeometricGate(self.w()).deform(Surface(1,1,1,0))['shape'],'sphere')
 def test_spheroid(self):self.assertEqual(GeometricGate(self.w()).deform(Surface(2,2,3,0))['shape'],'spheroid')
 def test_ellipsoid(self):self.assertEqual(GeometricGate(self.w()).deform(Surface(2,3,4,0))['shape'],'triaxial ellipsoid')
 def test_invalid_axes(self):
  with self.assertRaises(ValueError):GeometricGate(self.w()).deform(Surface(0,2,3,0))
 def test_invalid_genus(self):
  with self.assertRaises(ValueError):GeometricGate(self.w()).deform(Surface(1,2,3,2))
 def test_provenance_stable(self):
  g=GeometricGate(self.w());g.deform(Surface(2,3,4,0));self.assertEqual([w.ancestor for w in g.witnesses],[f'origin{i}' for i in range(3)])
 def test_append_only(self):
  g=GeometricGate(self.w());g.deform(Surface(1,2,3,0));self.assertEqual(len(g.history),2)
 def test_tamper(self):
  g=GeometricGate(self.w());g.deform(Surface(1,2,3,0));g.history[1]['data']['genus']=1;self.assertFalse(g.verify())
 def test_no_automatic_topology_change(self):
  g=GeometricGate(self.w());self.assertEqual(g.deform(Surface(1,1,1,1))['topology'],'torus')
if __name__=='__main__':unittest.main()