import unittest,tempfile,copy
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag086 import *
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'db.sqlite';self.chunks=[f'blob{i}'.encode() for i in range(17)];self.root,self.layers=merkle(self.chunks)
  self.hosts=[Host(f'W{i}',f'A{i}',f'D{i}',Ed25519PrivateKey.generate()) for i in range(1,4)]
  self.g=Gate(self.path,self.hosts,self.root,17);self.nonce=b'unpredictable-nonce-001';self.responses=[self.g.signed_response(h,self.chunks,self.nonce) for h in self.hosts]
 def tearDown(self):self.g.close();self.tmp.cleanup()
 def test_01_merkle(self):self.assertEqual(len(self.root),32)
 def test_02_single_leaf(self):self.assertTrue(verify(b'x',0,1,[],leaf(b'x')))
 def test_03_empty_archive(self):
  with self.assertRaises(ValueError):merkle([])
 def test_04_all_proofs(self):
  for i,c in enumerate(self.chunks):self.assertTrue(verify(c,i,17,proof(self.layers,i),self.root))
 def test_05_modified_chunk(self):self.assertFalse(verify(b'bad',1,17,proof(self.layers,1),self.root))
 def test_06_modified_path(self):
  p=proof(self.layers,1);p[0]='00'*32;self.assertFalse(verify(self.chunks[1],1,17,p,self.root))
 def test_07_short_path(self):self.assertFalse(verify(self.chunks[0],0,17,[],self.root))
 def test_08_wrong_index(self):self.assertFalse(verify(self.chunks[0],1,17,proof(self.layers,0),self.root))
 def test_09_out_of_bounds(self):self.assertFalse(verify(self.chunks[0],17,17,[],self.root))
 def test_10_odd_tree(self):self.assertTrue(verify(self.chunks[16],16,17,proof(self.layers,16),self.root))
 def test_11_nop_fake_sibling(self):
  p=proof(self.layers,16);p[0]='ff'*32;self.assertFalse(verify(self.chunks[16],16,17,p,self.root))
 def test_12_deterministic_sampling(self):self.assertEqual(challenge_indices(self.nonce,17,3),challenge_indices(self.nonce,17,3))
 def test_13_distinct_samples(self):self.assertEqual(len(set(challenge_indices(self.nonce,17,3))),3)
 def test_14_range(self):self.assertTrue(all(0<=i<17 for i in challenge_indices(self.nonce,17,3)))
 def test_15_one_sample(self):self.assertEqual(len(challenge_indices(self.nonce,17,1)),1)
 def test_16_all_samples(self):self.assertEqual(len(challenge_indices(self.nonce,17,17)),17)
 def test_17_short_nonce(self):
  with self.assertRaises(ValueError):challenge_indices(b'short',17,3)
 def test_18_k_too_big(self):
  with self.assertRaises(ValueError):challenge_indices(self.nonce,17,18)
 def test_19_accept(self):self.assertEqual(self.g.accept(self.responses,self.nonce),'LOCAL_SAMPLED_STORAGE_ELIGIBLE')
 def test_20_audit(self):self.g.accept(self.responses,self.nonce);self.assertTrue(self.g.ledger_ok())
 def test_21_replay(self):
  self.g.accept(self.responses,self.nonce)
  with self.assertRaises(ValueError):self.g.accept(self.responses,self.nonce)
 def test_22_replay_restart(self):
  self.g.accept(self.responses,self.nonce);self.g.close();self.g=Gate(self.path,self.hosts,self.root,17)
  with self.assertRaises(ValueError):self.g.accept(self.responses,self.nonce)
 def test_23_missing_host(self):
  with self.assertRaises(ValueError):self.g.accept(self.responses[:2],self.nonce)
 def test_24_duplicate_host(self):
  with self.assertRaises(ValueError):self.g.accept([self.responses[0]]*3,self.nonce)
 def test_25_fake_signature(self):
  r=copy.deepcopy(self.responses);r[0]['signature']='00'*64
  with self.assertRaises(ValueError):self.g.accept(r,self.nonce)
 def test_26_bad_epoch(self):
  r=copy.deepcopy(self.responses);r[0]['body']['epoch']=9
  with self.assertRaises(ValueError):self.g.accept(r,self.nonce)
 def test_27_bad_root(self):
  r=copy.deepcopy(self.responses);r[0]['body']['root']='00'*32
  with self.assertRaises(ValueError):self.g.accept(r,self.nonce)
 def test_28_bad_nonce(self):
  r=copy.deepcopy(self.responses);r[0]['body']['nonce']='00'*20
  with self.assertRaises(ValueError):self.g.accept(r,self.nonce)
 def test_29_tampered_chunk_signed(self):
  r=copy.deepcopy(self.responses);r[0]['body']['samples'][0]['chunk']='00'
  r[0]['signature']=self.hosts[0].key.sign(canon(r[0]['body'])).hex()
  with self.assertRaises(ValueError):self.g.accept(r,self.nonce)
 def test_30_wrong_indices_signed(self):
  r=copy.deepcopy(self.responses);r[0]['body']['indices']=[0,1,2];r[0]['signature']=self.hosts[0].key.sign(canon(r[0]['body'])).hex()
  with self.assertRaises(ValueError):self.g.accept(r,self.nonce)
 def test_31_bad_sample_count_signed(self):
  r=copy.deepcopy(self.responses);r[0]['body']['samples'].pop();r[0]['signature']=self.hosts[0].key.sign(canon(r[0]['body'])).hex()
  with self.assertRaises(ValueError):self.g.accept(r,self.nonce)
 def test_32_atomic_failure(self):
  r=copy.deepcopy(self.responses);r[2]['signature']='00'*64
  with self.assertRaises(ValueError):self.g.accept(r,self.nonce)
  self.assertEqual(self.g.conn.execute('select count(*) from used').fetchone()[0],0)
 def test_33_good_after_failure(self):
  r=copy.deepcopy(self.responses);r[2]['signature']='00'*64
  with self.assertRaises(ValueError):self.g.accept(r,self.nonce)
  self.assertEqual(self.g.accept(self.responses,self.nonce),'LOCAL_SAMPLED_STORAGE_ELIGIBLE')
 def test_34_duplicate_ancestor(self):
  h=list(self.hosts);h[2]=Host('W3','A1','D3',h[2].key)
  with self.assertRaises(ValueError):Gate(':memory:',h,self.root,17)
 def test_35_duplicate_domain(self):
  h=list(self.hosts);h[2]=Host('W3','A3','D1',h[2].key)
  with self.assertRaises(ValueError):Gate(':memory:',h,self.root,17)
 def test_36_ledger_tamper(self):
  self.g.accept(self.responses,self.nonce);self.g.conn.execute("update ledger set kind='altered'");self.g.conn.commit();self.assertFalse(self.g.ledger_ok())
 def test_37_demo(self):self.assertEqual(demo()['replay'],'REJECTED')
 def test_38_mismatched_host_name(self):
  r=copy.deepcopy(self.responses);r[0]['body']['host']='W7';r[0]['signature']=self.hosts[0].key.sign(canon(r[0]['body'])).hex()
  with self.assertRaises(ValueError):self.g.accept(r,self.nonce)
 def test_39_new_nonce_must_have_new_signatures(self):
  with self.assertRaises(ValueError):self.g.accept(self.responses,b'new-nonce-abcdef123')
 def test_40_wrong_sample_path(self):
  r=copy.deepcopy(self.responses);r[0]['body']['samples'][0]['path'][0]='00'*32;r[0]['signature']=self.hosts[0].key.sign(canon(r[0]['body'])).hex()
  with self.assertRaises(ValueError):self.g.accept(r,self.nonce)
if __name__=='__main__':unittest.main()