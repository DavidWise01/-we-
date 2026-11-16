import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from wag082 import RecoveryGate,Observer,Hold,digest,sign_bundle
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.keys={n:Ed25519PrivateKey.generate() for n in ('W1','W2','W3')}
  self.obs=[Observer(n,'ancestor-'+n,'domain-'+n,k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)) for n,k in self.keys.items()]
  self.db=Path(self.tmp.name)/'db.sqlite';self.anchors=Path(self.tmp.name)/'anchors.txt'
  self.g=RecoveryGate(self.db,self.anchors,self.obs);self.r0=digest('a');self.r1=digest('b')
 def anchor(self,e=0,s=3,r=None,keys=None):
  r=r or self.r0;es=self.g.chain();p=es[-1]['hash'] if es else '0'*64
  return self.g.append_anchor(e,s,r,sign_bundle(keys or self.keys,e,s,r,p))
 def seed(self):self.g.set_local(0,3,self.r0);self.anchor()
 def test_no_local(self):self.assertEqual(self.g.assess(),'HOLD_NO_LOCAL')
 def test_no_anchor(self):self.g.set_local(0,3,self.r0);self.assertEqual(self.g.assess(),'HOLD_NO_ANCHOR')
 def test_match(self):self.seed();self.assertEqual(self.g.assess(),'RECOVERY_MATCH_LOCAL')
 def test_local_ahead(self):self.seed();self.g.set_local(1,4,self.r1);self.assertEqual(self.g.assess(),'HOLD_UNANCHORED_LOCAL_ADVANCE')
 def test_anchor_ahead(self):self.seed();self.anchor(1,4,self.r1);self.assertEqual(self.g.assess(),'HOLD_LOCAL_ROLLBACK')
 def test_fork(self):self.g.set_local(0,3,self.r1);self.anchor();self.assertEqual(self.g.assess(),'QUARANTINE_FORK')
 def test_recover_after_anchor(self):self.seed();self.g.set_local(1,4,self.r1);self.anchor(1,4,self.r1);self.assertEqual(self.g.assess(),'RECOVERY_MATCH_LOCAL')
 def test_restart(self):self.seed();g=RecoveryGate(self.db,self.anchors,self.obs);self.assertEqual(g.assess(),'RECOVERY_MATCH_LOCAL')
 def test_reject_old_epoch(self):
  self.seed()
  with self.assertRaises(Hold):self.g.set_local(0,4,self.r1)
 def test_reject_old_anchor_epoch(self):
  self.seed()
  with self.assertRaises(Hold):self.anchor(0,4,self.r1)
 def test_reject_skipped_anchor_epoch(self):
  self.seed()
  with self.assertRaises(Hold):self.anchor(2,4,self.r1)
 def test_reject_nonincreasing_size(self):
  self.seed()
  with self.assertRaises(Hold):self.anchor(1,3,self.r1)
 def test_bad_genesis(self):
  with self.assertRaises(Hold):self.anchor(1,3,self.r0)
 def test_missing_signature(self):
  with self.assertRaises(Hold):self.g.append_anchor(0,3,self.r0,{'W1':'00'})
 def test_forged_signature(self):
  wrong={n:Ed25519PrivateKey.generate() for n in self.keys}
  with self.assertRaises(Hold):self.anchor(keys=wrong)
 def test_tampered_root(self):
  self.seed();self.anchors.write_text(self.anchors.read_text().replace(self.r0,self.r1))
  self.assertTrue(self.g.assess().startswith('QUARANTINE_'))
 def test_tampered_signature(self):
  self.seed();self.anchors.write_text(self.anchors.read_text().replace('"W1":"','"W1":"ff'))
  self.assertTrue(self.g.assess().startswith('QUARANTINE_'))
 def test_truncated_file(self):self.seed();self.anchors.write_text('{');self.assertEqual(self.g.assess(),'QUARANTINE_DAMAGED_ANCHOR_LOG')
 def test_corrupt_second_record(self):
  self.seed();self.anchor(1,4,self.r1);self.anchors.write_text(self.anchors.read_text().replace(self.r1,self.r0))
  self.assertTrue(self.g.assess().startswith('QUARANTINE_'))
 def test_distinct_ancestors(self):
  b=list(self.obs);b[1]=Observer('W2','ancestor-W1','domain-W2',b[1].public)
  with self.assertRaises(Hold):RecoveryGate(self.db,self.anchors,b)
 def test_distinct_domains(self):
  b=list(self.obs);b[1]=Observer('W2','ancestor-W2','domain-W1',b[1].public)
  with self.assertRaises(Hold):RecoveryGate(self.db,self.anchors,b)
 def test_distinct_keys(self):
  b=list(self.obs);b[1]=Observer('W2','ancestor-W2','domain-W2',b[0].public)
  with self.assertRaises(Hold):RecoveryGate(self.db,self.anchors,b)
 def test_three_only(self):
  with self.assertRaises(Hold):RecoveryGate(self.db,self.anchors,self.obs[:2])
 def test_hash_chain(self):
  self.seed();self.anchor(1,4,self.r1);es=self.g.chain();self.assertEqual(es[1]['previous'],es[0]['hash'])
 def test_unchanged_after_bad_anchor(self):
  self.seed();old=self.anchors.read_bytes()
  with self.assertRaises(Hold):self.g.append_anchor(1,4,self.r1,{'W1':'12'})
  self.assertEqual(self.anchors.read_bytes(),old)
 def test_bad_checkpoint(self):
  with self.assertRaises(Hold):self.g.set_local(0,0,self.r0)
 def test_atomic_local_reopen(self):
  self.seed();self.g.set_local(1,4,self.r1);g=RecoveryGate(self.db,self.anchors,self.obs);self.assertEqual(g.local()['epoch'],1)
 def test_anchor_not_local_upgrade(self):
  self.seed();self.anchor(1,4,self.r1);self.assertEqual(self.g.local()['epoch'],0)
 def test_no_auto_trust_from_anchors(self):
  self.seed();self.anchor(1,4,self.r1);self.assertNotEqual(self.g.assess(),'RECOVERY_MATCH_LOCAL')
if __name__=='__main__':unittest.main()
