import unittest,tempfile,concurrent.futures
from pathlib import Path
from wag161 import *
from cryptography.exceptions import InvalidSignature
class Tests(unittest.TestCase):
 def setUp(self):
    t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.db=Path(t.name)/'db';self.k=[Ed25519PrivateKey.generate() for _ in range(10)];self.pub=[k.public_key() for k in self.k];self.g=Gate(self.db,self.pub,'test-mesh');self.a=self.g.admit('a',[0,1,2]);self.b=self.g.admit('b',[0,9,8,7,6,5,4,3,2]);self.s=self.g.head()
 def yes(self,p):return {i:self.k[i].sign(enc(['YES',i,p])) for i in p[4]}
 def no(self,p,i=0):return {i:self.k[i].sign(enc(['NO',i,p]))}
 def test_sibling(self):
    a=self.g.close(self.a,self.no(self.a),0);self.assertEqual(a,self.s);self.assertEqual(self.g.close(self.b,self.yes(self.b))['spent'],8)
 def test_spend(self):
    self.g.close(self.a,self.yes(self.a));self.assertRaises(ValueError,self.g.close,self.b,self.yes(self.b))
 def test_replay(self):
    self.g.close(self.a,self.no(self.a),0);self.assertRaises(ValueError,self.g.close,self.a,self.no(self.a),0)
 def test_signature_scope(self):
    p=self.g.admit('c',[0,1,2]);self.assertRaises(InvalidSignature,self.g.close,p,self.yes(self.a))
 def test_restart(self):
    self.g.close(self.a,self.no(self.a),0);g=Gate(self.db,self.pub,'test-mesh');self.assertRaises(ValueError,g.close,self.a,self.yes(self.a));self.assertEqual(g.close(self.b,self.yes(self.b))['spent'],8)
 def test_race(self):
    def go(p):
     try:self.g.close(p,self.yes(p));return 1
     except ValueError:return 0
    with concurrent.futures.ThreadPoolExecutor(2) as e:self.assertEqual(sum(e.map(go,[self.a,self.b])),1)
 def test_duplicate_admission(self):self.assertRaises(sqlite3.IntegrityError,self.g.admit,'a',[0,1,2])
 def test_no_outsider(self):self.assertRaises(ValueError,self.g.close,self.a,self.no(self.a,3),3)
 def test_log(self):
    self.g.close(self.a,self.no(self.a),0);self.g.close(self.b,self.yes(self.b))
    with closing(self.g.open()) as c:self.assertEqual([json.loads(r[0])[0] for r in c.execute('SELECT body FROM log ORDER BY seq')],['ADMIT','ADMIT','WITHDRAW','COMMIT'])
if __name__=='__main__':unittest.main(verbosity=2)
