import unittest,tempfile
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from wag102 import Gate,canon
class Tests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.path=Path(t.name)/'gate.db'
  self.g={'A':[],'B':[],'C':[]};self.actors=('A','B','C')
  self.p={n:Ed25519PrivateKey.generate() for n in ('X','Y')}
  self.keys={n:k.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw) for n,k in self.p.items()}
  self.a=Gate(self.path,self.g,self.actors,self.keys);self.new={**self.g,'D':[],'A':['D']}
 def sign(self,p):return {n:k.sign(canon(p)) for n,k in self.p.items()}
 def test_accept(self):
  p=self.a.proposal(self.new);self.assertEqual(self.a.evaluate(self.new,p,self.sign(p)),'LOCAL_CORRECTION_ACCEPTED')
 def test_shared(self):
  g={**self.g,'A':['B']};p=self.a.proposal(g);self.assertEqual(self.a.evaluate(g,p,self.sign(p)),'HOLD_SHARED_CONTROL')
 def test_missing(self):
  p=self.a.proposal(self.new);self.assertEqual(self.a.evaluate(self.new,p,{}),'HOLD_CORROBORATION')
 def test_replay(self):
  p=self.a.proposal(self.new);s=self.sign(p);self.a.evaluate(self.new,p,s);self.assertEqual(self.a.evaluate(self.new,p,s),'HOLD_STALE')
 def test_restart(self):
  p=self.a.proposal(self.new);self.a.evaluate(self.new,p,self.sign(p));b=Gate(self.path,self.g,self.actors,self.keys);self.assertEqual(b.state(),(1,self.new));self.assertTrue(b.verify_audit())
if __name__=='__main__':unittest.main()
