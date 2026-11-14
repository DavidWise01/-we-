import unittest
from hashlib import sha256
from wag048 import AllocationLedger, Witness, generate_allocation, demonstration

S = b'synthetic-demo-seed-48-subjects-2026'
C = sha256(S).hexdigest()
W = [Witness(f'w{i}', f'r{i}', C) for i in range(3)]
COHORT = [f'S{i:02d}' for i in range(48)]

class Tests(unittest.TestCase):
    def setUp(self):
        self.l = AllocationLedger()
    def init(self):
        self.l.precommit(COHORT, 24, C, W, True)
    def allocated(self):
        self.init(); self.l.commit_assignment(generate_allocation(COHORT,24,S))
    def test_01_demo(self):
        l,v=demonstration(); self.assertTrue(l.verify()); self.assertIn('NOT_PROOF',v)
    def test_02_balance(self):
        a=generate_allocation(COHORT,24,S);self.assertEqual(list(a.values()).count('treatment'),24)
    def test_03_reproducible(self):
        self.assertEqual(generate_allocation(COHORT,24,S),generate_allocation(COHORT,24,S))
    def test_04_seed_must_be_bytes(self):
        with self.assertRaises(ValueError):generate_allocation(COHORT,24,'secret')
    def test_05_short_seed(self):
        with self.assertRaises(ValueError):generate_allocation(COHORT,24,b'x')
    def test_06_duplicate_subject(self):
        with self.assertRaises(ValueError):generate_allocation(['a','a'],1,S)
    def test_07_invalid_arm_size(self):
        with self.assertRaises(ValueError):generate_allocation(COHORT,48,S)
    def test_08_precommit(self):
        self.init();self.assertEqual(self.l.precommit_hash,C)
    def test_09_repeated_precommit(self):
        self.init()
        with self.assertRaises(ValueError):self.init()
    def test_10_two_witnesses(self):
        with self.assertRaises(ValueError):self.l.precommit(COHORT,24,C,W[:2],True)
    def test_11_shared_root(self):
        w=[Witness('a','same',C),Witness('b','same',C),Witness('c','other',C)]
        with self.assertRaises(ValueError):self.l.precommit(COHORT,24,C,w,True)
    def test_12_duplicate_name(self):
        w=[Witness('a','r1',C),Witness('a','r2',C),Witness('c','r3',C)]
        with self.assertRaises(ValueError):self.l.precommit(COHORT,24,C,w,True)
    def test_13_wrong_witness_commit(self):
        w=[Witness('a','r1','wrong'),W[1],W[2]]
        with self.assertRaises(ValueError):self.l.precommit(COHORT,24,C,w,True)
    def test_14_concealment_required(self):
        with self.assertRaises(ValueError):self.l.precommit(COHORT,24,C,W,False)
    def test_15_no_assign_before_commit(self):
        with self.assertRaises(ValueError):self.l.commit_assignment(generate_allocation(COHORT,24,S))
    def test_16_bad_arm_counts(self):
        self.init()
        with self.assertRaises(ValueError):self.l.commit_assignment(dict.fromkeys(COHORT,'control'))
    def test_17_commit_assignment(self):
        self.allocated(); self.assertEqual(len(self.l.assigned),48)
    def test_18_no_repeat_assignment(self):
        self.allocated()
        with self.assertRaises(ValueError):self.l.commit_assignment(self.l.assigned)
    def test_19_wrong_seed(self):
        self.allocated()
        with self.assertRaises(ValueError):self.l.reveal(b'another-long-seed-not-the-right-one')
    def test_20_bad_permutation(self):
        self.init();a=generate_allocation(COHORT,24,S);a['S00'],a['S01']='control','treatment'
        if a == generate_allocation(COHORT,24,S):a['S02'],a['S03']='treatment','control'
        # Force a valid but altered assignment by swapping one control and one treatment
        orig=generate_allocation(COHORT,24,S)
        x=next(k for k,v in orig.items() if v=='control'); y=next(k for k,v in orig.items() if v=='treatment')
        orig[x],orig[y]=orig[y],orig[x]
        self.l.commit_assignment(orig)
        with self.assertRaises(ValueError):self.l.reveal(S)
    def test_21_valid_reveal(self):
        self.allocated();self.assertIn('CONSISTENT',self.l.reveal(S))
    def test_22_reveal_twice(self):
        self.allocated();self.l.reveal(S)
        with self.assertRaises(ValueError):self.l.reveal(S)
    def test_23_tamper_detected(self):
        self.allocated();self.l.events[1]['detail']['n_treated']=10;self.assertFalse(self.l.verify())
    def test_24_reject_atomic(self):
        self.init();before=len(self.l.events)
        with self.assertRaises(ValueError):self.l.commit_assignment(dict.fromkeys(COHORT,'control'))
        self.assertEqual(before,len(self.l.events))

if __name__=='__main__':unittest.main()