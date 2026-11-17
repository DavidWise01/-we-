import unittest,tempfile,sqlite3
from contextlib import closing
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from wag103 import Gate,canon
class Tests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.path=Path(t.name)/'gate.db'
  self.g={'A':[],'B':[],'C':[]};self.new={**self.g,'D':[],'A':['D']};self.bad={**self.g,'A':['B']}
  self.private={n:Ed25519PrivateKey.generate() for n in 'XYZQ'}
  self.pub={n:k.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw) for n,k in self.private.items()};self.a=self.open()
 def open(self):return Gate(self.path,self.g,('A','B','C'),{n:self.pub[n] for n in 'XYZ'},self.pub['Q'],'demo')
 def anchor(self):
  a=self.a.anchor_statement();return a,self.private['Q'].sign(canon(a))
 def proposal(self,g):
  p=self.a.proposal(g);return p,{n:self.private[n].sign(canon(p)) for n in 'XYZ'}
 def repair(self):
  self.a.observe(self.bad);return self.a.revalidate(self.new,*self.proposal(self.new))
 def test_initial(self):self.assertEqual(self.a.decision(*self.anchor()),'LOCAL_ELIGIBLE')
 def test_mutation(self):self.assertEqual(self.a.observe(self.bad),'HOLD_MUTATION')
 def test_restart(self):
  self.a.observe(self.bad);self.a=self.open();self.assertEqual(self.a.decision(*self.anchor()),'HOLD_MUTATION')
 def test_original_does_not_clear(self):
  self.a.observe(self.bad);self.assertEqual(self.a.observe(self.g),'HOLD_MUTATION')
 def test_shared(self):
  self.a.observe(self.bad);self.assertEqual(self.a.revalidate(self.bad,*self.proposal(self.bad)),'HOLD_SHARED_CONTROL')
 def test_unknown(self):
  self.a.observe(self.bad);g={**self.g,'A':['missing']};self.assertEqual(self.a.revalidate(g,*self.proposal(g)),'HOLD_ANCESTRY')
 def test_cycle(self):
  self.a.observe(self.bad);g={**self.g,'A':['A']};self.assertEqual(self.a.revalidate(g,*self.proposal(g)),'HOLD_ANCESTRY')
 def test_missing_signature(self):
  self.a.observe(self.bad);p,s=self.proposal(self.new);del s['Z'];self.assertEqual(self.a.revalidate(self.new,p,s),'HOLD_QUORUM')
 def test_forged(self):
  self.a.observe(self.bad);p,s=self.proposal(self.new);s['X']=s['Y'];self.assertEqual(self.a.revalidate(self.new,p,s),'HOLD_SIGNATURE')
 def test_pending(self):self.assertEqual(self.repair(),'HOLD_PENDING_ANCHOR')
 def test_old_anchor(self):
  old=self.anchor();self.repair();self.assertEqual(self.a.decision(*old),'HOLD_ANCHOR_MISMATCH')
 def test_new_anchor(self):
  self.repair();self.assertEqual(self.a.decision(*self.anchor()),'LOCAL_ELIGIBLE')
 def test_replay(self):
  self.a.observe(self.bad);p,s=self.proposal(self.new);self.a.revalidate(self.new,p,s);self.assertEqual(self.a.revalidate(self.new,p,s),'HOLD_STALE')
 def test_new_mutation_invalidates_proposal(self):
  self.a.observe(self.bad);p,s=self.proposal(self.new);self.a.observe(self.new);self.assertEqual(self.a.revalidate(self.new,p,s),'HOLD_STALE')
 def test_forged_anchor(self):
  a,s=self.anchor();self.assertEqual(self.a.decision(a,b'bad'),'HOLD_ANCHOR_SIGNATURE')
 def test_rollback(self):
  old=self.a.state();self.repair();anchor=self.anchor()
  with closing(sqlite3.connect(self.path)) as c,c:c.execute('UPDATE state SET body=?',(canon(old).decode(),))
  self.assertEqual(self.a.decision(*anchor),'HOLD_ANCHOR_MISMATCH')
 def test_audit(self):self.repair();self.assertTrue(self.a.verify_audit())
 def test_audit_tamper(self):
  self.repair()
  with closing(sqlite3.connect(self.path)) as c,c:c.execute("UPDATE audit SET hash='bad' WHERE seq=0")
  self.assertFalse(self.a.verify_audit())
 def test_reopen_after_repair(self):
  self.repair();anchor=self.anchor();self.a=self.open();self.assertEqual(self.a.decision(*anchor),'LOCAL_ELIGIBLE')
if __name__=='__main__':unittest.main()
