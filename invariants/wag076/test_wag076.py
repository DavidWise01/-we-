"""WAG-076 compact GitHub regression tests; full 43-case local suite is separate."""
import unittest
from dataclasses import replace
from wag076 import Registry,Gate,make_key,sign,demo
class TestSignedAncestry(unittest.TestCase):
 def setUp(self):
  self.a,self.pa=make_key();self.b,self.pb=make_key()
  self.r=[Registry('A','RA','OA','DA','KA',self.pa),Registry('B','RB','OB','DB','KB',self.pb)]
  self.g=Gate(self.r,{'ORG-X'},2,'nonce')
 def claim(self,registry='A',parent='ORG-W',epoch=2,nonce='nonce'):
  return sign(self.a if registry=='A' else self.b,registry,'W4',parent,epoch,nonce)
 def two(self,x='ORG-W',y='ORG-W'):
  self.g.submit(self.claim('A',x))
  return self.g.submit(self.claim('B',y))
 def test_initial_hold(self):self.assertEqual(self.g.status(),'HOLD_INSUFFICIENT_REGISTRIES')
 def test_single_hold(self):self.assertEqual(self.g.submit(self.claim()),'HOLD_INSUFFICIENT_REGISTRIES')
 def test_matching(self):self.assertEqual(self.two(),'ELIGIBLE_DECLARED_ANCESTRY')
 def test_conflict(self):self.assertEqual(self.two('ORG-W','ORG-X'),'HOLD_REGISTRY_CONFLICT')
 def test_excluded(self):self.assertEqual(self.two('ORG-X','ORG-X'),'HOLD_COMPROMISED_ANCESTRY')
 def test_equivocation(self):
  self.g.submit(self.claim());self.g.submit(self.claim(parent='ORG-X'))
  self.assertEqual(self.g.status(),'QUARANTINE_EQUIVOCATION')
 def test_forgery(self):
  with self.assertRaises(ValueError):self.g.submit(replace(self.claim(),signature=b'\\0'*64))
 def test_scope(self):
  with self.assertRaises(ValueError):self.g.submit(self.claim(epoch=3))
 def test_nonce(self):
  with self.assertRaises(ValueError):self.g.submit(self.claim(nonce='other'))
 def test_duplicate_registry(self):
  with self.assertRaises(ValueError):Gate([self.r[0],replace(self.r[1],name='A')],set(),2,'nonce')
 def test_duplicate_domain(self):
  with self.assertRaises(ValueError):Gate([self.r[0],replace(self.r[1],domain='DA')],set(),2,'nonce')
 def test_duplicate_operator(self):
  with self.assertRaises(ValueError):Gate([self.r[0],replace(self.r[1],operator='OA')],set(),2,'nonce')
 def test_duplicate_ancestry(self):
  with self.assertRaises(ValueError):Gate([self.r[0],replace(self.r[1],ancestor='RA')],set(),2,'nonce')
 def test_duplicate_key_identity(self):
  with self.assertRaises(ValueError):Gate([self.r[0],replace(self.r[1],key_id='KA')],set(),2,'nonce')
 def test_replayed_one_registry(self):
  self.g.submit(self.claim());self.g.submit(self.claim())
  self.assertEqual(self.g.status(),'HOLD_INSUFFICIENT_REGISTRIES')
 def test_ledger(self):self.two();self.assertTrue(self.g.verify_history())
 def test_tampering(self):
  self.two();self.g.records[1]['data']['signature']='fake';self.assertFalse(self.g.verify_history())
 def test_freeze(self):
  self.two();self.assertEqual(self.g.freeze(),'ELIGIBLE_DECLARED_ANCESTRY')
  self.assertEqual(len(self.g.records),4)
 def test_rejected_atomicity(self):
  n=len(self.g.records)
  with self.assertRaises(ValueError):self.g.submit(self.claim(nonce='wrong'))
  self.assertEqual(n,len(self.g.records))
 def test_demo(self):
  d=demo()
  self.assertEqual(d['matching'],'ELIGIBLE_DECLARED_ANCESTRY')
  self.assertEqual(d['conflicting'],'HOLD_REGISTRY_CONFLICT')
  self.assertTrue(d['audit_valid'])
  self.assertEqual(d['records'],[4,4])
if __name__=='__main__':unittest.main()
