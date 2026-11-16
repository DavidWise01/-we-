"""WAG-081 compact repository smoke suite; full 34-test suite supplied locally."""
import unittest,tempfile,sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'wag079'))
from wag081 import AtomicGate,Hold
from wag079 import merkle_root,create_proof
class Tests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.keys={n:Ed25519PrivateKey.generate() for n in ['W1','W2','W3']}
  pub={n:k.public_key().public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw) for n,k in self.keys.items()}
  self.leaves=tuple(x.encode() for x in 'ABCDE');self.old=merkle_root(self.leaves[:3]).hex();self.new=merkle_root(self.leaves).hex()
  self.proof=create_proof(self.leaves,3);self.g=AtomicGate(Path(self.temp.name)/'state.db',pub,3,self.old,'nonce081-test')
 def votes(self,proof=None,new=None):
  p=proof or self.proof;r=new or self.new;s=self.g.state()
  msg=self.g.signable(s['epoch'],s['challenge'],s['size'],s['root'],p,r)
  return [(n,n+'-receipt',k.sign(msg)) for n,k in self.keys.items()]
 def test_good(self):
  s=self.g.state();self.assertEqual(self.g.advance(self.proof,self.new,self.votes(),tuple(s.values())),'LOCAL_ATOMIC_ADVANCED')
 def test_epoch(self):
  s=self.g.state();self.g.advance(self.proof,self.new,self.votes(),tuple(s.values()));self.assertEqual(self.g.state()['epoch'],1)
 def test_replay(self):
  s=self.g.state();v=self.votes();self.g.advance(self.proof,self.new,v,tuple(s.values()))
  with self.assertRaises(Hold):self.g.advance(self.proof,self.new,v,tuple(s.values()))
 def test_invalid_prefix(self):
  fake=(b'A',b'X',b'C',b'D',b'E');p=create_proof(fake,3)
  with self.assertRaises(Hold):self.g.advance(p,merkle_root(fake).hex(),self.votes(p,merkle_root(fake).hex()),tuple(self.g.state().values()))
 def test_signature(self):
  s=self.g.state();v=self.votes();v[0]=(v[0][0],v[0][1],b'bad')
  with self.assertRaises(Hold):self.g.advance(self.proof,self.new,v,tuple(s.values()))
 def test_missing_vote(self):
  with self.assertRaises(Hold):self.g.advance(self.proof,self.new,self.votes()[:2],tuple(self.g.state().values()))
 def test_atomic_invalid(self):
  s=self.g.state()
  with self.assertRaises(Hold):self.g.advance(self.proof,self.new,[],tuple(s.values()))
  self.assertEqual(self.g.state(),s)
 def test_restart(self):
  s=self.g.state();self.g.advance(self.proof,self.new,self.votes(),tuple(s.values()))
  self.assertEqual(AtomicGate(Path(self.temp.name)/'state.db',self.g.keys).state()['root'],self.new)
if __name__=='__main__':unittest.main()
