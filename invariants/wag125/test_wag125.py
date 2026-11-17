import unittest,tempfile,sqlite3
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from wag125 import *
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.ks={n:K.generate() for n in 'HON'};self.keys={n:k.public_key() for n,k in self.ks.items()};self.a=[Anchor(Path(self.tmp.name)/n) for n in 'HON'];self.op={'kind':'send','src':0,'dst':1,'q':26,'id':'p'}
 def event(self,s,o):
  m=message('mesh',s,o);return {'message':m,'op':o,'cert':{n:k.sign(enc(m)).hex() for n,k in self.ks.items()}}
 def put(self,o):
  e=self.event(replay('mesh',self.keys,self.a[0].read()),o)
  for a in self.a:a.append('mesh',self.keys,e)
  return e
 def check(self):return inspect('mesh',self.keys,[a.read() for a in self.a])
 def test_origin(self):self.assertEqual(self.check(),('CURRENT',genesis()))
 def test_transfer(self):self.put(self.op);self.put({'kind':'graduate'});self.put({'kind':'receive','id':'p'});self.assertEqual(self.check()[1]['balances'],[130,26,0])
 def test_rollback(self):
  self.put(self.op)
  with sqlite3.connect(self.a[0].path) as c:c.execute('DELETE FROM log')
  self.assertEqual(self.check()[0],'HOLD_LAG')
 def test_partial(self):self.a[0].append('mesh',self.keys,self.event(genesis(),self.op));self.assertEqual(self.check()[0],'HOLD_LAG')
 def test_missing(self):self.assertEqual(inspect('mesh',self.keys,[[],[],None])[0],'HOLD_MISSING')
 def test_forgery(self):
  e=self.event(genesis(),self.op);e['cert']['H']='00'*64;self.assertEqual(inspect('mesh',self.keys,[[e],[],[]])[0],'HOLD_INVALID')
 def test_fork(self):
  a=self.event(genesis(),self.op);b=self.event(genesis(),{'kind':'graduate'});self.assertEqual(inspect('mesh',self.keys,[[a],[b],[a]])[0],'HOLD_FORK')
 def test_scope(self):e=self.event(genesis(),self.op);self.assertEqual(inspect('other',self.keys,[[e]]*3)[0],'HOLD_INVALID')
 def test_restart(self):self.put(self.op);self.a=[Anchor(a.path) for a in self.a];self.assertEqual(self.check()[0],'CURRENT')
 def test_common_rollback_limit(self):
  self.put(self.op)
  for a in self.a:
   with sqlite3.connect(a.path) as c:c.execute('DELETE FROM log')
  self.assertEqual(self.check(),('CURRENT',genesis()))
if __name__=='__main__':unittest.main(verbosity=2)
