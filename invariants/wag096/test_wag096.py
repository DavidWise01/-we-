import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag096 import Gate,sign_head,root,path,inclusion
E={'epoch':96,'round':1,'archive_root':'a'*64,'event':'commit-observed'}
class Tests(unittest.TestCase):
 def setUp(self):
  self.private={x:Ed25519PrivateKey.generate() for x in 'ABC'}
  self.g=Gate({x:k.public_key() for x,k in self.private.items()}, {x:'root-'+x for x in 'ABC'})
 def submit(self,op,leaves,index=0):
  h=sign_head(self.private[op],op,leaves)
  return self.g.submit(h,leaves[index],index,path(leaves,index),leaves)
 def test_valid_three_logs(self):
  for op in 'ABC':self.assertEqual('VERIFIED_LOCAL_PROOF',self.submit(op,[E]))
  self.assertEqual('ELIGIBLE_FOR_EXTERNAL_TIME_AND_CUSTODY_VERIFICATION',self.g.checkpoint(E))
 def test_missing_log(self):
  for op in 'AB':self.submit(op,[E])
  self.assertEqual('HOLD_MISSING_LOG',self.g.checkpoint(E))
 def test_missing_entry(self):
  for op in 'AB':self.submit(op,[E])
  self.submit('C',[{'other':1}])
  self.assertEqual('HOLD_MISSING_ENTRY',self.g.checkpoint(E))
 def test_append_only_upgrade(self):
  self.submit('A',[E]);self.assertEqual('VERIFIED_LOCAL_PROOF',self.submit('A',[E,{'next':1}]))
 def test_fork_same_size(self):
  self.submit('A',[E]);self.assertEqual('QUARANTINE_FORK',self.submit('A',[{'other':2}]))
 def test_fork_longer(self):
  self.submit('A',[E]);self.assertEqual('QUARANTINE_FORK',self.submit('A',[{'other':2},E]))
 def test_rollback(self):
  self.submit('A',[E,{'next':1}]);self.assertEqual('HOLD_ROLLBACK',self.submit('A',[E]))
 def test_forged_signature(self):
  h=sign_head(self.private['B'],'A',[E])
  self.assertEqual('HOLD_INVALID_HEAD',self.g.submit(h,E,0,path([E],0),[E]))
 def test_wrong_proof(self):
  l=[E,{'other':3}];h=sign_head(self.private['A'],'A',l)
  self.assertEqual('HOLD_INVALID_INCLUSION',self.g.submit(h,E,0,[],l))
 def test_wrong_entry(self):
  l=[E];h=sign_head(self.private['A'],'A',l)
  self.assertEqual('HOLD_INVALID_INCLUSION',self.g.submit(h,{'altered':1},0,path(l,0),l))
 def test_bad_prefix(self):
  l=[E];h=sign_head(self.private['A'],'A',l)
  self.assertEqual('HOLD_INVALID_PREFIX',self.g.submit(h,E,0,path(l,0),[{'altered':1}]))
 def test_shared_ancestry(self):
  with self.assertRaises(ValueError):Gate({x:k.public_key() for x,k in self.private.items()},dict.fromkeys('ABC','same'))
 def test_empty_head_rejected(self):
  h=sign_head(self.private['A'],'A',[])
  self.assertFalse(self.g.verify_head(h))
 def test_audit_fork_retained(self):
  self.submit('A',[E]);self.submit('A',[{'other':2}])
  self.assertEqual(2,len(self.g.evidence));self.assertEqual(1,len(self.g.forks))
 def test_inclusion_odd_nodes(self):
  l=[{'i':i} for i in range(7)]
  for i in range(len(l)):
   self.assertTrue(inclusion(l[i],i,len(l),path(l,i),root(l).hex()))
 def test_wrong_index(self):
  l=[E,{'other':1}];self.assertFalse(inclusion(E,1,len(l),path(l,0),root(l).hex()))
 def test_same_head_replay_idempotent(self):
  self.submit('A',[E]);self.assertEqual('VERIFIED_LOCAL_PROOF',self.submit('A',[E]))
if __name__=='__main__':unittest.main()
