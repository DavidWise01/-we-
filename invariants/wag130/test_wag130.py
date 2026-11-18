import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from wag130 import *

def replay(events):
    q=156
    for i,e in enumerate(events):
        if e['seq']!=i+1 or e['q']!=156:raise ValueError('history')
        q=e['q']
    return {'g':len(events),'q':q}
class Tests(unittest.TestCase):
    def setUp(self):
        self.ks={n:K.generate() for n in 'HON'};self.keys={n:k.public_key() for n,k in self.ks.items()};self.e=[{'seq':i,'q':156,'op':'graduate'} for i in range(1,4)];self.b=issue('mesh',self.e,self.ks,replay)
    def check(self,e,b=None):return check('mesh',e,self.keys,self.b if b is None else b,replay)
    def test_complete(self):self.assertEqual(self.check(self.e),'COMPLETE_THROUGH_BOUND')
    def test_truncated(self):self.assertEqual(self.check(self.e[:-1]),'HOLD_TRUNCATED')
    def test_extension(self):self.assertEqual(self.check(self.e+[{'seq':4,'q':156,'op':'graduate'}]),'COMPLETE_THROUGH_BOUND')
    def test_fork(self):self.e[0]['op']='other';self.assertEqual(self.check(self.e),'HOLD_FORK')
    def test_bad_history(self):self.e[0]['q']=157;self.assertEqual(self.check(self.e),'HOLD_INVALID_HISTORY')
    def test_missing(self):self.assertEqual(check('mesh',self.e,self.keys,None,replay),'HOLD_MISSING')
    def test_tampered(self):self.b[0][2]=2;self.assertEqual(self.check(self.e),'HOLD_INVALID_BOUND')
    def test_scope(self):self.assertEqual(check('other',self.e,self.keys,self.b,replay),'HOLD_INVALID_BOUND')
    def test_shared_key(self):self.keys['O']=self.keys['H'];self.assertEqual(self.check(self.e),'HOLD_INVALID_BOUND')
    def test_missing_vote(self):del self.b[1]['N'];self.assertEqual(self.check(self.e),'HOLD_INVALID_BOUND')
    def test_old_bound_limit(self):old=issue('mesh',self.e[:1],self.ks,replay);self.assertEqual(self.check(self.e[:1],old),'COMPLETE_THROUGH_BOUND')
if __name__=='__main__':unittest.main(verbosity=2)
