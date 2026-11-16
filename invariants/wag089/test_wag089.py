import os, tempfile, unittest
from fractions import Fraction
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag089 import Witness,EvidenceGate,merkle,demo
class TestWAG089(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.db=os.path.join(self.tmp.name,'gate.db')
  self.chunks=[f'block-{i:02d}'.encode() for i in range(17)];self.root,_=merkle(self.chunks)
  self.ws=[Witness(f'W{i}',f'A{i}',f'D{i}',Ed25519PrivateKey.generate()) for i in range(1,4)]
  self.g=EvidenceGate(self.db,self.ws,self.root,17,3,3)
 def tearDown(self):self.g.close();self.tmp.cleanup()
 def make(self,t=1,nonce=b'unpredictable-demo-nonce-001'):
  return [self.g.signed_observation(w,self.chunks,nonce,t) for w in self.ws]
 def accept(self,t=1,nonce=b'unpredictable-demo-nonce-001'):return self.g.accept_round(self.make(t,nonce),nonce,t)
 def fail(self,responses,nonce=b'unpredictable-demo-nonce-001',round_no=1):
  with self.assertRaises((ValueError,KeyError,TypeError)):self.g.accept_round(responses,nonce,round_no)
  self.assertEqual(self.g.rounds(),0)
 def test_demo(self):self.assertTrue(demo()['audit_ok'])
 def test_qualifying_round(self):self.assertEqual(demo()['first_qualifying_round'],14)
 def test_accept(self):self.assertEqual(self.accept()['round'],1)
 def test_initial_hold(self):self.assertEqual(self.accept()['decision'],'HOLD_INSUFFICIENT_EVIDENCE')
 def test_three_positions(self):self.assertEqual(len(self.accept()['positions']),3)
 def test_unique_coverage(self):self.assertEqual(self.accept()['unique_coverage'],3)
 def test_bounds(self):self.assertEqual(self.g.one_round_miss(),Fraction(91,170))
 def test_alpha(self):self.assertEqual(self.g.threshold(1),Fraction(1,40))
 def test_second_bound(self):self.assertEqual(self.g.miss_bound(2),Fraction(91,170)**2)
 def test_audit(self):self.accept();self.assertTrue(self.g.verify_audit())
 def test_audit_tamper(self):self.accept();self.g.conn.execute("update ledger set kind='tampered'");self.assertFalse(self.g.verify_audit())
 def test_replay_nonce(self):
  r=self.make();n=b'unpredictable-demo-nonce-001';self.g.accept_round(r,n,1)
  with self.assertRaises(ValueError):self.g.accept_round(r,n,1)
 def test_replay_after_restart(self):
  r=self.make();n=b'unpredictable-demo-nonce-001';self.g.accept_round(r,n,1);self.g.close();self.g=EvidenceGate(self.db,self.ws,self.root,17,3,3)
  with self.assertRaises(ValueError):self.g.accept_round(r,n,1)
 def test_persist_rounds(self):self.accept();self.g.close();self.g=EvidenceGate(self.db,self.ws,self.root,17,3,3);self.assertEqual(self.g.rounds(),1)
 def test_policy_change(self):
  self.g.close()
  with self.assertRaises(ValueError):EvidenceGate(self.db,self.ws,self.root,17,3,2)
  self.g=EvidenceGate(self.db,self.ws,self.root,17,3,3)
 def test_wrong_nonce(self):self.fail(self.make(),b'wrong-unpredictable-nonce')
 def test_wrong_round(self):self.fail(self.make(),round_no=2)
 def test_missing_host(self):self.fail(self.make()[:2])
 def test_duplicate_host(self):r=self.make();r[2]=r[1];self.fail(r)
 def test_forged_signature(self):r=self.make();r[0]['signature']='00'*64;self.fail(r)
 def test_altered_chunk(self):r=self.make();r[0]['body']['samples'][0]['chunk']='deadbeef';self.fail(r)
 def test_altered_path(self):r=self.make();r[0]['body']['samples'][0]['path'][0]='00'*32;self.fail(r)
 def test_missing_sample(self):r=self.make();r[0]['body']['samples'].pop();self.fail(r)
 def test_changed_root(self):r=self.make();r[0]['body']['root']='00'*32;self.fail(r)
 def test_changed_epoch(self):r=self.make();r[0]['body']['epoch']=90;self.fail(r)
 def test_changed_protocol(self):r=self.make();r[0]['body']['protocol']='WAG-000';self.fail(r)
 def test_changed_count(self):r=self.make();r[0]['body']['count']=16;self.fail(r)
 def test_changed_index(self):r=self.make();r[0]['body']['indices'][0]=16;self.fail(r)
 def test_unknown_witness(self):r=self.make();r[0]['body']['witness']='W9';self.fail(r)
 def test_wrong_key(self):r=self.make();r[0]['signature']=self.ws[1].key.sign(b'test').hex();self.fail(r)
 def test_short_nonce(self):
  with self.assertRaises(ValueError):self.g.accept_round(self.make(),b'bad',1)
 def test_zero_round(self):self.fail(self.make(),round_no=0)
 def test_no_missing(self):
  with self.assertRaises(ValueError):EvidenceGate(':memory:',self.ws,self.root,17,3,0)
 def test_too_many_missing(self):
  with self.assertRaises(ValueError):EvidenceGate(':memory:',self.ws,self.root,17,3,18)
 def test_bad_budget(self):
  with self.assertRaises(ValueError):EvidenceGate(':memory:',self.ws,self.root,17,3,3,1)
 def test_duplicate_ancestor(self):
  ws=list(self.ws);ws[2]=Witness('W3','A1','D3',ws[2].key)
  with self.assertRaises(ValueError):EvidenceGate(':memory:',ws,self.root,17)
 def test_duplicate_domain(self):
  ws=list(self.ws);ws[2]=Witness('W3','A3','D1',ws[2].key)
  with self.assertRaises(ValueError):EvidenceGate(':memory:',ws,self.root,17)
 def test_distinct_hosts_one_round(self):self.assertEqual(self.accept()['unique_coverage'],3)
 def test_two_rounds(self):
  self.accept();self.g.accept_round(self.make(2,b'unpredictable-demo-nonce-002'),b'unpredictable-demo-nonce-002',2)
  self.assertEqual(self.g.rounds(),2)
 def test_ledger_two_rounds(self):
  self.accept();self.g.accept_round(self.make(2,b'unpredictable-demo-nonce-002'),b'unpredictable-demo-nonce-002',2)
  self.assertEqual(self.g.conn.execute('select count(*) from ledger').fetchone()[0],2)
 def test_retry_after_failed_round(self):
  r=self.make();r[0]['signature']='00'*64;self.fail(r);self.assertEqual(self.accept()['round'],1)
 def test_three_identical_views_do_not_triple_count(self):self.assertEqual(self.accept()['unique_coverage'],3)
 def test_miss_bound_monotonic(self):self.assertGreater(self.g.miss_bound(1),self.g.miss_bound(2))
 def test_exact_prefix_all_missing(self):
  self.g.close();self.g=EvidenceGate(':memory:',self.ws,self.root,17,3,17)
  self.assertEqual(self.g.one_round_miss(),0)
if __name__=='__main__':unittest.main()
