import unittest,hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag094 import Gate,sign,demo
def setup():
 keys=[Ed25519PrivateKey.generate() for _ in range(3)]
 authors={name:{'key':key.public_key(),'root':'r'+name,'operator':'o'+name,'domain':'d'+name} for name,key in zip(('clock','b','c'),keys)}
 g=Gate(authors,hashlib.sha256(b'archive').hexdigest(),94,'round-01')
 msgs=[{'kind':'commit','authority':'clock','epoch':94,'round':'round-01','root':g.root,'slot':12}]
 msgs +=[{'kind':'release','authority':name,'epoch':94,'round':'round-01','root':g.root,'slot':13+i,'output':hashlib.sha256(name.encode()).hexdigest()} for i,name in enumerate(('b','c'))]
 return g,keys,msgs
class Tests(unittest.TestCase):
 def setUp(self):self.g,self.keys,self.msgs=setup()
 def add(self,i):self.g.add(self.msgs[i],sign(self.keys[i],self.msgs[i]))
 def test_valid(self):self.add(0);self.add(1);self.add(2);self.assertEqual(len(set(self.g.sample())),3)
 def test_demo(self):self.assertTrue(demo()['audit_valid'])
 def test_missing_commit(self):
  with self.assertRaises(ValueError):self.add(1)
 def test_missing_beacon(self):
  self.add(0);self.add(1)
  with self.assertRaises(ValueError):self.g.sample()
 def test_repeat_commit(self):
  self.add(0)
  with self.assertRaises(ValueError):self.add(0)
 def test_repeat_beacon(self):
  self.add(0);self.add(1)
  with self.assertRaises(ValueError):self.add(1)
 def test_bad_sig(self):
  with self.assertRaises(ValueError):self.g.add(self.msgs[0],sign(self.keys[1],self.msgs[0]))
 def test_early_release(self):
  self.add(0);m={**self.msgs[1],'slot':12}
  with self.assertRaises(ValueError):self.g.add(m,sign(self.keys[1],m))
 def test_wrong_root(self):
  self.add(0);m={**self.msgs[1],'root':'f'*64}
  with self.assertRaises(ValueError):self.g.add(m,sign(self.keys[1],m))
 def test_wrong_round(self):
  self.add(0);m={**self.msgs[1],'round':'other'}
  with self.assertRaises(ValueError):self.g.add(m,sign(self.keys[1],m))
 def test_wrong_epoch(self):
  self.add(0);m={**self.msgs[1],'epoch':13}
  with self.assertRaises(ValueError):self.g.add(m,sign(self.keys[1],m))
 def test_bad_output(self):
  self.add(0);m={**self.msgs[1],'output':'x'}
  with self.assertRaises(ValueError):self.g.add(m,sign(self.keys[1],m))
 def test_sample_twice(self):
  for i in range(3):self.add(i)
  self.g.sample()
  with self.assertRaises(ValueError):self.g.sample()
 def test_audit(self):
  for i in range(3):self.add(i)
  self.g.sample();self.assertTrue(self.g.verify())
 def test_tamper(self):
  self.add(0);self.g.events[1]['data']['slot']=99;self.assertFalse(self.g.verify())
 def test_audit_count(self):
  for i in range(3):self.add(i)
  self.g.sample();self.assertEqual(len(self.g.events),5)
 def test_shared_domain(self):
  self.g.authors['b']['domain']=self.g.authors['clock']['domain']
  with self.assertRaises(ValueError):Gate(self.g.authors,self.g.root,94,'round-01')
if __name__=='__main__':unittest.main()
