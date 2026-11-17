import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag098 import Observer,Gate,root,proof,verify,sign_head,sign_gossip

class WAG098Tests(unittest.TestCase):
    def setUp(self):
        self.log=Ed25519PrivateKey.generate()
        self.keys=[Ed25519PrivateKey.generate() for _ in range(3)]
        people=[Observer('W'+str(i+1),'A'+str(i),'O'+str(i),'D'+str(i),k.public_key()) for i,k in enumerate(self.keys)]
        self.g=Gate('REG',98,'NONCE',self.log.public_key(),people)
        self.base=(b'A',b'B',b'C');self.ext=self.base+(b'D',b'E')
        self.old=sign_head(self.log,'REG',98,self.base)
        self.new=sign_head(self.log,'REG',98,self.ext)
        self.p=proof(self.ext,3)
    def put(self,i,head=None,prior=None,consistency=None):
        h=head or self.new
        return self.g.observe('W'+str(i+1),h,sign_gossip(self.keys[i],'W'+str(i+1),h,'NONCE'),prior,consistency)
    def test_honest(self):
        self.put(0,self.old)
        for i in range(3):result=self.put(i,self.new,self.old,self.p)
        self.assertEqual(result,'LOCAL_CROSS_SIZE_AGREEMENT')
    def test_no_proof(self):
        self.put(0,self.old)
        self.assertEqual(self.put(1),'HOLD_UNPROVEN_EXTENSION')
    def test_same_size_fork(self):
        self.put(0,self.old)
        altered=sign_head(self.log,'REG',98,(b'A',b'X',b'C'))
        self.assertEqual(self.put(1,altered),'QUARANTINE_SPLIT_VIEW')
        self.assertEqual(self.g.events[-1][0],'SIGNED_FORK')
    def test_bad_proof_not_fork(self):
        self.put(0,self.old)
        self.assertEqual(self.put(1,self.new,self.old,{'invalid':1}),'HOLD_INVALID_PREFIX_PROOF')
        self.assertEqual(self.g.events[-1][0],'INVALID_PROOF')
    def test_forged_head(self):
        h=dict(self.new);h['sig']=b'0'*64
        with self.assertRaises(ValueError):self.put(0,h)
    def test_nonce(self):
        with self.assertRaises(ValueError):
            self.g.observe('W1',self.new,sign_gossip(self.keys[0],'W1',self.new,'OLD'))
    def test_three(self):
        for i in range(3):s=self.put(i)
        self.assertEqual(s,'LOCAL_CROSS_SIZE_AGREEMENT')
    def test_prefixes(self):
        xs=tuple(str(i).encode() for i in range(1,81))
        for m in range(1,81):self.assertTrue(verify(proof(xs,m),m,root(xs[:m]),80,root(xs)))
    def test_prefix_rewrite(self):
        rewritten=(b'A',b'X',b'C',b'D',b'E')
        self.assertFalse(verify(proof(rewritten,3),3,root(self.base),5,root(rewritten)))
    def test_repeated_observation_not_quorum(self):
        self.put(0);self.put(0);self.put(1)
        self.assertNotEqual(self.g.decision,'LOCAL_CROSS_SIZE_AGREEMENT')
    def test_bad_witness_ancestry(self):
        people=[Observer('W1','A','O1','D1',self.keys[0].public_key()),
                Observer('W2','A','O2','D2',self.keys[1].public_key()),
                Observer('W3','C','O3','D3',self.keys[2].public_key())]
        with self.assertRaises(ValueError):Gate('REG',98,'N',self.log.public_key(),people)
if __name__=='__main__':unittest.main()
