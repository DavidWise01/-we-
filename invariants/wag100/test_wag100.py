import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from wag100 import Gate,signed,digest
class Tests(unittest.TestCase):
 def setUp(self):
  self.ks={x:K.generate() for x in 'ABC'}; self.a=K.generate(); self.w=K.generate()
  self.g=Gate({x:k.public_key() for x,k in self.ks.items()},{x:x for x in self.ks},self.a.public_key(),self.w.public_key(),'pin100')
  self.o=signed(self.w,{'tag':'observation','key':'W1','claimed':1}); self.r=signed(self.a,{'tag':'revoke','key':'W1','effective':5})
 def views(self,seen=4,head=6):
  return {x:signed(k,{'tag':'chronology','observer':x,'pin':'pin100','obs':digest(self.o),'rev':digest(self.r),'seen':seen,'cutoff':5,'head':head}) for x,k in self.ks.items()}
 def check(self,v):return self.g.evaluate(self.o,self.r,v)
 def test_prior(self):self.assertEqual(self.check(self.views()),'LOCAL_HISTORICAL_ELIGIBLE')
 def test_equal(self):self.assertEqual(self.check(self.views(5)),'HOLD_REVOKED')
 def test_backdate(self):self.assertEqual(self.check(self.views(6)),'HOLD_REVOKED')
 def test_missing(self):v=self.views();v.pop('C');self.assertEqual(self.check(v),'HOLD_MISSING')
 def test_tamper(self):v=self.views();v['A']['body']['seen']=2;self.assertEqual(self.check(v),'HOLD_SIGNATURE')
 def test_stale(self):self.assertEqual(self.check(self.views(head=3)),'HOLD_STALE')
 def test_disagree(self):v=self.views();v['C']=self.views(3)['C'];self.assertEqual(self.check(v),'HOLD_DISAGREEMENT')
 def test_replay(self):v=self.views();v['B']=v['A'];self.assertEqual(self.check(v),'HOLD_SIGNATURE')
 def test_pin(self):v=self.views();self.g.pin='new';self.assertEqual(self.check(v),'HOLD_BINDING')
 def test_rev_change(self):v=self.views();self.r=signed(self.a,{'tag':'revoke','key':'W1','effective':6});self.assertEqual(self.check(v),'HOLD_BINDING')
 def test_shared_root(self):
  with self.assertRaises(ValueError):Gate(self.g.keys,dict.fromkeys('ABC','one'),self.a.public_key(),self.w.public_key(),'pin')
 def test_shared_key(self):
  with self.assertRaises(ValueError):Gate(dict.fromkeys('ABC',self.a.public_key()),{x:x for x in 'ABC'},self.a.public_key(),self.w.public_key(),'pin')
if __name__=='__main__':unittest.main()
