import unittest
from dataclasses import replace
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag061 import QuorumGate, make_witness, make_anchor, demo

class Tests(unittest.TestCase):
    def setUp(self):
        self.g=QuorumGate(['a','b','c'])
        self.g.reconnect(['a','b','c','d'])
    def witness(self,i,**changes):
        w=make_witness(Ed25519PrivateKey.generate(),f'W{i}',f'root{i}',
                       f'op{i}',f'd{i}',self.g.head_digest,12)
        return replace(w,**changes)
    def add_three(self):
        for i in range(3):self.g.witness(self.witness(i))
    def anchor(self,**changes):
        a=make_anchor(Ed25519PrivateKey.generate(),'A','independent-op',
                      'independent-domain',self.g.head_digest,12)
        return replace(a,**changes)
    def test_demo(self):
        g,v=demo()
        self.assertEqual(v,'RECERTIFIED_LOCAL_ANCHOR')
        self.assertTrue(g.verify_chain())
    def test_demo_events(self):self.assertEqual(len(demo()[0].events),8)
    def test_valid_extension(self):self.assertEqual(self.g.status,'PENDING_QUORUM')
    def test_rollback(self):
        g=QuorumGate(['a','b','c'])
        self.assertEqual(g.reconnect(['a','b']),'HOLD_ROLLBACK')
    def test_fork(self):
        g=QuorumGate(['a','b','c'])
        self.assertEqual(g.reconnect(['a','x','c','d']),'QUARANTINE_FORK')
    def test_equal(self):
        g=QuorumGate(['a','b','c'])
        self.assertEqual(g.reconnect(['a','b','c']),'HOLD_NO_ADVANCE')
    def test_reconnect_twice(self):
        with self.assertRaises(ValueError):self.g.reconnect(['a','b','c','d','e'])
    def test_witness(self):
        self.g.witness(self.witness(0))
        self.assertEqual(len(self.g.witnesses),1)
    def test_witness_bad_signature(self):
        with self.assertRaises(ValueError):self.g.witness(self.witness(0,signature='00'*64))
    def test_witness_bad_head(self):
        with self.assertRaises(ValueError):self.g.witness(self.witness(0,head_digest='0'*64))
    def test_shared_origin(self):
        self.g.witness(self.witness(0))
        with self.assertRaises(ValueError):self.g.witness(self.witness(1,ancestry='root0'))
    def test_shared_operator(self):
        self.g.witness(self.witness(0))
        with self.assertRaises(ValueError):self.g.witness(self.witness(1,operator='op0'))
    def test_shared_failure(self):
        self.g.witness(self.witness(0))
        with self.assertRaises(ValueError):self.g.witness(self.witness(1,failure_domain='d0'))
    def test_repeat_witness(self):
        self.g.witness(self.witness(0))
        with self.assertRaises(ValueError):self.g.witness(self.witness(0))
    def test_incomplete(self):self.assertEqual(self.g.certify(13),'HOLD_INCOMPLETE')
    def test_no_anchor(self):
        self.add_three()
        self.assertEqual(self.g.certify(13),'HOLD_INCOMPLETE')
    def test_two_witness(self):
        for i in range(2):self.g.witness(self.witness(i))
        self.g.anchor(self.anchor())
        self.assertEqual(self.g.certify(13),'HOLD_INCOMPLETE')
    def test_anchor(self):
        self.g.anchor(self.anchor())
        self.assertIsNotNone(self.g.anchor_receipt)
    def test_bad_anchor_signature(self):
        with self.assertRaises(ValueError):self.g.anchor(self.anchor(signature='00'*64))
    def test_shared_anchor_domain(self):
        self.g.witness(self.witness(0))
        with self.assertRaises(ValueError):self.g.anchor(self.anchor(operator='op0'))
    def test_duplicate_anchor(self):
        self.g.anchor(self.anchor())
        with self.assertRaises(ValueError):self.g.anchor(self.anchor())
    def test_stale(self):
        self.add_three()
        self.g.anchor(self.anchor())
        self.assertEqual(self.g.certify(20),'HOLD_STALE')
    def test_failed_atomic(self):
        n=len(self.g.events)
        with self.assertRaises(ValueError):self.g.witness(self.witness(0,signature='00'*64))
        self.assertEqual(len(self.g.events),n)
    def test_tamper(self):
        self.g.events[1]['data']['size']=999
        self.assertFalse(self.g.verify_chain())

if __name__=='__main__':unittest.main()
