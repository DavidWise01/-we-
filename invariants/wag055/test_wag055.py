import unittest
from dataclasses import replace
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from wag055 import RecoverySeal,Identity,Attestation,canonical,demo

class Tests(unittest.TestCase):
 def setUp(self):
  self.keys=[Ed25519PrivateKey.generate() for _ in range(3)]
  self.identities=[Identity(f'w{i}',f'r{i}',f'd{i}',k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()) for i,k in enumerate(self.keys)]
  self.a=RecoverySeal(self.identities)
  self.proofs=[Attestation(f'w{i}',k.sign(canonical(self.a.payload())).hex()) for i,k in enumerate(self.keys)]
  self.receipt={'service':'fixture','digest':self.a.candidate_digest()}
  self.verifier=lambda r,d:r.get('service')=='fixture' and r.get('digest')==d
 def certify(self):return self.a.certify(self.proofs,anchor_receipt=self.receipt,anchor_verifier=self.verifier)
 def test_demo(self):self.assertEqual(demo()[1],'CERTIFIED')
 def test_demo_chain(self):self.assertTrue(demo()[0].verify_ledger())
 def test_certify(self):self.assertEqual(self.certify(),'CERTIFIED')
 def test_certificate_parent(self):self.certify();self.assertEqual(self.a.certificate['parent'],'C0')
 def test_three_signers(self):
  with self.assertRaises(ValueError):self.a.certify(self.proofs[:2])
 def test_duplicate_signer(self):
  with self.assertRaises(ValueError):self.a.certify([self.proofs[0]]*3)
 def test_wrong_signature(self):
  p=list(self.proofs);p[0]=replace(p[0],signature_hex=self.keys[1].sign(canonical(self.a.payload())).hex())
  with self.assertRaises(ValueError):self.a.certify(p)
 def test_unknown_signer(self):
  p=list(self.proofs);p[0]=replace(p[0],signer='other')
  with self.assertRaises(ValueError):self.a.certify(p)
 def test_revoked(self):
  self.a.identities['w1']=replace(self.a.identities['w1'],revoked=True)
  with self.assertRaises(ValueError):self.certify()
 def test_shared_root(self):
  self.a.identities['w1']=replace(self.a.identities['w1'],root='r0')
  with self.assertRaises(ValueError):self.certify()
 def test_shared_domain(self):
  self.a.identities['w1']=replace(self.a.identities['w1'],domain='d0')
  with self.assertRaises(ValueError):self.certify()
 def test_no_anchor(self):self.assertEqual(self.a.certify(self.proofs),'HOLD_EXTERNAL_ANCHOR')
 def test_no_anchor_is_not_certified(self):self.a.certify(self.proofs);self.assertIsNone(self.a.certificate)
 def test_bad_anchor(self):
  with self.assertRaises(ValueError):self.a.certify(self.proofs,anchor_receipt={'service':'bad'},anchor_verifier=self.verifier)
 def test_bad_anchor_no_mutation(self):
  count=len(self.a.records)
  with self.assertRaises(ValueError):self.a.certify(self.proofs,anchor_receipt={'service':'bad'},anchor_verifier=self.verifier)
  self.assertEqual(len(self.a.records),count)
 def test_repeated_certification(self):
  self.certify()
  with self.assertRaises(ValueError):self.certify()
 def test_hold_is_final(self):
  self.a.certify(self.proofs)
  with self.assertRaises(ValueError):self.certify()
 def test_changed_payload_invalidates_signature(self):
  self.a.recovered_id='C2'
  with self.assertRaises(ValueError):self.certify()
 def test_invalid_lineage(self):
  with self.assertRaises(ValueError):RecoverySeal(self.identities,original_id='C0',recovered_id='C0')
 def test_reused_fallback(self):
  with self.assertRaises(ValueError):RecoverySeal(self.identities,fallback_root='E0')
 def test_ledger_tamper(self):
  self.certify();self.a.records[1]['payload']['parent']='tamper';self.assertFalse(self.a.verify_ledger())
 def test_no_inferred_identity(self):self.assertEqual(len(self.a.identities),3)
 def test_signature_is_ed25519(self):self.assertEqual(len(bytes.fromhex(self.proofs[0].signature_hex)),64)
 def test_untampered(self):self.certify();self.assertTrue(self.a.verify_ledger())

if __name__=='__main__':unittest.main()
