import unittest,tempfile,itertools
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from wag123 import Witness,decision
class Tests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.ks={n:K.generate() for n in 'HON'};self.keys={n:k.public_key() for n,k in self.ks.items()};self.scope=['mesh',1,'prior'];self.ws=self.reopen()
 def reopen(self):return [Witness(Path(self.t.name)/n,n,k,self.scope,self.keys) for n,k in self.ks.items()]
 def close(self):return {w.name:w.close() for w in self.ws}
 def test_restart_closed(self):
  self.ws[0].vote('A');p=self.close();self.ws=self.reopen();self.assertEqual(self.close(),p)
  with self.assertRaises(ValueError):self.ws[0].vote('A')
 def test_advance_restart(self):
  p=self.close();self.assertEqual(self.ws[0].advance(p),1);self.ws=self.reopen();self.ws[0].vote('B')
  with self.assertRaises(ValueError):self.ws[0].advance(p)
 def test_old_unanimous(self):
  for w in self.ws:w.vote('A')
  p=self.close();self.assertEqual(decision(self.scope,0,p,self.keys),'RECOVER')
  with self.assertRaises(ValueError):self.ws[0].advance(p)
 def test_conflict(self):
  self.ws[0].vote('A');self.ws[1].vote('B');p=self.close();self.assertEqual(decision(self.scope,0,p,self.keys),'ADVANCE')
  for w in self.ws:self.assertEqual(w.advance(p),1)
 def test_scope(self):
  p=self.close()
  for scope in [['other',1,'prior'],['mesh',2,'prior'],['mesh',1,'other']]:self.assertEqual(decision(scope,0,p,self.keys),'HOLD')
 def test_missing(self):
  p=self.close();p.pop('H');self.assertEqual(decision(self.scope,0,p,self.keys),'HOLD')
 def test_tamper(self):
  p=self.close();p['H'][0]='A';self.assertEqual(decision(self.scope,0,p,self.keys),'HOLD')
 def test_lock_restart(self):
  self.ws[0].vote('A');self.ws=self.reopen()
  with self.assertRaises(ValueError):self.ws[0].vote('B')
 def test_scope_reopen(self):
  self.scope=['mesh',2,'prior']
  with self.assertRaises(ValueError):self.reopen()
 def test_partial_advance(self):
  p=self.close();self.ws[0].advance(p);self.ws=self.reopen()
  for w in self.ws[1:]:self.assertEqual(w.advance(p),1)
if __name__=='__main__':unittest.main()
