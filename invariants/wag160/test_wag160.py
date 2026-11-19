import unittest,tempfile,concurrent.futures
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from cryptography.exceptions import InvalidSignature
from wag160 import *
class Tests(unittest.TestCase):
 def setUp(self):
    t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.path=Path(t.name)/'db';self.k=[K.generate() for _ in range(10)];self.pub=[k.public_key() for k in self.k];self.g=Gate(self.path,self.pub);self.s=self.g.head();self.p=self.g.propose()
 def yes(self,p):return {i:self.k[i].sign(enc(['YES',i,p])) for i in p[2]}
 def no(self,p,i=1):return {i:self.k[i].sign(enc(['NO',i,p]))}
 def test_withdraw_first(self):
    t=self.g.execute(self.p,self.no(self.p),1);self.assertEqual(t['x'],self.s['x']);self.assertEqual(t['spent'],0);self.assertRaises(ValueError,self.g.execute,self.p,self.yes(self.p))
 def test_commit_first(self):
    t=self.g.execute(self.p,self.yes(self.p));self.assertEqual(t['x'],[2]*10);self.assertRaises(ValueError,self.g.execute,self.p,self.no(self.p),1);self.assertEqual(self.g.head(),t)
 def test_restart(self):
    self.g.execute(self.p,self.no(self.p),1);g=Gate(self.path,self.pub);self.assertRaises(ValueError,g.execute,self.p,self.yes(self.p))
 def test_new_consent(self):
    self.g.execute(self.p,self.no(self.p),1);p=self.g.propose();self.assertEqual(self.g.execute(p,self.yes(p))['spent'],2)
 def test_wrong_signer(self):self.assertRaises(InvalidSignature,self.g.execute,self.p,{1:self.k[0].sign(enc(['NO',1,self.p]))},1)
 def test_wrong_role(self):self.assertRaises(InvalidSignature,self.g.execute,self.p,{1:self.yes(self.p)[1]},1)
 def test_outsider(self):self.assertRaises(ValueError,self.g.execute,self.p,self.no(self.p,3),3)
 def test_altered(self):
    p=self.g.propose((0,9,8,7,6,5,4,3,2));self.assertRaises(InvalidSignature,self.g.execute,p,self.no(self.p,0),0)
 def test_duplicate_no(self):
    self.g.execute(self.p,self.no(self.p),1);self.assertRaises(ValueError,self.g.execute,self.p,self.no(self.p),1)
 def test_race(self):
    def go(i):
        try:self.g.execute(self.p,self.yes(self.p) if i==0 else self.no(self.p),None if i==0 else 1);return 1
        except ValueError:return 0
    with concurrent.futures.ThreadPoolExecutor(2) as e:self.assertEqual(sum(e.map(go,range(2))),1)
    s=self.g.head();self.assertEqual(s['seq'],1);self.assertEqual(sum(s['x'])+6,26);self.assertEqual(sum(s['b'])+s['spent'],540)
    with closing(self.g.open()) as c:self.assertEqual(c.execute('SELECT count(*) FROM log').fetchone()[0],1)
if __name__=='__main__':unittest.main(verbosity=2)
