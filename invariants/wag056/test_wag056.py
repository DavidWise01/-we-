import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from wag056 import CheckpointAudit,Anchor,inclusion_root,receipt_message,demonstration,leaf_hash,node_hash
class Tests(unittest.TestCase):
 def setUp(self):self.a=CheckpointAudit({'checkpoint':'C1','parent':'C0'},'S2')
 def make(self,i,epoch=10,operator=None,domain=None):
  k=Ed25519PrivateKey.generate();name=f'A{i}';root=inclusion_root(self.a.cert_hash,())
  pub=k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()
  sig=k.sign(receipt_message(name,self.a.cert_hash,root,epoch)).hex()
  return Anchor(name,operator or f'op{i}',domain or f'd{i}',pub,root,sig,epoch)
 def populate(self):
  for i in (1,2,3):self.a.anchor(self.make(i))
  self.a.issue()
 def test_demo(self):
  a,b,c=demonstration();self.assertEqual(b['current'],'CURRENT');self.assertEqual(c['current'],'HOLD_REVOKED_SIGNER');self.assertTrue(a.verify_chain())
 def test_history_preserved(self):
  self.populate();self.a.revoke('S2',12,'reason');self.assertEqual(self.a.trust(13)['historical'],'SEALED_AT_ISSUANCE')
 def test_before_revocation(self):
  self.populate();self.a.revoke('S2',12,'reason');self.assertEqual(self.a.trust(11)['current'],'CURRENT')
 def test_anchor_revocation(self):
  self.populate();self.a.revoke('A1',12,'reason');self.assertEqual(self.a.trust(13)['current'],'HOLD_ANCHOR_QUORUM')
 def test_anchor_pre_revocation(self):
  self.populate();self.a.revoke('A1',12,'reason');self.assertEqual(self.a.trust(11)['current'],'CURRENT')
 def test_no_issue(self):self.assertEqual(self.a.trust(0)['current'],'HOLD')
 def test_insufficient_anchors(self):
  self.a.anchor(self.make(1))
  with self.assertRaises(ValueError):self.a.issue()
 def test_duplicate_anchor(self):
  self.a.anchor(self.make(1))
  with self.assertRaises(ValueError):self.a.anchor(self.make(1))
 def test_shared_operator(self):
  self.a.anchor(self.make(1))
  with self.assertRaises(ValueError):self.a.anchor(self.make(2,operator='op1'))
 def test_shared_domain(self):
  self.a.anchor(self.make(1))
  with self.assertRaises(ValueError):self.a.anchor(self.make(2,domain='d1'))
 def test_wrong_root(self):
  a=self.make(1)
  with self.assertRaises(ValueError):self.a.anchor(Anchor(a.name,a.operator,a.failure_domain,a.public_key_hex,'0'*64,a.signature_hex,a.epoch))
 def test_bad_signature(self):
  a=self.make(1)
  with self.assertRaises(ValueError):self.a.anchor(Anchor(a.name,a.operator,a.failure_domain,a.public_key_hex,a.root_hex,'0'*64,a.epoch))
 def test_bad_key(self):
  a=self.make(1)
  with self.assertRaises(ValueError):self.a.anchor(Anchor(a.name,a.operator,a.failure_domain,'bad',a.root_hex,a.signature_hex,a.epoch))
 def test_no_post_issue_anchor(self):
  self.populate()
  with self.assertRaises(ValueError):self.a.anchor(self.make(4))
 def test_double_issue(self):
  self.populate()
  with self.assertRaises(ValueError):self.a.issue()
 def test_unknown_revocation(self):
  self.populate()
  with self.assertRaises(ValueError):self.a.revoke('unknown',12,'reason')
 def test_duplicate_revocation(self):
  self.populate();self.a.revoke('A1',12,'reason')
  with self.assertRaises(ValueError):self.a.revoke('A1',13,'other')
 def test_revocation_reason(self):
  self.populate()
  with self.assertRaises(ValueError):self.a.revoke('S2',12,'')
 def test_revocation_before_anchor(self):
  self.populate()
  with self.assertRaises(ValueError):self.a.revoke('A1',1,'reason')
 def test_merkle_path(self):
  other='22'*32;root=inclusion_root(self.a.cert_hash,(('L',other),))
  self.assertEqual(root,node_hash(bytes.fromhex(other),leaf_hash(self.a.cert_hash)).hex())
 def test_invalid_proof(self):
  with self.assertRaises(ValueError):inclusion_root(self.a.cert_hash,(('wrong','0'*64),))
 def test_bad_epoch(self):
  with self.assertRaises(ValueError):self.a.trust(-1)
 def test_tampering(self):
  self.populate();self.a.events[1]['data']['operator']='attacker';self.assertFalse(self.a.verify_chain())
 def test_rejected_atomic(self):
  n=len(self.a.events);a=self.make(1)
  with self.assertRaises(ValueError):self.a.anchor(Anchor(a.name,a.operator,a.failure_domain,a.public_key_hex,'f'*64,a.signature_hex,a.epoch))
  self.assertEqual(len(self.a.events),n)
if __name__=='__main__':unittest.main()
