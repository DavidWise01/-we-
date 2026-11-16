"""Compact smoke tests for WAG-085 GitHub reference; full local suite has 35 tests."""
import unittest,tempfile
from pathlib import Path
from dataclasses import replace
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag085 import Host,Gate,Challenge,H
class TestWAG085(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  root=Path(self.tmp.name);self.data=b'checkpoint';keys={n:Ed25519PrivateKey.generate() for n in ['W1','W2','W3']}
  self.hosts={n:Host(n,root/n,k) for n,k in keys.items()}
  for h in self.hosts.values():h.persist(self.data)
  self.g=Gate(root/'gate.db',{n:k.public_key() for n,k in keys.items()},{'W1':'a','W2':'b','W3':'c'},self.data)
  self.c=Challenge(85,H(self.data),'nonce');self.g.register(self.c)
 def proofs(self):return [h.answer(self.c) for h in self.hosts.values()]
 def test_accept(self):self.assertEqual(self.g.check(self.c,self.proofs()),'LOCAL_FRESH_STORAGE_ELIGIBLE')
 def test_replay(self):
  p=self.proofs();self.g.check(self.c,p)
  with self.assertRaises(ValueError):self.g.check(self.c,p)
 def test_restart(self):
  p=self.proofs();self.g.check(self.c,p)
  g=Gate(Path(self.tmp.name)/'gate.db',{n:h.key.public_key() for n,h in self.hosts.items()},{'W1':'a','W2':'b','W3':'c'},self.data)
  with self.assertRaises(ValueError):g.check(self.c,p)
 def test_short_quorum(self):
  with self.assertRaises(ValueError):self.g.check(self.c,self.proofs()[:2])
 def test_bad_content(self):
  self.hosts['W1'].persist(b'tampered')
  with self.assertRaises(ValueError):self.g.check(self.c,self.proofs())
 def test_missing_file(self):
  (Path(self.tmp.name)/'W1'/'checkpoint').unlink()
  with self.assertRaises(FileNotFoundError):self.hosts['W1'].answer(self.c)
 def test_forged(self):
  p=self.proofs();p[0]=replace(p[0],signature=Ed25519PrivateKey.generate().sign(p[0].message()))
  with self.assertRaises(ValueError):self.g.check(self.c,p)
 def test_wrong_challenge(self):
  p=self.proofs();p[0]=replace(p[0],challenge_id='x')
  with self.assertRaises(ValueError):self.g.check(self.c,p)
 def test_duplicate_nonce(self):
  with self.assertRaises(Exception):self.g.register(Challenge(86,self.c.root,self.c.nonce))
 def test_stale_epoch(self):
  self.g.register(Challenge(86,self.c.root,'another'))
  with self.assertRaises(ValueError):self.g.register(Challenge(84,self.c.root,'stale'))
 def test_atomic_reject(self):
  with self.assertRaises(ValueError):self.g.check(self.c,self.proofs()[:1])
  self.assertEqual(self.g.check(self.c,self.proofs()),'LOCAL_FRESH_STORAGE_ELIGIBLE')
 def test_wrong_root(self):
  with self.assertRaises(ValueError):self.g.register(Challenge(85,'0'*64,'other'))
if __name__=='__main__':unittest.main()
