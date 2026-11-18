import unittest,copy
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from wag133 import *
class Tests(unittest.TestCase):
 def setUp(self):
    self.a=K.generate();self.ks={n:K.generate() for n in 'HON'};self.keys={n:k.public_key() for n,k in self.ks.items()};self.graph={'H':['A'],'O':['B'],'N':['C'],'A':[],'B':[],'C':[]};self.m=manifest('mesh',1,self.graph,self.keys,self.a)
 def gate(self,m=None):
    m=m or self.m;return Gate('mesh',self.a.public_key(),self.keys,{'A','B','C'},m[0][2],digest(m[0]))
 def answers(self,g,m=None,head='G1'):
    return {n:response('mesh',g.nonce,digest((m or self.m)[0]),head,n,k) for n,k in self.ks.items()}
 def test_valid(self):g=self.gate();self.assertEqual(g.verify(self.m,self.answers(g),'G1'),'VERIFIED_DECLARED_TOPOLOGY')
 def test_tamper(self):g=self.gate();m=copy.deepcopy(self.m);m[0][3]['O']=['A'];self.assertEqual(g.verify(m,self.answers(g),'G1'),'HOLD_INVALID')
 def test_stale(self):m=manifest('mesh',2,self.graph,self.keys,self.a);g=self.gate(m);self.assertEqual(g.verify(self.m,self.answers(g),'G1'),'HOLD_STALE_TOPOLOGY')
 def test_shared(self):self.graph['O']=['A'];m=manifest('mesh',2,self.graph,self.keys,self.a);g=self.gate(m);self.assertEqual(g.verify(m,self.answers(g,m),'G1'),'HOLD_SHARED_ROOT')
 def test_missing_ancestry(self):del self.graph['A'];m=manifest('mesh',2,self.graph,self.keys,self.a);g=self.gate(m);self.assertEqual(g.verify(m,self.answers(g,m),'G1'),'HOLD_INVALID')
 def test_replay(self):g=self.gate();self.assertEqual(g.verify(self.m,self.answers(self.gate()),'G1'),'HOLD_RESPONSE_SCOPE')
 def test_old_response(self):m=manifest('mesh',2,self.graph,self.keys,self.a);g=self.gate(m);self.assertEqual(g.verify(m,self.answers(g),'G1'),'HOLD_RESPONSE_SCOPE')
 def test_missing_vote(self):g=self.gate();a=self.answers(g);del a['H'];self.assertEqual(g.verify(self.m,a,'G1'),'HOLD_MISSING')
 def test_head(self):g=self.gate();self.assertEqual(g.verify(self.m,self.answers(g),'G2'),'HOLD_RESPONSE_SCOPE')
 def test_used(self):g=self.gate();a=self.answers(g);g.verify(self.m,a,'G1');self.assertEqual(g.verify(self.m,a,'G1'),'HOLD_USED')
 def test_hidden_root_limit(self):g=self.gate();actual={'A':'X','B':'X','C':'Y'};self.assertEqual(actual['A'],actual['B']);self.assertEqual(g.verify(self.m,self.answers(g),'G1'),'VERIFIED_DECLARED_TOPOLOGY')
if __name__=='__main__':unittest.main(verbosity=2)
