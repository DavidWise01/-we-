import unittest
from fractions import Fraction
from math import comb
from wag088 import (miss_probability, look_budget, FamilyBudget, Auditor,
                    challenge_positions, demo)

SEED=b'WAG088_TEST_SEED_DO_NOT_USE_LIVE!'
def make(n=17,m=3,k=3,a=Fraction(1,20),name='a'):
    return Auditor(name,n,m,k,FamilyBudget(),a,SEED)
def submit(a,found=False):
    return a.submit(*a.challenge(),found)

class TestWAG088(unittest.TestCase):
    def test_probability_exact(self): self.assertEqual(miss_probability(17,3,3),Fraction(91,170))
    def test_probability_all_missing(self): self.assertEqual(miss_probability(10,10,2),0)
    def test_probability_one_missing(self): self.assertEqual(miss_probability(10,1,2),Fraction(4,5))
    def test_sample_all(self): self.assertEqual(miss_probability(10,1,10),0)
    def test_bad_n(self):
        with self.assertRaises(ValueError): miss_probability(0,1,1)
    def test_bad_missing_zero(self):
        with self.assertRaises(ValueError): miss_probability(10,0,1)
    def test_bad_missing_large(self):
        with self.assertRaises(ValueError): miss_probability(10,11,1)
    def test_bad_k(self):
        with self.assertRaises(ValueError): miss_probability(10,1,11)
    def test_bool_rejected(self):
        with self.assertRaises(ValueError): miss_probability(True,1,1)
    def test_budget_series_one(self): self.assertEqual(look_budget(Fraction(1,20),1),Fraction(1,40))
    def test_budget_series_sum(self):
        self.assertLess(sum((look_budget(Fraction(1,20),t) for t in range(1,101)),Fraction(0)),Fraction(1,20))
    def test_budget_invalid(self):
        with self.assertRaises(ValueError): look_budget(Fraction(1,20),0)
    def test_family_two(self):
        f=FamilyBudget();f.reserve('a',Fraction(1,40));f.reserve('b',Fraction(1,40));self.assertEqual(sum(f.allocations.values()),Fraction(1,20))
    def test_family_overdraft(self):
        f=FamilyBudget();f.reserve('a',Fraction(1,20))
        with self.assertRaises(ValueError): f.reserve('b',Fraction(1,100))
    def test_family_reuse(self):
        f=FamilyBudget();f.reserve('a',Fraction(1,40))
        with self.assertRaises(ValueError): f.reserve('a',Fraction(1,40))
    def test_family_negative(self):
        with self.assertRaises(ValueError): FamilyBudget(-1)
    def test_repeated_sample_deterministic(self):
        self.assertEqual(challenge_positions(SEED,'x',1,17,3),challenge_positions(SEED,'x',1,17,3))
    def test_unique_within_round(self):
        for t in range(1,20): self.assertEqual(len(set(challenge_positions(SEED,'x',t,17,5))),5)
    def test_positions_in_range(self):
        for t in range(1,12): self.assertTrue(all(0<=x<17 for x in challenge_positions(SEED,'x',t,17,3)))
    def test_sample_no_replacement_exact(self): self.assertEqual(challenge_positions(SEED,'x',1,5,5),tuple(range(5)))
    def test_round_index_changes(self): self.assertNotEqual(challenge_positions(SEED,'x',1,17,3),challenge_positions(SEED,'x',2,17,3))
    def test_experiment_domain_separation(self): self.assertNotEqual(challenge_positions(SEED,'x',1,17,3),challenge_positions(SEED,'y',1,17,3))
    def test_secret_min_length(self):
        with self.assertRaises(ValueError): make().__class__('a',17,3,3,FamilyBudget(),Fraction(1,20),b'short')
    def test_initial_state(self): self.assertEqual(make().status,'COLLECTING')
    def test_first_round(self): self.assertEqual(submit(make()).round,1)
    def test_exact_bound_one(self): self.assertEqual(submit(make()).p_bound,Fraction(91,170))
    def test_exact_bound_two(self):
        a=make();submit(a);s=submit(a);self.assertEqual(s.p_bound,Fraction(91,170)**2)
    def test_unique_coverage(self):
        a=make()
        for _ in range(5): submit(a)
        self.assertEqual(len(a.positions_seen),len(set().union(*(s.positions for s in a.snapshots))))
    def test_detect_missing(self): self.assertEqual(submit(make(),True).decision,'HOLD_DETECTED_MISSING')
    def test_no_new_challenge_after_detection(self):
        a=make();submit(a,True)
        with self.assertRaises(ValueError): a.challenge()
    def test_bad_round(self):
        a=make();t,p,n=a.challenge()
        with self.assertRaises(ValueError): a.submit(t+1,p,n,False)
    def test_bad_nonce(self):
        a=make();t,p,n=a.challenge()
        with self.assertRaises(ValueError): a.submit(t,p,'fake',False)
    def test_bad_positions(self):
        a=make();t,p,n=a.challenge()
        with self.assertRaises(ValueError): a.submit(t,tuple(reversed(p)),n,False)
    def test_duplicate_positions(self):
        a=make();t,p,n=a.challenge()
        with self.assertRaises(ValueError): a.submit(t,(p[0],)*3,n,False)
    def test_bad_missing_type(self):
        a=make();t,p,n=a.challenge()
        with self.assertRaises(ValueError): a.submit(t,p,n,0)
    def test_replay(self):
        a=make();args=a.challenge();a.submit(*args,False)
        with self.assertRaises(ValueError): a.submit(*args,False)
    def test_failed_submit_atomic(self):
        a=make();events=len(a.events)
        with self.assertRaises(ValueError): a.submit(1,(),'',False)
        self.assertEqual((a.round,len(a.events)),(0,events))
    def test_no_early_certify(self):
        a=make()
        with self.assertRaises(ValueError): a.certify()
    def test_early_stop_hold(self): self.assertEqual(make().stop(),'HOLD_EARLY_STOP')
    def test_early_stop_blocks_certification(self):
        a=make();a.stop()
        with self.assertRaises(ValueError): a.certify()
    def test_early_stop_audit(self):
        a=make();a.stop();self.assertTrue(a.ledger_valid())
    def test_demo_pass(self): self.assertEqual(demo()[1]['decision'],'CERTIFIED_STATISTICAL_BOUND')
    def test_demo_round_14(self): self.assertEqual(demo()[1]['rounds'],14)
    def test_demo_ledger(self): self.assertTrue(demo()[0].ledger_valid())
    def test_demo_events(self): self.assertEqual(demo()[1]['ledger_events'],16)
    def test_demo_coverage_not_round_count_times_hosts(self):
        a,_=demo();self.assertLessEqual(len(a.positions_seen),17)
    def test_demo_threshold(self):
        a,_=demo();s=a.snapshots[-1];self.assertLessEqual(s.p_bound,s.alpha_spent)
    def test_no_double_certify(self):
        a,_=demo()
        with self.assertRaises(ValueError): a.certify()
    def test_no_more_sample_after_certify(self):
        a,_=demo()
        with self.assertRaises(ValueError): a.challenge()
    def test_chain_mutation(self):
        a=make();submit(a);a.events[1]['data']['round']=100;self.assertFalse(a.ledger_valid())
    def test_chain_valid(self):
        a=make();submit(a);self.assertTrue(a.ledger_valid())
    def test_adaptive_sample_overlap_cannot_reset_p(self):
        a=make()
        for _ in range(4): submit(a)
        self.assertEqual(a.snapshots[-1].p_bound,a.q**4)
    def test_no_inflate_multihost(self):
        a=make();s=submit(a);self.assertEqual(s.unique_coverage,3)
    def test_pure_under_null_bound(self):
        a,_=demo();self.assertGreater(a.snapshots[0].p_bound,a.snapshots[0].alpha_spent)
    def test_all_missing_detected_if_reported(self):
        a=make(17,17,3);self.assertEqual(submit(a,True).decision,'HOLD_DETECTED_MISSING')
    def test_zero_probability_eligible_requires_certification(self):
        a=make(17,17,3);self.assertEqual(submit(a,False).decision,'ELIGIBLE_BOUND')
        self.assertEqual(a.certify(),'CERTIFIED_STATISTICAL_BOUND')
if __name__=='__main__': unittest.main()
