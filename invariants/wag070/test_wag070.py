import unittest
from wag070 import Witness,EpochGate,demo

def gate():
    return EpochGate([Witness('W1','A','oa','da'),Witness('W2','B','ob','db'),Witness('W3','C','oc','dc')],
        {'W1':{'power','net','ra'},'W2':{'power','net','rb'},'W3':{'independent','rc'}})

class WAG070Tests(unittest.TestCase):
    def setUp(self):self.g=gate()
    def verified(self):return self.g.verify_infrastructure()
    def attest_all(self,e,h):
        for n in ('W1','W2','W3'):self.g.attest(n,'receipt-'+n,e,h)
    def test_01_three_available(self):self.assertEqual(self.g.available(),self.g.names)
    def test_02_genesis(self):self.assertEqual(len(self.g.history),1)
    def test_03_audit(self):self.assertTrue(self.g.audit_valid())
    def test_04_initial_epoch(self):self.assertEqual(self.g.epoch,0)
    def test_05_initial_verify(self):self.assertEqual(self.verified()[0],0)
    def test_06_attestation(self):
        e,h=self.verified();self.g.attest('W1','r1',e,h);self.assertEqual(self.g.receipts['W1'],'r1')
    def test_07_certificate(self):
        e,h=self.verified();self.attest_all(e,h);self.assertEqual(self.g.certify(e,h),'LOCAL_EPOCH_BOUND_CERTIFICATE')
    def test_08_no_verify(self):
        with self.assertRaises(ValueError):self.g.attest('W1','r1',0,self.g.snapshot())
    def test_09_no_certify(self):
        with self.assertRaises(ValueError):self.g.certify(0,self.g.snapshot())
    def test_10_partial_certificate(self):
        e,h=self.verified();self.g.attest('W1','r1',e,h)
        with self.assertRaises(ValueError):self.g.certify(e,h)
    def test_11_cut(self):self.g.transition('power',False);self.assertEqual(self.g.available(),{'W3'})
    def test_12_epoch_increments(self):self.g.transition('power',False);self.assertEqual(self.g.epoch,1)
    def test_13_snapshot_changes(self):
        s=self.g.snapshot();self.g.transition('power',False);self.assertNotEqual(s,self.g.snapshot())
    def test_14_verify_rejects_outage(self):
        self.g.transition('power',False)
        with self.assertRaises(ValueError):self.g.verify_infrastructure()
    def test_15_old_receipts_cleared(self):
        e,h=self.verified();self.g.attest('W1','a',e,h);self.g.transition('power',False);self.assertEqual(self.g.receipts,{})
    def test_16_old_verification_cleared(self):
        self.verified();self.g.transition('power',False);self.assertIsNone(self.g.verified)
    def test_17_repair_does_not_verify(self):
        self.g.transition('power',False);self.g.transition('power',True);self.assertIsNone(self.g.verified)
    def test_18_repair_epoch_two(self):
        self.g.transition('power',False);self.g.transition('power',True);self.assertEqual(self.g.epoch,2)
    def test_19_old_attestation_rejected(self):
        e,h=self.verified();self.g.transition('power',False);self.g.transition('power',True)
        with self.assertRaises(ValueError):self.g.attest('W1','old',e,h)
    def test_20_old_certificate_rejected(self):
        e,h=self.verified();self.attest_all(e,h);self.g.certify(e,h)
        self.g.transition('power',False);self.g.transition('power',True)
        with self.assertRaises(ValueError):self.g.certify(e,h)
    def test_21_new_attestation(self):
        self.g.transition('power',False);self.g.transition('power',True)
        e,h=self.verified();self.attest_all(e,h);self.assertEqual(self.g.certify(e,h),'LOCAL_EPOCH_BOUND_CERTIFICATE')
    def test_22_replay_witness(self):
        e,h=self.verified();self.g.attest('W1','r1',e,h)
        with self.assertRaises(ValueError):self.g.attest('W1','r2',e,h)
    def test_23_duplicate_receipt(self):
        e,h=self.verified();self.g.attest('W1','r1',e,h)
        with self.assertRaises(ValueError):self.g.attest('W2','r1',e,h)
    def test_24_wrong_epoch(self):
        e,h=self.verified()
        with self.assertRaises(ValueError):self.g.attest('W1','r',e+1,h)
    def test_25_wrong_hash(self):
        e,h=self.verified()
        with self.assertRaises(ValueError):self.g.attest('W1','r',e,'bad')
    def test_26_unknown_witness(self):
        e,h=self.verified()
        with self.assertRaises(ValueError):self.g.attest('W4','r',e,h)
    def test_27_empty_receipt(self):
        e,h=self.verified()
        with self.assertRaises(ValueError):self.g.attest('W1','',e,h)
    def test_28_unknown_domain(self):
        with self.assertRaises(ValueError):self.g.transition('unknown',False)
    def test_29_duplicate_transition(self):
        with self.assertRaises(ValueError):self.g.transition('power',True)
    def test_30_invalid_boolean(self):
        with self.assertRaises(ValueError):self.g.transition('power',0)
    def test_31_atomic_bad_transition(self):
        before=len(self.g.history)
        with self.assertRaises(ValueError):self.g.transition('bad',False)
        self.assertEqual(before,len(self.g.history))
    def test_32_distinct_ancestor(self):
        with self.assertRaises(ValueError):EpochGate([Witness('W1','A','oa','da'),Witness('W2','A','ob','db'),Witness('W3','C','oc','dc')],self.g.deps)
    def test_33_distinct_operator(self):
        with self.assertRaises(ValueError):EpochGate([Witness('W1','A','oa','da'),Witness('W2','B','oa','db'),Witness('W3','C','oc','dc')],self.g.deps)
    def test_34_distinct_failure_domain(self):
        with self.assertRaises(ValueError):EpochGate([Witness('W1','A','oa','da'),Witness('W2','B','ob','da'),Witness('W3','C','oc','dc')],self.g.deps)
    def test_35_empty_dependency(self):
        with self.assertRaises(ValueError):EpochGate(self.g.witnesses,{'W1':[],'W2':['a'],'W3':['b']})
    def test_36_missing_witness_dependency(self):
        with self.assertRaises(ValueError):EpochGate(self.g.witnesses,{'W1':['a'],'W2':['b']})
    def test_37_tampered_ledger(self):
        self.g.transition('power',False);self.g.history[1]['payload']['domain']='fake';self.assertFalse(self.g.audit_valid())
    def test_38_demo(self):self.assertTrue(demo()[1]['audit_ok'])
    def test_39_demo_stale(self):self.assertTrue(demo()[1]['old_rejected'])
    def test_40_demo_epochs(self):self.assertEqual((demo()[1]['old_epoch'],demo()[1]['new_epoch']),(0,2))
    def test_41_demo_events(self):self.assertEqual(demo()[1]['events'],13)
    def test_42_reverify_same_epoch_changes_no_head(self):self.assertEqual(self.verified(),self.verified())
    def test_43_two_domain_independence(self):
        self.g.transition('independent',False);self.assertEqual(self.g.available(),{'W1','W2'})
    def test_44_old_genesis_immutable_after_recovery(self):
        first=self.g.history[0]['hash'];self.g.transition('power',False);self.g.transition('power',True);self.assertEqual(first,self.g.history[0]['hash'])
    def test_45_replay_receipt_across_epochs(self):
        e,h=self.verified();self.g.attest('W1','r1',e,h);self.g.transition('power',False);self.g.transition('power',True)
        e,h=self.verified()
        with self.assertRaises(ValueError):self.g.attest('W1','r1',e,h)
if __name__=='__main__':unittest.main()
