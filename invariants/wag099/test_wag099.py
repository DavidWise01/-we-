import unittest,tempfile,os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag099 import Head,Witness,Gate,demo
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=os.path.join(self.tmp.name,'gate.db')
  self.keys={n:Ed25519PrivateKey.generate() for n in ('W1','W2','W3')}
  self.h=Head(3,'a'*64,99)
  self.ws=[Witness(n,n+'-root',n+'-domain',key.public_key()) for n,key in self.keys.items()]
  self.g=Gate(self.path,self.ws,self.h,'nonce-99')
 def tearDown(self):self.g.close();self.tmp.cleanup()
 def sign(self,n,h=None,nonce=None):return self.keys[n].sign(self.g.statement(n,h or self.h,nonce))
 def fill(self):
  for n in self.keys:self.assertEqual(self.g.observe(n,self.h,self.sign(n)),'RECORDED')
 def test_demo(self):self.assertTrue(demo()['audit_valid'])
 def test_accept(self):self.fill();self.assertEqual(self.g.certify(),'LOCAL_CURRENT_AGREEMENT')
 def test_revoked(self):self.fill();self.g.revoke('W1',99);self.assertEqual(self.g.certify(),'HOLD_REVOKED')
 def test_history(self):s=self.sign('W1');self.g.revoke('W1',99);self.assertTrue(self.g.historical_signature('W1',self.h,'nonce-99',s))
 def test_forgery(self):self.assertEqual(self.g.observe('W1',self.h,self.sign('W2')),'REJECT_SIGNATURE')
 def test_replay(self):self.g.observe('W1',self.h,self.sign('W1'));self.assertEqual(self.g.observe('W1',self.h,self.sign('W1')),'REJECT_REPLAY')
 def test_stale_nonce(self):self.assertEqual(self.g.observe('W1',self.h,self.sign('W1',nonce='old'),nonce='old'),'HOLD_STALE')
 def test_stale_epoch(self):
  h=Head(3,'a'*64,98);self.assertEqual(self.g.observe('W1',h,self.sign('W1',h)),'HOLD_STALE')
 def test_missing_quorum(self):self.assertEqual(self.g.certify(),'HOLD_QUORUM')
 def test_conflict(self):
  h=Head(3,'b'*64,99);self.assertEqual(self.g.observe('W1',h,self.sign('W1',h)),'QUARANTINE_CONFLICT');self.assertEqual(self.g.certify(),'QUARANTINE_CONFLICT')
 def test_persistent_conflict(self):
  h=Head(3,'b'*64,99);self.g.observe('W1',h,self.sign('W1',h));self.g.close();self.g=Gate(self.path,self.ws,self.h,'nonce-99');self.assertEqual(self.g.certify(),'QUARANTINE_CONFLICT')
 def test_future_revocation(self):self.fill();self.g.revoke('W1',100);self.assertEqual(self.g.certify(),'LOCAL_CURRENT_AGREEMENT')
 def test_tamper(self):self.g.db.execute("UPDATE events SET body='{}' WHERE seq=0");self.g.db.commit();self.assertFalse(self.g.verify())
 def test_restart(self):self.fill();self.g.close();self.g=Gate(self.path,self.ws,self.h,'nonce-99');self.assertEqual(self.g.certify(),'LOCAL_CURRENT_AGREEMENT')
if __name__=='__main__':unittest.main()
