import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag077 import Registry,Gate,demo,h
def setup():
 r=Registry('R');r.append('declare','W4','org-w',1);return r,Gate({'R':r.public})
def observe3(r,g):
 for w in ('W1','W2','W3'):g.observe(*r.head(),w)
class TestRegistryTransparency(unittest.TestCase):
 def setUp(self):self.r,self.g=setup()
 def test_demo(self):self.assertEqual(demo()['after_revocation'],'HOLD_REVOKED')
 def test_demo_records(self):self.assertEqual(demo()['observations'],6)
 def test_demo_audit(self):self.assertTrue(demo()['audit_valid'])
 def test_chain(self):self.assertTrue(self.r.valid())
 def test_size(self):self.assertEqual(self.r.head()[0]['size'],1)
 def test_prefix_differs(self):self.assertNotEqual(self.r.root(0),self.r.root(1))
 def test_historical_active(self):self.assertEqual(self.r.status('W4','org-w',1),'ACTIVE')
 def test_unknown(self):self.assertEqual(self.r.status('W5','org-w'),'UNKNOWN')
 def test_three(self):observe3(self.r,self.g);self.assertEqual(self.g.evaluate(self.r,'W4','org-w',('W1','W2','W3')),'LOCAL_DECLARED_ANCESTRY_ACCEPTED')
 def test_one(self):
  self.g.observe(*self.r.head(),'W1')
  self.assertEqual(self.g.evaluate(self.r,'W4','org-w',('W1','W2','W3')),'HOLD_MISSING_WITNESS')
 def test_same_witness_repeated(self):
  observe3(self.r,self.g)
  self.assertEqual(self.g.evaluate(self.r,'W4','org-w',('W1','W1','W3')),'HOLD_MISSING_WITNESS')
 def test_revoked(self):
  observe3(self.r,self.g);self.r.append('revoke','W4','org-w',2);observe3(self.r,self.g)
  self.assertEqual(self.g.evaluate(self.r,'W4','org-w',('W1','W2','W3')),'HOLD_REVOKED')
 def test_stale(self):
  observe3(self.r,self.g);self.r.append('revoke','W4','org-w',2)
  self.assertEqual(self.g.evaluate(self.r,'W4','org-w',('W1','W2','W3')),'HOLD_STALE_OR_UNMATCHED_LOG')
 def test_fork(self):
  other=Registry('R',self.r.key);other.append('declare','W4','evil',1)
  self.g.observe(*self.r.head(),'W1')
  self.assertEqual(self.g.observe(*other.head(),'W2'),'QUARANTINE_SPLIT_VIEW')
 def test_fork_quarantined(self):
  other=Registry('R',self.r.key);other.append('declare','W4','evil',1)
  self.g.observe(*self.r.head(),'W1');self.g.observe(*other.head(),'W2')
  self.assertEqual(self.g.evaluate(self.r,'W4','org-w',('W1','W2','W3')),'QUARANTINE_SPLIT_VIEW')
 def test_one_witness_fork(self):
  other=Registry('R',self.r.key);other.append('declare','W4','evil',1)
  self.g.observe(*self.r.head(),'W1')
  self.assertEqual(self.g.observe(*other.head(),'W1'),'QUARANTINE_SPLIT_VIEW')
 def test_rollback(self):
  self.g.observe(*self.r.head(),'W1');self.r.append('revoke','W4','org-w',2)
  self.g.observe(*self.r.head(),'W1')
  self.assertEqual(self.g.observe(*self.r.head(1),'W1'),'HOLD_ROLLBACK')
 def test_signed(self):self.assertEqual(self.g.observe(*self.r.head(),'W1'),'OBSERVED')
 def test_forged_signature(self):
  record,_=self.r.head()
  with self.assertRaises(ValueError):self.g.observe(record,b'0'*64,'W1')
 def test_wrong_key(self):
  rogue=Registry('R',Ed25519PrivateKey.generate());rogue.append('declare','W4','org-w',1)
  with self.assertRaises(ValueError):self.g.observe(*rogue.head(),'W1')
 def test_unknown_registry(self):
  other=Registry('Z')
  with self.assertRaises(ValueError):self.g.observe(*other.head(),'W1')
 def test_bad_kind(self):
  with self.assertRaises(ValueError):self.r.append('overwrite','W4','org-w',2)
 def test_bad_epoch(self):
  with self.assertRaises(ValueError):self.r.append('revoke','W4','org-w',-1)
 def test_tamper_event(self):self.r.events[0]['subject']='fake';self.assertFalse(self.r.valid())
 def test_tamper_holds(self):
  observe3(self.r,self.g);self.r.events[0]['subject']='fake'
  self.assertEqual(self.g.evaluate(self.r,'W4','org-w',('W1','W2','W3')),'HOLD_INVALID_LOG')
 def test_tamper_audit(self):
  observe3(self.r,self.g);self.g.audit[0]['data']['witness']='fake';self.assertFalse(self.g.audit_valid())
 def test_audit_normal(self):observe3(self.r,self.g);self.assertTrue(self.g.audit_valid())
 def test_new_heads_disagree(self):
  self.g.observe(*self.r.head(),'W1');self.g.observe(*self.r.head(),'W2')
  self.r.append('revoke','W4','org-w',2);self.g.observe(*self.r.head(),'W3')
  self.assertEqual(self.g.evaluate(self.r,'W4','org-w',('W1','W2','W3')),'HOLD_HEAD_DISAGREEMENT')
 def test_other_subject_revoked(self):
  self.r.append('revoke','W8','org-w',2);observe3(self.r,self.g)
  self.assertEqual(self.g.evaluate(self.r,'W4','org-w',('W1','W2','W3')),'LOCAL_DECLARED_ANCESTRY_ACCEPTED')
 def test_invalid_name(self):
  with self.assertRaises(ValueError):Registry('')
 def test_invalid_size(self):
  with self.assertRaises(ValueError):self.r.head(999)
 def test_no_keys(self):
  with self.assertRaises(ValueError):Gate({})
 def test_three_observations(self):observe3(self.r,self.g);self.assertEqual(len(self.g.audit),3)
if __name__=='__main__':unittest.main()
