import unittest,tempfile,copy,sqlite3
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from cryptography.exceptions import InvalidSignature
from wag134 import *
class Tests(unittest.TestCase):
 def setUp(self):
    t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.path=Path(t.name)/'registry';self.a={n:K.generate() for n in 'HON'};self.b={**self.a,'N':K.generate()};self.old=self.man(0,self.a);self.new=self.man(1,self.b);self.r=Registry(self.path,self.old)
 def man(self,g,ks):return {'mesh':'mesh','generation':g,'keys':{n:raw(k.public_key()) for n,k in ks.items()},'roots':{n:[n+'-root'] for n in ks}}
 def sign(self,ks,body):return {n:k.sign(enc(body)).hex() for n,k in ks.items()}
 def cert(self,o,n,a,b):return self.sign(a,statement(o,n,'approve')),self.sign(b,statement(o,n,'accept'))
 def advance(self):self.r.advance(self.new,*self.cert(self.old,self.new,self.a,self.b))
 def test_success(self):self.advance();self.assertEqual(self.r.head(),self.new)
 def test_restart(self):self.advance();self.assertEqual(Registry(self.path,self.old).head(),self.new)
 def test_missing_old(self):a,b=self.cert(self.old,self.new,self.a,self.b);del a['N'];self.assertRaises(ValueError,self.r.advance,self.new,a,b)
 def test_missing_new(self):a,b=self.cert(self.old,self.new,self.a,self.b);del b['N'];self.assertRaises(ValueError,self.r.advance,self.new,a,b)
 def test_replay(self):self.advance();self.assertRaises(ValueError,self.advance)
 def test_shared_root(self):self.new['roots']['N']=self.new['roots']['H'];self.assertRaises(ValueError,self.advance)
 def test_tamper(self):a,b=self.cert(self.old,self.new,self.a,self.b);self.new['roots']['N']=['other'];self.assertRaises(InvalidSignature,self.r.advance,self.new,a,b)
 def test_retired_observation(self):self.advance();body=['WAG134-observe','mesh',digest(self.old),'checkpoint'];self.assertRaises(ValueError,self.r.authorize,body,self.sign(self.a,body))
 def test_new_observation(self):self.advance();body=['WAG134-observe','mesh',digest(self.new),'checkpoint'];self.assertEqual(self.r.authorize(body,self.sign(self.b,body)),'CURRENT_MEMBERSHIP_SIGNATURES')
 def test_retired_reentry(self):self.advance();n=self.man(2,self.a);self.assertRaises(ValueError,self.r.advance,n,*self.cert(self.new,n,self.b,self.a))
 def test_tampered_history(self):
    self.advance();n=copy.deepcopy(self.new);n["roots"]["N"]=["other"]
    with sqlite3.connect(self.path) as c:c.execute("UPDATE lineage SET manifest=? WHERE g=1",(enc(n).decode(),))
    self.assertRaises(InvalidSignature,self.r.head)
 def test_wrong_mesh(self):self.new['mesh']='other';self.assertRaises(ValueError,self.advance)
if __name__=='__main__':unittest.main(verbosity=2)
