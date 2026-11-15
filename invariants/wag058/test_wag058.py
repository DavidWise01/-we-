import unittest
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from wag058 import Auditor,Witness,Head,root,proof,verify,msg,gossipmsg,H,demo
pub=lambda k:k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()
class Tests(unittest.TestCase):
 def setUp(self):
  self.op=Ed25519PrivateKey.generate();self.a=Auditor('LOG',pub(self.op))
  self.values=[('e'+str(i)).encode() for i in range(8)]
  self.keys={}
 def register(self,i):
  name='W'+str(i);k=Ed25519PrivateKey.generate();self.keys[name]=k
  self.a.register(Witness(name,'root'+str(i),'domain'+str(i),pub(k)))
 def report(self,i,n,values=None):
  name='W'+str(i);values=values or self.values;r=root(values[:n]).hex()
  s=self.op.sign(msg('LOG',n,r,10)).hex();h=Head('LOG',n,r,10,s)
  hh=H(msg('LOG',n,r,10)+bytes.fromhex(s)).hex()
  self.a.submit(name,h,11,self.keys[name].sign(gossipmsg(name,hh,11)).hex())
 def three(self,sizes=(3,8,8)):
  for i,n in enumerate(sizes,1):self.register(i);self.report(i,n)
 def test_demo(self):
  a,r=demo();self.assertEqual(r['status'],'CONSISTENT_RECEIVED_VIEWS');self.assertEqual(len(a.events),9)
 def test_full_size_matrix(self):
  for n in range(2,24):
   vals=[bytes([i]) for i in range(n)]
   for m in range(1,n):
    self.assertTrue(verify(m,n,root(vals[:m]).hex(),root(vals).hex(),proof(vals,m)))
 def test_changed_proof(self):
  p=proof(self.values,3);p[0]='00'*32
  self.assertFalse(verify(3,8,root(self.values[:3]).hex(),root(self.values).hex(),p))
 def test_changed_old_root(self):
  self.assertFalse(verify(3,8,'ee'*32,root(self.values).hex(),proof(self.values,3)))
 def test_zero_size(self):
  self.assertFalse(verify(0,8,'00'*32,'11'*32,[]))
 def test_equal_valid(self):
  self.assertTrue(verify(1,1,'11'*32,'11'*32,[]))
 def test_equal_invalid(self):
  self.assertFalse(verify(1,1,'11'*32,'22'*32,[]))
 def test_valid_gossip(self):
  self.three();self.a.add_proof(3,8,root(self.values[:3]).hex(),root(self.values).hex(),proof(self.values,3))
  self.assertEqual(self.a.decide()['status'],'CONSISTENT_RECEIVED_VIEWS')
 def test_missing_proof(self):
  self.three();self.assertEqual(self.a.decide()['status'],'HOLD_INCOMPLETE')
 def test_same_size_fork(self):
  self.register(1);self.report(1,3)
  self.register(2);other=self.values.copy();other[0]=b'altered';self.report(2,3,other)
  self.register(3);self.report(3,3)
  self.assertEqual(self.a.decide()['status'],'QUARANTINE_CONFLICT')
 def test_invalid_proof_quarantine(self):
  self.three();self.a.add_proof(3,8,root(self.values[:3]).hex(),root(self.values).hex(),['aa'*32])
  self.assertEqual(self.a.decide()['status'],'QUARANTINE_CONFLICT')
 def test_incomplete_quorum(self):
  self.register(1);self.report(1,3)
  self.assertEqual(self.a.decide()['status'],'HOLD_INCOMPLETE')
 def test_duplicate_witness(self):
  self.register(1)
  with self.assertRaises(ValueError):self.register(1)
 def test_shared_root(self):
  self.register(1)
  with self.assertRaises(ValueError):self.a.register(Witness('W2','root1','diff',pub(Ed25519PrivateKey.generate())))
 def test_shared_domain(self):
  self.register(1)
  with self.assertRaises(ValueError):self.a.register(Witness('W2','diff','domain1',pub(Ed25519PrivateKey.generate())))
 def test_invalid_log_signature(self):
  self.register(1);h=Head('LOG',3,root(self.values[:3]).hex(),10,'00'*64)
  with self.assertRaises(ValueError):self.a.submit('W1',h,11,'00'*64)
 def test_invalid_gossip_signature(self):
  self.register(1);r=root(self.values[:3]).hex();h=Head('LOG',3,r,10,self.op.sign(msg('LOG',3,r,10)).hex())
  with self.assertRaises(ValueError):self.a.submit('W1',h,11,'00'*64)
 def test_wrong_log(self):
  self.register(1)
  with self.assertRaises(ValueError):self.a.submit('W1',Head('OTHER',3,'00'*32,10,''),11,'')
 def test_gossip_replay(self):
  self.register(1);self.report(1,3)
  with self.assertRaises(ValueError):self.report(1,3)
 def test_time_order(self):
  self.register(1)
  with self.assertRaises(ValueError):self.a.submit('W1',Head('LOG',3,'00'*32,10,''),9,'')
 def test_duplicate_decision(self):
  self.three();self.a.decide()
  with self.assertRaises(ValueError):self.a.decide()
 def test_duplicate_proof(self):
  vals=self.values;self.a.add_proof(3,8,root(vals[:3]).hex(),root(vals).hex(),proof(vals,3))
  with self.assertRaises(ValueError):self.a.add_proof(3,8,root(vals[:3]).hex(),root(vals).hex(),proof(vals,3))
 def test_tamper(self):
  self.register(1);self.a.events[1]['data']['root']='altered';self.assertFalse(self.a.verify_history())
 def test_atomic_invalid_report(self):
  n=len(self.a.events)
  with self.assertRaises(ValueError):self.a.submit('unregistered',Head('LOG',3,'00'*32,10,''),11,'')
  self.assertEqual(n,len(self.a.events))
if __name__=='__main__':unittest.main()
