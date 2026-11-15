"""GitHub-reference smoke and adversarial tests for WAG-073.

The 52-test full locally executed suite is the separate conversation artifact.
This reference suite has not been executed in GitHub Actions.
"""
import unittest
from wag073 import Gate,fresh,payload,signed,valid,demo

def fixture():
    w1,k1=fresh('W1','A','opA','fdA')
    w2,k2=fresh('W2','B','opB','fdB')
    w3,k3=fresh('W3','C','opC','fdC')
    w4,k4=fresh('W4','D','opD','fdD')
    gate=Gate([w1,w2,w3],2,'nonce','A')
    a=payload('W1',2,'nonce','A')
    b=payload('W1',2,'nonce','B')
    return gate,((w1,k1),(w2,k2),(w3,k3),(w4,k4)),(a,b)

def quarantine():
    g,people,(a,b)=fixture()
    g.equivocation('W1',a,signed(people[0][1],a),b,signed(people[0][1],b))
    return g,people

def reviewed():
    g,people=quarantine();g.authorize_review(*people[1]);return g,people

def rotated():
    g,people=reviewed();g.rotate('W1',people[3][0]);return g,people

def receipts(g,people):
    return {w.name:(payload(w.name,g.epoch,g.challenge,g.snapshot),signed(k,payload(w.name,g.epoch,g.challenge,g.snapshot))) for w,k in people[1:]}

class WAG073Tests(unittest.TestCase):
    def test_demo(self):
        r=demo();self.assertTrue(r['verified']);self.assertEqual(r['events'],5)
    def test_three_members(self):
        self.assertEqual(set(fixture()[0].active),{'W1','W2','W3'})
    def test_proof_hold(self):
        g,p=quarantine();self.assertEqual(g.status(),'HOLD_EQUIVOCATION')
    def test_conflicting_signatures_preserved(self):
        g,p=quarantine();self.assertNotEqual(g.cert['a']['snapshot'],g.cert['b']['snapshot'])
    def test_wrong_signature(self):
        g,p,(a,b)=fixture()
        with self.assertRaises(ValueError):g.equivocation('W1',a,signed(p[1][1],a),b,signed(p[0][1],b))
    def test_different_challenge(self):
        g,p,(a,b)=fixture();c=payload('W1',2,'other','B')
        with self.assertRaises(ValueError):g.equivocation('W1',a,signed(p[0][1],a),c,signed(p[0][1],c))
    def test_no_review_before_proof(self):
        g,p,_=fixture()
        with self.assertRaises(ValueError):g.authorize_review(*p[1])
    def test_quarantined_reviewer(self):
        g,p=quarantine()
        with self.assertRaises(ValueError):g.authorize_review(*p[0])
    def test_no_rotation_before_review(self):
        g,p=quarantine()
        with self.assertRaises(ValueError):g.rotate('W1',p[3][0])
    def test_retired_kept(self):
        g,p=rotated();self.assertIn('W1',g.retired);self.assertIn('W1',g.quarantine)
    def test_new_ancestry(self):
        g,p=rotated();self.assertEqual({w.ancestor for w in g.active.values()},{'B','C','D'})
    def test_no_ancestor_reuse(self):
        g,p=reviewed();w,k=fresh('W4','A','opD','fdD')
        with self.assertRaises(ValueError):g.rotate('W1',w)
    def test_new_challenge(self):
        g,p=rotated();self.assertNotEqual(g.challenge,'nonce')
    def test_no_cert_before_rotate(self):
        g,p=quarantine()
        with self.assertRaises(ValueError):g.certify({})
    def test_missing_reciepts(self):
        g,p=rotated()
        with self.assertRaises(ValueError):g.certify({})
    def test_fresh_attestations(self):
        g,p=rotated();self.assertEqual(g.certify(receipts(g,p)),'LOCAL_SIGNED_QUORUM_RECONSTITUTED')
    def test_old_epoch_replay(self):
        g,p=rotated();r=receipts(g,p);w,k=p[1];old=payload('W2',2,'nonce','A');r['W2']=(old,signed(k,old))
        with self.assertRaises(ValueError):g.certify(r)
    def test_duplicate_cert(self):
        g,p=rotated();r=receipts(g,p);g.certify(r)
        with self.assertRaises(ValueError):g.certify(r)
    def test_ledger_tamper(self):
        g,p=quarantine();g.events[1]['data']['a']['snapshot']='forged';self.assertFalse(g.verify())
    def test_rejected_call_atomic(self):
        g,p=rotated();n=len(g.events)
        with self.assertRaises(ValueError):g.certify({})
        self.assertEqual(n,len(g.events))

if __name__=='__main__':unittest.main()
