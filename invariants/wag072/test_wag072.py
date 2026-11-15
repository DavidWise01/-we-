import unittest
from dataclasses import replace
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag072 import EquivocationGate,sign,demo,Certificate
class WAG072Tests(unittest.TestCase):
 def setUp(self):
  self.priv={n:Ed25519PrivateKey.generate() for n in ('W1','W2','W3')}
  self.keys={n:k.public_key() for n,k in self.priv.items()}
  self.roots={'W1':'A','W2':'B','W3':'C'}
  self.g=EquivocationGate(self.keys,self.roots,2,'r7','0123456789abcdef')
 def s(self,n='W1',snap='A',epoch=2,r='r7',nonce='0123456789abcdef'):
  return sign(self.priv[n],n,epoch,r,nonce,snap)
 def all_a(self):
  for n in self.priv:self.g.submit(self.s(n))
 def test_demo(self):self.assertEqual(demo()[1]['after'],'HOLD_EQUIVOCATION')
 def test_demo_cert(self):self.assertEqual(demo()[1]['certificates'],1)
 def test_demo_ledger(self):self.assertTrue(demo()[1]['ledger_verified'])
 def test_initial_hold(self):self.assertEqual(self.g.decision(),'HOLD_MISSING_WITNESS')
 def test_one_submit(self):self.assertEqual(self.g.submit(self.s()),'RECORDED')
 def test_missing_second(self):self.g.submit(self.s());self.assertEqual(self.g.decision(),'HOLD_MISSING_WITNESS')
 def test_all_agree(self):self.all_a();self.assertEqual(self.g.decision(),'LOCAL_SIGNED_AGREEMENT')
 def test_disagree_without_equivocation(self):
  self.g.submit(self.s('W1'));self.g.submit(self.s('W2'));self.g.submit(self.s('W3','B'))
  self.assertEqual(self.g.decision(),'HOLD_SNAPSHOT_DISAGREEMENT')
 def test_same_replay(self):self.g.submit(self.s());self.assertEqual(self.g.submit(self.s()),'REPLAY_NO_CHANGE')
 def test_equivocation(self):self.g.submit(self.s());self.assertEqual(self.g.submit(self.s(snap='B')),'QUARANTINE_EQUIVOCATION')
 def test_quarantine(self):self.g.submit(self.s());self.g.submit(self.s(snap='B'));self.assertEqual(self.g.quarantined,{'W1'})
 def test_certificate_present(self):self.g.submit(self.s());self.g.submit(self.s(snap='B'));self.assertIn('W1',self.g.equivocations)
 def test_certificate_valid(self):self.g.submit(self.s());self.g.submit(self.s(snap='B'));self.assertTrue(self.g.verify_certificate(self.g.equivocations['W1']))
 def test_certificate_tampered(self):
  a=self.s();b=self.s(snap='B');self.assertFalse(self.g.verify_certificate(Certificate('W1',a,replace(b,snapshot='C'))))
 def test_same_claim_not_fork(self):self.g.submit(self.s());self.g.submit(self.s());self.assertEqual(len(self.g.equivocations),0)
 def test_bad_signature(self):self.assertEqual(self.g.submit(replace(self.s(),signature='00'*64)),'REJECT_BAD_SIGNATURE')
 def test_bad_hex(self):self.assertEqual(self.g.submit(replace(self.s(),signature='nope')),'REJECT_BAD_SIGNATURE')
 def test_wrong_epoch(self):self.assertEqual(self.g.submit(self.s(epoch=1)),'REJECT_WRONG_CHALLENGE_OR_ROUND')
 def test_future_epoch(self):self.assertEqual(self.g.submit(self.s(epoch=3)),'REJECT_WRONG_CHALLENGE_OR_ROUND')
 def test_wrong_round(self):self.assertEqual(self.g.submit(self.s(r='r8')),'REJECT_WRONG_CHALLENGE_OR_ROUND')
 def test_wrong_nonce(self):self.assertEqual(self.g.submit(self.s(nonce='123456789abcdef0')),'REJECT_WRONG_CHALLENGE_OR_ROUND')
 def test_nonce_signature_binds(self):self.assertFalse(self.g.verify_signature(replace(self.s(),challenge='123456789abcdef0')))
 def test_snapshot_signature_binds(self):self.assertFalse(self.g.verify_signature(replace(self.s(),snapshot='B')))
 def test_epoch_signature_binds(self):self.assertFalse(self.g.verify_signature(replace(self.s(),epoch=3)))
 def test_round_signature_binds(self):self.assertFalse(self.g.verify_signature(replace(self.s(),round_id='r8')))
 def test_name_signature_binds(self):self.assertFalse(self.g.verify_signature(replace(self.s(),signer='W2')))
 def test_unknown_signer(self):self.assertEqual(self.g.submit(replace(self.s(),signer='W4')),'REJECT_BAD_SIGNATURE')
 def test_distinct_roots_required(self):
  with self.assertRaises(ValueError):EquivocationGate(self.keys,{'W1':'A','W2':'A','W3':'C'},2,'r7','0123456789abcdef')
 def test_three_keys_required(self):
  with self.assertRaises(ValueError):EquivocationGate({'W1':self.keys['W1']},{'W1':'A'},2,'r7','0123456789abcdef')
 def test_missing_root(self):
  with self.assertRaises(ValueError):EquivocationGate(self.keys,{'W1':'A','W2':'B'},2,'r7','0123456789abcdef')
 def test_short_nonce(self):
  with self.assertRaises(ValueError):EquivocationGate(self.keys,self.roots,2,'r7','short')
 def test_negative_epoch(self):
  with self.assertRaises(ValueError):EquivocationGate(self.keys,self.roots,-1,'r7','0123456789abcdef')
 def test_empty_round(self):
  with self.assertRaises(ValueError):EquivocationGate(self.keys,self.roots,2,'','0123456789abcdef')
 def test_initial_ledger(self):self.assertEqual(len(self.g.ledger),1)
 def test_all_ledger(self):self.all_a();self.assertEqual(len(self.g.ledger),4)
 def test_fork_ledger(self):self.all_a();self.g.submit(self.s(snap='B'));self.assertEqual(len(self.g.ledger),5)
 def test_replay_no_extra_event(self):self.g.submit(self.s());self.g.submit(self.s());self.assertEqual(len(self.g.ledger),2)
 def test_rejected_no_extra_event(self):self.g.submit(self.s(epoch=1));self.assertEqual(len(self.g.ledger),1)
 def test_tamper_ledger(self):self.all_a();self.g.ledger[2]['data']['snapshot']='FAKE';self.assertFalse(self.g.verify_ledger())
 def test_valid_ledger(self):self.all_a();self.assertTrue(self.g.verify_ledger())
 def test_fork_persists_after_more(self):
  self.all_a();self.g.submit(self.s(snap='B'));self.g.submit(self.s('W2',snap='A'));self.assertEqual(self.g.decision(),'HOLD_EQUIVOCATION')
 def test_two_equivocators(self):
  self.all_a();self.g.submit(self.s(snap='B'));self.g.submit(self.s('W2',snap='B'))
  self.assertEqual(len(self.g.equivocations),2)
 def test_different_nonce_not_equivocation(self):
  self.g.submit(self.s());self.g.submit(self.s(snap='B',nonce='123456789abcdef0'))
  self.assertEqual(len(self.g.equivocations),0)
 def test_different_epoch_not_equivocation(self):
  self.g.submit(self.s());self.g.submit(self.s(snap='B',epoch=3));self.assertEqual(len(self.g.equivocations),0)
 def test_different_round_not_equivocation(self):
  self.g.submit(self.s());self.g.submit(self.s(snap='B',r='r8'));self.assertEqual(len(self.g.equivocations),0)
 def test_certificate_swapped(self):
  a=self.s();b=self.s(snap='B');self.assertTrue(self.g.verify_certificate(Certificate('W1',b,a)))
 def test_certificate_mismatch_signer(self):self.assertFalse(self.g.verify_certificate(Certificate('W2',self.s(),self.s(snap='B'))))
 def test_certificate_same_snapshot(self):self.assertFalse(self.g.verify_certificate(Certificate('W1',self.s(),self.s())))
 def test_immutably_preserve_first(self):
  a=self.s();self.g.submit(a);self.g.submit(self.s(snap='B'));self.assertEqual(self.g.statements['W1'],a)
if __name__=='__main__':unittest.main()
