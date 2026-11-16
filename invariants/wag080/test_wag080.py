import unittest
from dataclasses import replace
from wag080 import *
class WAG080Tests(unittest.TestCase):
 def setUp(self):
  self.g,self.keys=fixtures();self.old=self.g.root;self.challenge=self.g.challenge;self.new=H('new');self.proof=H('proof')
  self.v=votes_for(self.g,self.keys,self.old,self.new,0,self.challenge,self.proof)
 def advance(self,**override):
  x=dict(old=self.old,new=self.new,epoch=0,challenge=self.challenge,proof=self.proof,votes=self.v,proof_verified=True)
  x.update(override);return self.g.advance(**x)
 def reject(self,code,**kw):
  before=(self.g.root,self.g.epoch,len(self.g.events))
  with self.assertRaises(Hold) as e:self.advance(**kw)
  self.assertEqual(str(e.exception),code)
  self.assertEqual(before,(self.g.root,self.g.epoch,len(self.g.events)))
 def test_valid(self):self.assertEqual(self.advance(),'ADVANCED_LOCAL')
 def test_epoch(self):self.advance();self.assertEqual(self.g.epoch,1)
 def test_new_root(self):self.advance();self.assertEqual(self.g.root,self.new)
 def test_challenge_rotation(self):self.advance();self.assertNotEqual(self.g.challenge,self.challenge)
 def test_audit(self):self.advance();self.assertTrue(self.g.audit_ok())
 def test_record_count(self):self.advance();self.assertEqual(len(self.g.events),2)
 def test_certificate_retained(self):self.advance();self.assertEqual(self.g.certs[0]['old'],self.old)
 def test_ids_consumed(self):self.advance();self.assertEqual(len(self.g.used_ids),3)
 def test_old_root(self):self.reject('OLD_ROOT_MISMATCH',old=H('fake'))
 def test_stale_epoch(self):self.reject('STALE_EPOCH',epoch=-1)
 def test_future_epoch(self):self.reject('STALE_EPOCH',epoch=1)
 def test_challenge(self):self.reject('STALE_CHALLENGE',challenge=H('wrong'))
 def test_same_root(self):self.reject('INVALID_TRANSITION',new=self.old)
 def test_bad_new_root(self):self.reject('INVALID_TRANSITION',new='bad')
 def test_bad_proof_digest(self):self.reject('INVALID_TRANSITION',proof='bad')
 def test_false_proof(self):self.reject('INVALID_PROOF',proof_verified=False)
 def test_missing_vote(self):self.reject('MISSING_WITNESS',votes=self.v[:2])
 def test_duplicate_signer(self):self.reject('MISSING_WITNESS',votes=[self.v[0],self.v[0],self.v[2]])
 def test_duplicate_id(self):self.reject('DUPLICATE_RECEIPT',votes=[self.v[0],replace(self.v[1],receipt_id=self.v[0].receipt_id),self.v[2]])
 def test_invalid_signature(self):self.reject('INVALID_SIGNATURE',votes=[self.v[0],replace(self.v[1],signature=b'0'*64),self.v[2]])
 def test_replay_old(self):
  self.advance()
  with self.assertRaises(Hold) as e:self.advance()
  self.assertEqual(str(e.exception),'OLD_ROOT_MISMATCH')
 def test_replay_ids_fresh_epoch(self):
  self.advance();third=H('third');vv=votes_for(self.g,self.keys,self.new,third,1,self.g.challenge,self.proof)
  with self.assertRaises(Hold) as e:self.g.advance(self.new,third,1,self.g.challenge,self.proof,vv,True)
  self.assertEqual(str(e.exception),'REPLAYED_RECEIPT')
 def test_second_with_fresh_ids(self):
  self.advance();third=H('third');vv=votes_for(self.g,self.keys,self.new,third,1,self.g.challenge,self.proof,'b')
  self.assertEqual(self.g.advance(self.new,third,1,self.g.challenge,self.proof,vv,True),'ADVANCED_LOCAL')
 def test_tamper_detection(self):self.advance();self.g.events[1]['data']['epoch']=42;self.assertFalse(self.g.audit_ok())
if __name__=='__main__':unittest.main()
