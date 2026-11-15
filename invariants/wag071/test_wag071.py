import unittest
from dataclasses import replace
from wag071 import Gate,Witness,Report,sign,demo,hashof,payload
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
def make(verified=True):
 k=[Ed25519PrivateKey.from_private_bytes(bytes([i])*32) for i in (3,4,5)]
 ws=[Witness('W'+str(i+1),chr(65+i),'domain-'+str(i+1),k[i].public_key().public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)) for i in range(3)]
 return Gate(ws,2,hashof('expected'),verified),k
class Tests(unittest.TestCase):
 def setUp(self):self.g,self.keys=make()
 def submit(self,i,snapshot=None,nonce=None):return self.g.submit(sign(self.keys[i],'W'+str(i+1),2,snapshot or self.g.snapshot,nonce or 'nonce-'+str(i)))
 def test_01_initial_hold(self):self.assertEqual(self.g.status(),'HOLD_INCOMPLETE_QUORUM')
 def test_02_one_hold(self):self.submit(0);self.assertEqual(self.g.status(),'HOLD_INCOMPLETE_QUORUM')
 def test_03_two_hold(self):self.submit(0);self.submit(1);self.assertEqual(self.g.status(),'HOLD_INCOMPLETE_QUORUM')
 def test_04_three_accept(self):
  for i in range(3):self.submit(i)
  self.assertEqual(self.g.status(),'LOCAL_SIGNED_QUORUM_ACCEPTED')
 def test_05_conflict(self):self.submit(0);self.submit(1);self.submit(2,hashof('other'));self.assertEqual(self.g.status(),'QUARANTINE_SNAPSHOT_CONFLICT')
 def test_06_conflict_sticky(self):self.submit(0,hashof('other'));self.submit(1);self.submit(2);self.assertEqual(self.g.status(),'QUARANTINE_SNAPSHOT_CONFLICT')
 def test_07_unverified(self):
  g,k=make(False)
  for i in range(3):g.submit(sign(k[i],'W'+str(i+1),2,g.snapshot,str(i)))
  self.assertEqual(g.status(),'HOLD_UNVERIFIED_INFRASTRUCTURE')
 def test_08_old_epoch(self):
  with self.assertRaises(ValueError):self.g.submit(sign(self.keys[0],'W1',1,self.g.snapshot,'old'))
 def test_09_future_epoch(self):
  with self.assertRaises(ValueError):self.g.submit(sign(self.keys[0],'W1',3,self.g.snapshot,'future'))
 def test_10_wrong_key(self):
  with self.assertRaises(ValueError):self.g.submit(sign(self.keys[1],'W1',2,self.g.snapshot,'wrongkey'))
 def test_11_mutated_hash(self):
  r=sign(self.keys[0],'W1',2,self.g.snapshot,'n')
  with self.assertRaises(ValueError):self.g.submit(replace(r,snapshot_hash=hashof('other')))
 def test_12_mutated_name(self):
  r=sign(self.keys[0],'W1',2,self.g.snapshot,'n')
  with self.assertRaises(ValueError):self.g.submit(replace(r,name='W2'))
 def test_13_mutated_nonce(self):
  r=sign(self.keys[0],'W1',2,self.g.snapshot,'n')
  with self.assertRaises(ValueError):self.g.submit(replace(r,nonce='m'))
 def test_14_duplicate_witness(self):
  self.submit(0)
  with self.assertRaises(ValueError):self.g.submit(sign(self.keys[0],'W1',2,self.g.snapshot,'second'))
 def test_15_replay_nonce(self):
  self.submit(0)
  with self.assertRaises(ValueError):self.g.submit(sign(self.keys[1],'W2',2,self.g.snapshot,'nonce-0'))
 def test_16_unknown_name(self):
  with self.assertRaises(ValueError):self.g.submit(sign(self.keys[0],'W9',2,self.g.snapshot,'n'))
 def test_17_empty_nonce(self):
  with self.assertRaises(ValueError):self.g.submit(sign(self.keys[0],'W1',2,self.g.snapshot,''))
 def test_18_invalid_snapshot(self):
  with self.assertRaises(ValueError):self.g.submit(sign(self.keys[0],'W1',2,'xx','n'))
 def test_19_invalid_report(self):
  with self.assertRaises(ValueError):self.g.submit('not report')
 def test_20_signature_bytes_tamper(self):
  r=sign(self.keys[0],'W1',2,self.g.snapshot,'n')
  with self.assertRaises(ValueError):self.g.submit(replace(r,signature=b'\x00'*64))
 def test_21_no_failed_event(self):
  n=len(self.g.audit)
  with self.assertRaises(ValueError):self.g.submit(sign(self.keys[0],'W1',1,self.g.snapshot,'bad'))
  self.assertEqual(len(self.g.audit),n)
 def test_22_audit_initial(self):self.assertTrue(self.g.audit_ok())
 def test_23_audit_three(self):
  for i in range(3):self.submit(i)
  self.assertTrue(self.g.audit_ok())
 def test_24_audit_tamper(self):self.submit(0);self.g.audit[1]['data']['nonce']='fake';self.assertFalse(self.g.audit_ok())
 def test_25_audit_chain(self):
  for i in range(3):self.submit(i)
  self.assertEqual(len(self.g.audit),4)
 def test_26_duplicate_ancestor(self):
  w=list(self.g.ws);w[1]=replace(w[1],ancestor=w[0].ancestor)
  with self.assertRaises(ValueError):Gate(w,2,self.g.snapshot)
 def test_27_duplicate_domain(self):
  w=list(self.g.ws);w[1]=replace(w[1],domain=w[0].domain)
  with self.assertRaises(ValueError):Gate(w,2,self.g.snapshot)
 def test_28_duplicate_pubkey(self):
  w=list(self.g.ws);w[1]=replace(w[1],public_key=w[0].public_key)
  with self.assertRaises(ValueError):Gate(w,2,self.g.snapshot)
 def test_29_duplicate_name(self):
  w=list(self.g.ws);w[1]=replace(w[1],name=w[0].name)
  with self.assertRaises(ValueError):Gate(w,2,self.g.snapshot)
 def test_30_short_quorum(self):
  with self.assertRaises(ValueError):Gate(self.g.ws[:2],2,self.g.snapshot)
 def test_31_negative_epoch(self):
  with self.assertRaises(ValueError):Gate(self.g.ws,-1,self.g.snapshot)
 def test_32_bad_expected(self):
  with self.assertRaises(ValueError):Gate(self.g.ws,2,'not-sha256')
 def test_33_preserve_conflict_evidence(self):
  self.submit(0);self.submit(1);self.submit(2,hashof('other'));self.assertEqual(len(self.g.reports),3)
 def test_34_report_message_domain(self):self.assertIn(b'WAG-071/SNAPSHOT/v1',payload('W1',2,self.g.snapshot,'n'))
 def test_35_deterministic_snapshot(self):self.assertEqual(hashof({'a':1,'b':2}),hashof({'b':2,'a':1}))
 def test_36_demo_conflict(self):self.assertEqual(demo().status(),'QUARANTINE_SNAPSHOT_CONFLICT')
 def test_37_demo_events(self):self.assertEqual(len(demo().audit),4)
 def test_38_demo_audit(self):self.assertTrue(demo().audit_ok())
 def test_39_empty_ancestor(self):
  w=list(self.g.ws);w[0]=replace(w[0],ancestor='')
  with self.assertRaises(ValueError):Gate(w,2,self.g.snapshot)
 def test_40_empty_domain(self):
  w=list(self.g.ws);w[0]=replace(w[0],domain='')
  with self.assertRaises(ValueError):Gate(w,2,self.g.snapshot)
 def test_41_evidence_count(self):self.assertEqual(len(self.g.reports),0)
 def test_42_independent_signatures(self):
  r1=sign(self.keys[0],'W1',2,self.g.snapshot,'a');r2=sign(self.keys[0],'W1',2,self.g.snapshot,'b')
  self.assertNotEqual(r1.signature,r2.signature)
if __name__=='__main__':unittest.main()
