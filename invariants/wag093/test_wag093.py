import unittest, tempfile, json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag093 import H,enc,root_proof,included,sample,Gate,demonstration
class Tests(unittest.TestCase):
 def setUp(self):
  self.chunks=[f'chunk-{i}'.encode() for i in range(17)]
  self.root=root_proof(self.chunks,0)[0]
  self.beacon=Ed25519PrivateKey.generate()
  self.keys={f'W{i}':Ed25519PrivateKey.generate() for i in (1,2,3)}
  self.g=Gate(':memory:',self.beacon.public_key(),{k:v.public_key() for k,v in self.keys.items()})
 def tearDown(self):self.g.close()
 def ready(self):
  self.g.freeze(93,self.root,17,'receipt-1')
  b={'v':'WAG093','epoch':93,'value':'beacon'}
  ids=self.g.beacon(b,self.beacon.sign(enc(b)).hex())
  nonce=self.g.db.execute('SELECT nonce FROM state').fetchone()[0]
  rs=[]
  for name,key in self.keys.items():
   samples=[{'i':i,'data':self.chunks[i].hex(),'siblings':root_proof(self.chunks,i)[1]} for i in ids]
   body={'host':name,'epoch':93,'root':self.root.hex(),'nonce':nonce,'samples':samples}
   rs.append({'body':body,'signature':key.sign(enc(body)).hex()})
  return ids,rs
 def test_demo(self):self.assertEqual(demonstration()['decision'],'LOCAL_E2E_SAMPLED_STORAGE_ELIGIBLE')
 def test_paths(self):
  for i,data in enumerate(self.chunks):self.assertTrue(included(data,i,17,root_proof(self.chunks,i)[1],self.root))
 def test_changed_data(self):self.assertFalse(included(b'x',0,17,root_proof(self.chunks,0)[1],self.root))
 def test_changed_root(self):self.assertFalse(included(self.chunks[0],0,17,root_proof(self.chunks,0)[1],b'0'*32))
 def test_sample_unique(self):self.assertEqual(len(set(sample(b'a'*32,17,3))),3)
 def test_sample_deterministic(self):self.assertEqual(sample(b'a'*32,17,3),sample(b'a'*32,17,3))
 def test_freeze_once(self):
  self.g.freeze(93,self.root,17,'receipt')
  with self.assertRaises(ValueError):self.g.freeze(93,self.root,17,'receipt')
 def test_beacon_forged(self):
  self.g.freeze(93,self.root,17,'receipt')
  with self.assertRaises(ValueError):self.g.beacon({'v':'WAG093','epoch':93,'value':'x'},'00'*64)
 def test_beacon_before_freeze(self):
  with self.assertRaises(ValueError):self.g.beacon({},'00'*64)
 def test_beacon_fixed(self):
  self.ready()
  b={'v':'WAG093','epoch':93,'value':'another'}
  with self.assertRaises(ValueError):self.g.beacon(b,self.beacon.sign(enc(b)).hex())
 def test_accept(self):self.assertEqual(self.g.certify(self.ready()[1]),'LOCAL_E2E_SAMPLED_STORAGE_ELIGIBLE')
 def test_no_replay(self):
  rs=self.ready()[1];self.g.certify(rs)
  with self.assertRaises(ValueError):self.g.certify(rs)
 def test_missing(self):
  rs=self.ready()[1]
  with self.assertRaises(ValueError):self.g.certify(rs[:2])
 def test_duplicate(self):
  rs=self.ready()[1]
  with self.assertRaises(ValueError):self.g.certify([rs[0],rs[0],rs[2]])
 def test_tampered_chunk(self):
  rs=self.ready()[1];rs[0]['body']['samples'][0]['data']='00'
  rs[0]['signature']=self.keys['W1'].sign(enc(rs[0]['body'])).hex()
  with self.assertRaises(ValueError):self.g.certify(rs)
 def test_forged_signature(self):
  rs=self.ready()[1];rs[0]['signature']='00'*64
  with self.assertRaises(ValueError):self.g.certify(rs)
 def test_rollback_then_success(self):
  rs=self.ready()[1]
  with self.assertRaises(ValueError):self.g.certify([rs[0],rs[0],rs[2]])
  self.assertEqual(self.g.certify(rs),'LOCAL_E2E_SAMPLED_STORAGE_ELIGIBLE')
if __name__=='__main__':unittest.main()
