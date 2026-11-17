import unittest,tempfile,random
from pathlib import Path
from wag120 import Mesh
class Tests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.paths=[Path(self.t.name)/x for x in 'HON'];self.m=Mesh(self.paths);self.p={'id':'p','src':0,'dst':1,'q':26}
 def test_genesis(self): self.assertEqual(self.m.total(),156)
 def test_send_receive(self):
  self.m.submit('send',self.p);self.assertEqual(self.m.total(),156);self.m.submit('receive',self.p);self.assertEqual(self.m.inspect()[0]['balances'],[130,26,0])
 def test_partial(self):
  self.m.submit('send',self.p,1)
  with self.assertRaises(ValueError):self.m.inspect()
 def test_repair(self):
  self.m.submit('send',self.p,2);self.m=Mesh(self.paths);self.m.repair();self.assertEqual(self.m.total(),156)
 def test_duplicate(self):
  self.m.submit('send',self.p);self.m.submit('receive',self.p)
  with self.assertRaises(ValueError):self.m.submit('receive',self.p)
 def test_bad_direction(self):
  with self.assertRaises(ValueError):self.m.submit('send',{**self.p,'dst':2})
 def test_overspend(self):
  with self.assertRaises(ValueError):self.m.submit('send',{**self.p,'q':157})
 def test_restart(self):
  self.m.submit('send',self.p);self.m=Mesh(self.paths);self.assertEqual(self.m.total(),156)
 def test_random(self):
  r=random.Random(120)
  for i in range(100):
   s,_=self.m.inspect();a=r.randrange(3)
   if s['balances'][a]:
    p={'id':str(i),'src':a,'dst':(a+1)%3,'q':r.randint(1,s['balances'][a])};self.m.submit('send',p);self.m.submit('receive',p)
   self.assertEqual(self.m.total(),156)
 def test_fork(self):
  from wag120 import digest,GENESIS
  for j,q in zip(self.m.j,[1,2,1]):j.append({'seq':1,'prev':digest(GENESIS),'kind':'send','packet':{**self.p,'q':q}})
  with self.assertRaises(ValueError):self.m.repair()
if __name__=='__main__':unittest.main()
