import unittest,itertools
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag122 import *
class Tests(unittest.TestCase):
 def setup_mesh(self):
  ws=[Witness(n,Ed25519PrivateKey.generate()) for n in 'HON'];return ws,{w.name:w.key.public_key() for w in ws}
 def test_exhaustive(self):
  for vals in itertools.product([None,'A','B'],repeat=3):
   ws,keys=self.setup_mesh();votes={w.name:[v,w.vote(v)] for w,v in zip(ws,vals) if v is not None};proof={w.name:w.close() for w in ws}
   old=any(certified(0,v,votes,keys) for v in ['A','B']);self.assertEqual(decision(0,proof,keys),'RECOVER_OLD_CERTIFICATE' if old else 'ADVANCE')
   if not old:
    for w in ws:w.advance(proof,keys)
    fresh={w.name:['B',w.vote('B')] for w in ws};self.assertTrue(certified(1,'B',fresh,keys))
 def test_closed(self):
  ws,k=self.setup_mesh();ws[0].close()
  with self.assertRaises(ValueError):ws[0].vote('A')
 def test_missing(self):
  ws,k=self.setup_mesh();self.assertEqual(decision(0,{w.name:w.close() for w in ws[:2]},k),'HOLD_INVALID')
 def test_forged(self):
  ws,k=self.setup_mesh();p={w.name:w.close() for w in ws};p['H'][0]='A';self.assertEqual(decision(0,p,k),'HOLD_INVALID')
 def test_replay(self):
  ws,k=self.setup_mesh();p={w.name:w.close() for w in ws};self.assertEqual(decision(1,p,k),'HOLD_INVALID')
 def test_lock(self):
  ws,k=self.setup_mesh();ws[0].vote('A')
  with self.assertRaises(ValueError):ws[0].vote('B')
 def test_old_certificate(self):
  ws,k=self.setup_mesh();p={w.name:['A',w.vote('A')] for w in ws};self.assertTrue(certified(0,'A',p,k));c={w.name:w.close() for w in ws}
  with self.assertRaises(ValueError):ws[0].advance(c,k)
if __name__=='__main__':unittest.main()
