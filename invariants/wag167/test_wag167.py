import unittest,tempfile
from pathlib import Path
from wag167 import *
class Tests(unittest.TestCase):
 def setUp(self):
    self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.d=Path(self.tmp.name)
    self.rs=records(167);self.x=list(map(leaf,self.rs));self.old=root(self.x[:166]);self.a=statement('mesh',166,167,self.old,root(self.x));self.p=proof(self.x,166)
    y=self.x[:-1]+[leaf({'alternate':True})];self.b=statement('mesh',166,167,self.old,root(y));self.q=proof(y,166)
    self.k=[Ed25519PrivateKey.generate() for _ in range(3)];self.reg={str(i):(str(i),k.public_key()) for i,k in enumerate(self.k)}
 def w(self,i,suffix=''):return Witness(self.d/f'{i}{suffix}.db','mesh',str(i),self.k[i],166,self.old)
 def collect(self,s,p,suffix=''):return {str(i):self.w(i,suffix).sign(s,p) for i in range(3)}
 def test_valid(self):self.assertTrue(certify(self.a,self.reg,self.collect(self.a,self.p)))
 def test_both_proofs_valid(self):self.assertTrue(verify(166,167,self.old,bytes.fromhex(self.b[-1]),self.q))
 def test_fork(self):
    self.collect(self.a,self.p)
    for i in range(3):self.assertRaises(ValueError,self.w(i).sign,self.b,self.q)
 def test_restart(self):self.w(0).sign(self.a,self.p);self.assertRaises(ValueError,self.w(0).sign,self.a,self.p)
 def test_two(self):
    s=self.collect(self.a,self.p);del s['2'];self.assertRaises(ValueError,certify,self.a,self.reg,s)
 def test_shared_root(self):
    self.reg['2']=('1',self.k[2].public_key());self.assertRaises(ValueError,certify,self.a,self.reg,self.collect(self.a,self.p))
 def test_tampered_proof(self):self.assertRaises(ValueError,self.w(0).sign,self.a,self.p[:-1])
 def test_reset_counterexample(self):
    self.assertTrue(certify(self.a,self.reg,self.collect(self.a,self.p)))
    self.assertTrue(certify(self.b,self.reg,self.collect(self.b,self.q,'reset')))
 def test_prior_root(self):self.assertEqual(self.old.hex(),'6c2ddd404b4a5cc3f926b58a0a6c91be5bf21bb6d1c376423830b2b1c616c7d3')
if __name__=='__main__':unittest.main(verbosity=2)
