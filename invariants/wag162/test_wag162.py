import unittest,tempfile,concurrent.futures
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from cryptography.exceptions import InvalidSignature
from wag162 import *
class Tests(unittest.TestCase):
    def setUp(self):
        d=tempfile.TemporaryDirectory();self.addCleanup(d.cleanup);self.db=Path(d.name)/'db';self.k=[K.generate() for _ in range(10)];self.pub=[k.public_key() for k in self.k];self.g=Gate(self.db,self.pub,'mesh162');self.a=self.g.admit('a',[0,1,2]);self.b=self.g.admit('b',[3,4,5]);self.s=self.g.head()
    def yes(self,p):return {i:self.k[i].sign(enc(['YES',i,p])) for i in p[3]}
    def no(self,p,i):return {i:self.k[i].sign(enc(['NO',i,p]))}
    def test_disjoint(self):
        self.g.close(self.a,self.yes(self.a));t=self.g.close(self.b,self.yes(self.b));self.assertEqual(t['x'],[2]*10);self.assertEqual(t['spent'],4);self.assertEqual(t['v'],[1]*6+[0]*4)
    def test_reverse(self):
        self.g.close(self.b,self.yes(self.b));t=self.g.close(self.a,self.yes(self.a));self.assertEqual(t['x'],[2]*10);self.assertEqual(t['spent'],4)
    def test_overlap(self):
        p=self.g.admit('c',[0,1,2]);self.g.close(self.a,self.yes(self.a));self.assertRaises(ValueError,self.g.close,p,self.yes(p))
    def test_withdraw(self):
        self.assertEqual(self.g.close(self.a,self.no(self.a,1),1),self.s);self.g.close(self.b,self.yes(self.b));self.assertRaises(ValueError,self.g.close,self.a,self.yes(self.a))
    def test_restart(self):
        self.g.close(self.a,self.yes(self.a));g=Gate(self.db,self.pub,'mesh162');self.assertEqual(g.close(self.b,self.yes(self.b))['spent'],4)
    def test_signature_scope(self):
        p=self.g.admit('c',[0,1,2]);self.assertRaises(InvalidSignature,self.g.close,p,self.yes(self.a))
    def test_concurrent_disjoint(self):
        with concurrent.futures.ThreadPoolExecutor(2) as e:list(e.map(lambda p:self.g.close(p,self.yes(p)),[self.a,self.b]))
        self.assertEqual(self.g.head()['x'],[2]*10)
    def test_concurrent_overlap(self):
        p=self.g.admit('c',[0,1,2])
        def go(q):
            try:self.g.close(q,self.yes(q));return 1
            except ValueError:return 0
        with concurrent.futures.ThreadPoolExecutor(2) as e:self.assertEqual(sum(e.map(go,[self.a,p])),1)
    def test_journal(self):
        self.g.close(self.a,self.yes(self.a));t=self.g.close(self.b,self.yes(self.b))
        with closing(self.g.open()) as c:r=[json.loads(a[0]) for a in c.execute('SELECT body FROM log ORDER BY seq')]
        self.assertEqual([a[0] for a in r],['ADMIT','ADMIT','COMMIT','COMMIT']);self.assertEqual(r[2][3],r[3][2]);self.assertEqual(r[3][3],digest(t))
    def test_failure_unchanged(self):
        a=self.yes(self.a);del a[1];self.assertRaises(ValueError,self.g.close,self.a,a);self.assertEqual(self.g.head(),self.s)
if __name__=='__main__':unittest.main(verbosity=2)
