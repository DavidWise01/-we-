import unittest,tempfile,random
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from wag121 import *
class Tests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.ks={n:K.generate() for n in 'HON'};self.keys={n:k.public_key() for n,k in self.ks.items()};self.ws=self.reopen();self.p={'src':0,'dst':1,'q':26,'id':'p'}
 def reopen(self):return [Witness(Path(self.t.name)/n,n,k,self.keys) for n,k in self.ks.items()]
 def event(self,kind='send',p=None):
  s=self.ws[0].read();return {'seq':s['seq']+1,'prev':digest(s),'kind':kind,'packet':p or self.p}
 def prep(self,e):return {w.name:w.prepare(e) for w in self.ws}
 def commit(self,e):
  c=self.prep(e)
  for w in self.ws:w.commit(e,c)
 def test_transfer(self):
  self.commit(self.event());self.commit(self.event('receive'));self.assertEqual(self.ws[0].read()['balances'],[130,26,0])
 def test_partial(self):
  self.ws[0].prepare(self.event());self.assertEqual(recover(self.ws,1),'HOLD_INCOMPLETE');self.assertEqual(self.ws[0].read(),GEN)
 def test_lock_restart(self):
  e=self.event();self.ws[0].prepare(e);self.ws=self.reopen()
  with self.assertRaises(ValueError):self.ws[0].prepare(self.event(p={**self.p,'q':1}))
 def test_prepare_retry(self):
  e=self.event();self.assertEqual(self.ws[0].prepare(e),self.ws[0].prepare(e))
 def test_recover_all_prepared(self):
  self.prep(self.event());self.ws=self.reopen();self.assertEqual(recover(self.ws,1),'COMMITTED')
 def test_recover_partial_commit(self):
  e=self.event();c=self.prep(e);self.ws[0].commit(e,c);self.ws=self.reopen();self.assertEqual(recover(self.ws,1),'COMMITTED');self.assertEqual(len({digest(w.read()) for w in self.ws}),1)
 def test_forged(self):
  e=self.event();c=self.prep(e);c['H']='00'*64
  with self.assertRaises(ValueError):self.ws[0].commit(e,c)
 def test_missing_vote(self):
  e=self.event();c=self.prep(e);del c['N']
  with self.assertRaises(ValueError):self.ws[0].commit(e,c)
 def test_conflict(self):
  e=self.event();self.ws[0].prepare(e);self.ws[1].prepare(self.event(p={**self.p,'q':1}));self.ws[2].prepare(e);self.assertEqual(recover(self.ws,1),'HOLD_CONFLICT')
 def test_duplicate_commit(self):
  e=self.event();c=self.prep(e);self.ws[0].commit(e,c);self.ws[0].commit(e,c);self.assertEqual(total(self.ws[0].read()),156)
 def test_overspend(self):
  with self.assertRaises(ValueError):self.prep(self.event(p={**self.p,'q':157}))
 def test_wrong_direction(self):
  with self.assertRaises(ValueError):self.prep(self.event(p={**self.p,'dst':2}))
 def test_replay_receipt(self):
  self.commit(self.event());self.commit(self.event('receive'))
  with self.assertRaises(ValueError):self.prep(self.event('receive'))
 def test_random(self):
  r=random.Random(121)
  for i in range(40):
   s=self.ws[0].read();a=r.choice([a for a in range(3) if s['balances'][a]]);p={'src':a,'dst':(a+1)%3,'q':r.randint(1,s['balances'][a]),'id':str(i)};self.commit(self.event(p=p));self.commit(self.event('receive',p));self.assertTrue(all(total(w.read())==156 for w in self.ws))
if __name__=='__main__':unittest.main()
