import unittest
from wag067 import Witness, DomainCutAudit, demo

def shared():
    return DomainCutAudit((Witness('W1','A',('network-x','host-a')),
                           Witness('W2','B',('network-x','host-b')),
                           Witness('W3','C',('network-x','host-c'))))

def separated():
    return DomainCutAudit((Witness('W1','A',('host-a',)),
                           Witness('W2','B',('host-b',)),
                           Witness('W3','C',('host-c',))))

class Tests(unittest.TestCase):
    def setUp(self): self.a=shared()
    def test_demo(self): self.assertTrue(demo()[1]['ledger_valid'])
    def test_four_records(self): self.assertEqual(demo()[1]['records'],4)
    def test_initial(self): self.assertEqual(self.a.state(),'ELIGIBLE_DECLARED_QUORUM')
    def test_three_witness_names(self): self.assertEqual(self.a.names,{'W1','W2','W3'})
    def test_shared_impact(self): self.assertEqual(self.a.impacted({'network-x'}),self.a.names)
    def test_minimal_cut_single(self): self.assertEqual(self.a.minimal_cut_sets(3),[('network-x',),('host-a','host-b','host-c')])
    def test_distinct_hosts(self): self.assertEqual(separated().minimal_cut_sets(3),[('host-a','host-b','host-c')])
    def test_two_objective(self): self.assertIn(('network-x',),self.a.minimal_cut_sets(2))
    def test_individual_host(self): self.assertEqual(self.a.impacted({'host-a'}),{'W1'})
    def test_one_host_quorum_hold(self): self.assertEqual(self.a.state({'host-a'}),'HOLD_COMMON_CAUSE')
    def test_failure(self): self.a.fail('network-x');self.assertEqual(self.a.state(),'HOLD_COMMON_CAUSE')
    def test_all_lost(self): self.a.fail('network-x');self.assertEqual(len(self.a.survivors()),0)
    def test_repair(self): self.a.fail('network-x');self.a.repair('network-x');self.assertEqual(self.a.state(),'ELIGIBLE_DECLARED_QUORUM')
    def test_fresh_required(self):
        self.a.fail('network-x')
        with self.assertRaises(ValueError): self.a.validate_fresh({'W1':'a','W2':'b','W3':'c'})
    def test_fresh_succeeds(self): self.assertEqual(self.a.validate_fresh({'W1':'a','W2':'b','W3':'c'}),'LOCAL_DECLARED_QUORUM')
    def test_fresh_duplicate(self):
        with self.assertRaises(ValueError): self.a.validate_fresh({'W1':'a','W2':'a','W3':'c'})
    def test_fresh_missing(self):
        with self.assertRaises(ValueError): self.a.validate_fresh({'W1':'a','W2':'b'})
    def test_repeat_fail(self):
        self.a.fail('network-x')
        with self.assertRaises(ValueError): self.a.fail('network-x')
    def test_repeat_repair(self):
        with self.assertRaises(ValueError): self.a.repair('network-x')
    def test_unknown_fail(self):
        with self.assertRaises(ValueError): self.a.fail('missing')
    def test_unknown_impact(self):
        with self.assertRaises(ValueError): self.a.impacted({'missing'})
    def test_duplicate_origin(self):
        with self.assertRaises(ValueError): DomainCutAudit((Witness('W1','A',('h1',)),Witness('W2','A',('h2',)),Witness('W3','C',('h3',))))
    def test_duplicate_dependency(self):
        with self.assertRaises(ValueError): DomainCutAudit((Witness('W1','A',('h1','h1')),Witness('W2','B',('h2',)),Witness('W3','C',('h3',))))
    def test_insufficient_witness(self):
        with self.assertRaises(ValueError): DomainCutAudit((Witness('W1','A',('h1',)),))
    def test_invalid_quorum(self):
        with self.assertRaises(ValueError): DomainCutAudit(shared().witnesses,2)
    def test_tampering(self): self.a.fail('network-x');self.a.history[1]['data']['domain']='other';self.assertFalse(self.a.verify())
    def test_atomic_reject(self):
        n=len(self.a.history)
        with self.assertRaises(ValueError): self.a.fail('unknown')
        self.assertEqual(len(self.a.history),n)
    def test_preserve_roots(self): self.a.fail('network-x');self.assertEqual({w.ancestor for w in self.a.witnesses},{'A','B','C'})

if __name__=='__main__':unittest.main()