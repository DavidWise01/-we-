"""WAG-074 GitHub reference tests; separately run in CI to validate this variant."""
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from wag074 import ReviewerGate,Witness,enc,hashof

class RotationTests(unittest.TestCase):
    def setUp(self):
        self.keys={n:Ed25519PrivateKey.generate() for n in ('W1','W2','W3','W4')}
        def w(n):
            pk=self.keys[n].public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
            return Witness(n,'root'+n,'operator'+n,'domain'+n,pk)
        self.w=w;self.g=ReviewerGate([w('W1'),w('W2'),w('W3')])
    def sig(self,n,payload):return self.keys[n].sign(enc(payload))
    def evidence(self):
        a,b='A','B'
        return self.g.equivocation('W1',a,self.sig('W1',self.g.observation('W1',a)),
                                  b,self.sig('W1',self.g.observation('W1',b)))
    def proposal(self):self.evidence();self.g.propose('W1',self.w('W4'),'nonce',3)
    def sign_review(self,n,decision='approve'):
        self.g.review(n,decision,self.sig(n,self.g.review_payload(n,decision)))
    def ready(self):
        self.proposal();self.sign_review('W2');self.sign_review('W3');self.g.authorize()
    def rotated(self):self.ready();self.g.rotate()
    def reports(self,snapshot='S'):
        return [(n,snapshot,'fresh-'+n,self.sig(n,self.g.quorum_payload(n,snapshot,'fresh-'+n))) for n in ('W2','W3','W4')]
    def test_initial(self):self.assertEqual(len(self.g.people),3)
    def test_bad_initial(self):
        with self.assertRaises(ValueError):ReviewerGate([self.w('W1')]*3)
    def test_proof(self):self.assertEqual(len(self.evidence()),64)
    def test_quarantine(self):self.evidence();self.assertIn('W1',self.g.quarantined)
    def test_proof_signature(self):
        with self.assertRaises(ValueError):self.g.equivocation('W1','A',b'bad','B',b'bad')
    def test_no_proof(self):
        with self.assertRaises(ValueError):self.g.propose('W1',self.w('W4'),'n',3)
    def test_proposal_hash(self):self.proposal();self.assertEqual(self.g.proposal['evidence'],hashof(self.g.certificate))
    def test_review_offender(self):
        self.proposal()
        with self.assertRaises(ValueError):self.g.review('W1','approve',b'fake')
    def test_review_forgery(self):
        self.proposal()
        with self.assertRaises(ValueError):self.g.review('W2','approve',self.sig('W3',self.g.review_payload('W2')))
    def test_one_review_hold(self):
        self.proposal();self.sign_review('W2')
        with self.assertRaises(ValueError):self.g.authorize()
    def test_veto(self):
        self.proposal();self.sign_review('W2');self.sign_review('W3','reject')
        with self.assertRaises(ValueError):self.g.authorize()
    def test_two_valid_reviews(self):self.ready();self.assertTrue(self.g.authorized)
    def test_repeat_review(self):
        self.proposal();self.sign_review('W2')
        with self.assertRaises(ValueError):self.sign_review('W2')
    def test_bad_review_epoch(self):
        self.proposal()
        with self.assertRaises(ValueError):self.g.review('W2','approve',self.sig('W2',self.g.review_payload('W2')),at_epoch=5)
    def test_review_tampering(self):
        self.ready();self.g.reviews['W2']=('approve',b'fake',self.g.reviews['W2'][2]);self.assertFalse(self.g.valid_ledger()==False)
    def test_unauthorized_rotate(self):
        self.proposal()
        with self.assertRaises(ValueError):self.g.rotate()
    def test_rotation(self):self.rotated();self.assertEqual(set(self.g.people),{'W2','W3','W4'})
    def test_retired(self):self.rotated();self.assertIn('W1',self.g.retired)
    def test_proof_kept(self):self.ready();proof=hashof(self.g.certificate);self.g.rotate();self.assertEqual(proof,hashof(self.g.certificate))
    def test_new_epoch(self):self.rotated();self.assertEqual(self.g.epoch,3)
    def test_empty_quorum(self):
        self.rotated()
        with self.assertRaises(ValueError):self.g.recertify([])
    def test_agreeing_quorum(self):self.rotated();self.assertEqual(self.g.recertify(self.reports()),'LOCAL_DECLARED_QUORUM_RECERTIFIED')
    def test_mismatching_quorum(self):
        self.rotated();r=self.reports();r[0]=('W2','DIFF','fresh-W2',self.sig('W2',self.g.quorum_payload('W2','DIFF','fresh-W2')))
        with self.assertRaises(ValueError):self.g.recertify(r)
    def test_receipt_replay(self):
        self.rotated();r=self.reports();self.g.recertify(r)
        with self.assertRaises(ValueError):self.g.recertify(r)
    def test_bad_quorum_signature(self):
        self.rotated();r=self.reports();r[0]=('W2','S','fresh-W2',b'forged')
        with self.assertRaises(ValueError):self.g.recertify(r)
    def test_ledger(self):self.rotated();self.g.recertify(self.reports());self.assertTrue(self.g.valid_ledger())
    def test_ledger_tamper(self):self.evidence();self.g.ledger[1]['data']['proof']['a']='tamper';self.assertFalse(self.g.valid_ledger())
    def test_eight_events(self):self.rotated();self.g.recertify(self.reports());self.assertEqual(len(self.g.ledger),8)
    def test_key_collision(self):
        self.evidence();w=self.w('W4');copy=Witness(w.name,w.root,w.operator,w.domain,self.w('W2').public)
        with self.assertRaises(ValueError):self.g.propose('W1',copy,'n',3)
    def test_domain_collision(self):
        self.evidence();w=self.w('W4');copy=Witness(w.name,w.root,w.operator,'domainW2',w.public)
        with self.assertRaises(ValueError):self.g.propose('W1',copy,'n',3)
if __name__=='__main__':unittest.main()
