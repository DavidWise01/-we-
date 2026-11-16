import unittest
from dataclasses import replace
from wag078 import PrefixGate,demo

class WAG078ReferenceTests(unittest.TestCase):
 def setUp(self):
  self.g=PrefixGate()
  self.g.freeze(('A','B','C'),7)
  self.e=('A','B','C','D')
  self.h=self.g.head(self.e,8)
 def votes(self,h=None):
  h=h or self.h
  return [self.g.vote(w,h) for w in ('W1','W2','W3')]
 def test_demo(self):self.assertTrue(demo()['valid'])
 def test_valid_head(self):self.assertTrue(self.g.valid_head(self.h))
 def test_changed_signature(self):self.assertFalse(self.g.valid_head(replace(self.h,root='x'*64)))
 def test_honest_prefix(self):self.assertEqual(self.g.decision(self.h,self.e),'PREFIX_VALID')
 def test_honest_certify(self):self.assertEqual(self.g.confirm(self.h,self.e,self.votes()),'LOCAL_PREFIX_CERTIFIED')
 def test_rewrite_middle(self):
  x=('A','X','C','D');h=self.g.head(x,8)
  self.assertEqual(self.g.decision(h,x),'QUARANTINE_REWRITTEN_PREFIX')
 def test_rewrite_first(self):
  x=('X','B','C','D');h=self.g.head(x,8)
  self.assertEqual(self.g.decision(h,x),'QUARANTINE_REWRITTEN_PREFIX')
 def test_rewrite_last(self):
  x=('A','B','X','D');h=self.g.head(x,8)
  self.assertEqual(self.g.decision(h,x),'QUARANTINE_REWRITTEN_PREFIX')
 def test_rollback(self):
  x=('A','B');self.assertEqual(self.g.decision(self.g.head(x,8),x),'HOLD_ROLLBACK')
 def test_stale_epoch(self):
  h=self.g.head(self.e,7);self.assertEqual(self.g.decision(h,self.e),'HOLD_STALE_EPOCH')
 def test_equal_size(self):
  h=self.g.head(('A','B','C'),8)
  self.assertEqual(self.g.decision(h,('A','B','C')),'HOLD_NO_EXTENSION')
 def test_data_mismatch(self):self.assertEqual(self.g.decision(self.h,('A','B','C','X')),'HOLD_SNAPSHOT_MISMATCH')
 def test_quorum_hold(self):self.assertEqual(self.g.confirm(self.h,self.e,self.votes()[:2]),'HOLD_OBSERVER_QUORUM')
 def test_duplicate_vote(self):
  x=self.votes();x[2]=x[0]
  self.assertEqual(self.g.confirm(self.h,self.e,x),'HOLD_OBSERVER_QUORUM')
 def test_forged_vote(self):
  x=self.votes();x[0]=replace(x[0],signature=b'0'*64)
  self.assertEqual(self.g.confirm(self.h,self.e,x),'HOLD_OBSERVER_SIGNATURE')
 def test_wrong_vote_context(self):
  x=self.votes();x[0]=replace(x[0],old_root='0'*64)
  self.assertEqual(self.g.confirm(self.h,self.e,x),'HOLD_OBSERVER_CONTEXT')
 def test_freeze_once(self):
  with self.assertRaises(ValueError):self.g.freeze(('A','B','C'),7)
 def test_preserved_frozen(self):
  self.g.confirm(self.h,self.e,self.votes())
  self.assertEqual(self.g.frozen_events,('A','B','C'))
 def test_audit_tamper(self):
  self.g.audit[0]['kind']='fake'
  self.assertFalse(self.g.audit_valid())
 def test_audit_verifies(self):
  self.g.confirm(self.h,self.e,self.votes())
  self.assertTrue(self.g.audit_valid())
if __name__=='__main__':unittest.main()
