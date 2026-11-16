import unittest,tempfile,json
from pathlib import Path
from wag084 import setup,demo,Remote,DeliveryGate
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
class Tests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.g=setup(self.t.name)
  self.a=[r.store(83,'root-83','challenge-83') for r in self.g.remotes]
 def test_happy(self):self.assertEqual(self.g.decision(self.a),'LOCAL_DURABLE_ACK_QUORUM')
 def test_consume(self):self.assertEqual(self.g.decision(self.a,consume=True),'LOCAL_DURABLE_ACK_QUORUM')
 def test_replay(self):self.g.decision(self.a,consume=True);self.assertEqual(self.g.decision(self.a),'HOLD_REPLAY')
 def test_missing(self):self.assertEqual(self.g.decision(self.a[:2]),'HOLD_MISSING_ACK')
 def test_no_acks(self):self.assertEqual(self.g.decision([]),'HOLD_MISSING_ACK')
 def test_duplicate_host(self):self.assertEqual(self.g.decision([self.a[0],self.a[0],self.a[1]]),'HOLD_HOST_SET')
 def test_wrong_host(self):
  a=json.loads(json.dumps(self.a));a[2]['payload']['host']='wrong';self.assertEqual(self.g.decision(a),'HOLD_HOST_SET')
 def test_context_root(self):
  a=json.loads(json.dumps(self.a));a[0]['payload']['root']='evil';self.assertEqual(self.g.decision(a),'HOLD_CONTEXT')
 def test_context_epoch(self):
  a=json.loads(json.dumps(self.a));a[0]['payload']['epoch']=84;self.assertEqual(self.g.decision(a),'HOLD_CONTEXT')
 def test_context_challenge(self):
  a=json.loads(json.dumps(self.a));a[0]['payload']['challenge']='other';self.assertEqual(self.g.decision(a),'HOLD_CONTEXT')
 def test_bad_signature(self):
  a=json.loads(json.dumps(self.a));a[0]['signature']='00'*64;self.assertEqual(self.g.decision(a),'HOLD_BAD_SIGNATURE')
 def test_malformed_signature(self):
  a=json.loads(json.dumps(self.a));a[0]['signature']='not-hex';self.assertEqual(self.g.decision(a),'HOLD_BAD_SIGNATURE')
 def test_missing_storage(self):
  (self.g.remotes[1].directory/'checkpoint.json').unlink();self.assertEqual(self.g.decision(self.a),'HOLD_NOT_DURABLE')
 def test_no_write(self):
  (self.g.remotes[0].directory/'checkpoint.json').unlink();self.g.remotes[0].store(83,'root-83','challenge-83',ack_only=True);self.assertEqual(self.g.decision(self.a),'HOLD_NOT_DURABLE')
 def test_storage_tamper(self):
  p=self.g.remotes[0].directory/'checkpoint.json';p.write_text('{}');self.assertEqual(self.g.decision(self.a),'HOLD_STORAGE_MISMATCH')
 def test_stale_stored(self):
  self.g.remotes[0].store(82,'root-82','challenge-82');self.assertEqual(self.g.decision(self.a),'HOLD_STORAGE_MISMATCH')
 def test_restart_read(self):self.assertEqual(DeliveryGate(self.g.remotes,83,'root-83','challenge-83').decision(self.a),'LOCAL_DURABLE_ACK_QUORUM')
 def test_epoch_advance(self):self.g.advance(84,'root-84','challenge-84');self.assertEqual(self.g.decision(self.a),'HOLD_CONTEXT')
 def test_advance_new_receipts(self):
  self.g.advance(84,'root-84','challenge-84');a=[r.store(84,'root-84','challenge-84') for r in self.g.remotes];self.assertEqual(self.g.decision(a),'LOCAL_DURABLE_ACK_QUORUM')
 def test_rollback_epoch(self):
  with self.assertRaises(ValueError):self.g.advance(82,'old','new')
 def test_reuse_challenge(self):
  with self.assertRaises(ValueError):self.g.advance(84,'new','challenge-83')
 def test_duplicate_domain(self):
  r=self.g.remotes
  with self.assertRaises(ValueError):DeliveryGate([r[0],r[1],Remote('host-D',r[1].domain,Ed25519PrivateKey.generate(),Path(self.t.name)/'host-D')],83,'root','nonce')
 def test_duplicate_name(self):
  with self.assertRaises(ValueError):DeliveryGate([self.g.remotes[0]]*3,83,'root','nonce')
 def test_2_hosts(self):
  with self.assertRaises(ValueError):DeliveryGate(self.g.remotes[:2],83,'root','nonce')
 def test_audit(self):self.g.decision(self.a);self.assertTrue(self.g.audit_ok())
 def test_tampered_audit(self):self.g.decision(self.a);self.g.log[-1]['decision']='fake';self.assertFalse(self.g.audit_ok())
 def test_failure_atomic(self):
  self.g.decision(self.a[:2],consume=True);self.assertEqual(len(self.g.used),0)
 def test_demo(self):
  with tempfile.TemporaryDirectory() as d:
   z=demo(d);self.assertEqual(z['events'],3);self.assertTrue(z['audit_ok'])
if __name__=='__main__':unittest.main()
