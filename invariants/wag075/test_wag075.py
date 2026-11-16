"""GitHub reference regression tests for WAG-075.
Full locally tested suite: 58 tests, available as conversation artifact.
"""
import unittest
from wag075 import Witness,ControlSuccession,demo
def base():
    w=[Witness('W1','k1','A','org-x','op1','fd1'),Witness('W2','k2','B','org-y','op2','fd2'),Witness('W3','k3','C','org-z','op3','fd3')]
    return ControlSuccession(w,{'shell-w4':['org-x'],'shell2':['shell-w4'],'proxy-y':['org-y']})
def candidate(**kv):
    d=dict(name='W4',key='k4',root='D',controller='org-w',operator='op4',domain='fd4');d.update(kv);return Witness(**d)
class WAG075Tests(unittest.TestCase):
    def setUp(self):self.g=base()
    def ready(self):
        self.g.propose(candidate());self.g.review('W2');self.g.review('W3');self.g.rotate()
    def test_initial_hold(self):self.assertIn('HOLD',self.g.decide())
    def test_ancestor_closure(self):self.assertIn('org-x',self.g.ancestors('shell2'))
    def test_direct_control_rejected(self):
        with self.assertRaises(ValueError):self.g.propose(candidate(controller='org-x'))
    def test_transitive_control_rejected(self):
        with self.assertRaises(ValueError):self.g.propose(candidate(controller='shell2'))
    def test_shared_survivor_control_rejected(self):
        with self.assertRaises(ValueError):self.g.propose(candidate(controller='proxy-y'))
    def test_reject_preserved(self):
        with self.assertRaises(ValueError):self.g.propose(candidate(controller='shell-w4'))
        self.assertEqual(self.g.ledger[-1]['kind'],'reject')
    def test_reuse_key(self):
        with self.assertRaises(ValueError):self.g.propose(candidate(key='k1'))
    def test_reuse_root(self):
        with self.assertRaises(ValueError):self.g.propose(candidate(root='A'))
    def test_shared_domain(self):
        with self.assertRaises(ValueError):self.g.propose(candidate(domain='fd2'))
    def test_shared_operator(self):
        with self.assertRaises(ValueError):self.g.propose(candidate(operator='op2'))
    def test_unauthorized_review(self):
        self.g.propose(candidate())
        with self.assertRaises(ValueError):self.g.review('W1')
    def test_duplicate_review(self):
        self.g.propose(candidate());self.g.review('W2')
        with self.assertRaises(ValueError):self.g.review('W2')
    def test_one_review_insufficient(self):
        self.g.propose(candidate());self.g.review('W2')
        with self.assertRaises(ValueError):self.g.rotate()
    def test_two_reviews_rotate(self):self.ready();self.assertEqual(set(self.g.witnesses),{'W2','W3','W4'})
    def test_old_reentry_rejected(self):
        self.ready()
        with self.assertRaises(ValueError):self.g.propose(candidate(name='W1',key='k5',root='E'))
    def test_post_rotation_hold(self):self.ready();self.assertIn('HOLD',self.g.decide())
    def test_old_attester_rejected(self):
        self.ready()
        with self.assertRaises(ValueError):self.g.attest('W1','r1',1)
    def test_stale_epoch_rejected(self):
        self.ready()
        with self.assertRaises(ValueError):self.g.attest('W2','r1',0)
    def test_receipt_reuse_rejected(self):
        self.ready();self.g.attest('W2','receipt',1)
        with self.assertRaises(ValueError):self.g.attest('W3','receipt',1)
    def test_fresh_quorum(self):
        self.ready()
        for n in ('W2','W3','W4'):self.g.attest(n,'fresh-'+n,1)
        self.assertEqual(self.g.decide(),'LOCAL_DECLARED_SUCCESSION_ACCEPTED')
    def test_demo_ledger(self):self.assertTrue(demo().verify())
    def test_demo_nine_events(self):self.assertEqual(len(demo().ledger),9)
    def test_tamper_detected(self):
        self.g.propose(candidate());self.g.ledger[1]['data']['candidate']='forged'
        self.assertFalse(self.g.verify())
    def test_cycle_rejected(self):
        with self.assertRaises(ValueError):ControlSuccession(list(base().witnesses.values()),{'org-x':['org-x']})
if __name__=='__main__':unittest.main()
