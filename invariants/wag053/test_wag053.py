import unittest
from wag053 import RecoveryAuditor, Policy, demonstration, fisher_two_sided

class Tests(unittest.TestCase):
    def setUp(self):
        self.a=RecoveryAuditor();self.a.seal(10)
    def initial_abort(self):
        self.a.attempt('C0','initial','abort',11,abort_reason='withheld')
    def recovery(self,**changes):
        params=dict(attempt_id='C1',stage='recovery',outcome='complete',tick=12,parent='C0',source=self.a.policy.fallback_source)
        params.update(changes);return self.a.attempt(**params)
    def test_demo(self):
        a,r=demonstration();self.assertTrue(a.verify());self.assertEqual(r['initial'],30)
    def test_demo_recoveries(self):
        _,r=demonstration();self.assertEqual((r['recovery'],r['completed_recovery'],r['aborted_recovery']),(10,9,1))
    def test_record_count(self):
        a,_=demonstration();self.assertEqual(len(a.records),43)
    def test_policy_hash(self):self.assertEqual(len(self.a.policy_hash),64)
    def test_bad_policy_recovery_limit(self):
        with self.assertRaises(ValueError):RecoveryAuditor(Policy(max_recoveries=2))
    def test_bad_policy_source(self):
        with self.assertRaises(ValueError):RecoveryAuditor(Policy(fallback_source=''))
    def test_seal_repeat(self):
        with self.assertRaises(ValueError):self.a.seal(10)
    def test_seal_tick(self):
        with self.assertRaises(ValueError):RecoveryAuditor().seal(9)
    def test_normal_attempt(self):
        self.a.attempt('C0','initial','complete',11);self.assertEqual(len(self.a.attempts),1)
    def test_abort_preserved(self):
        self.initial_abort();self.assertEqual(self.a.attempts['C0']['abort_reason'],'withheld')
    def test_abort_without_reason(self):
        with self.assertRaises(ValueError):self.a.attempt('C0','initial','abort',11)
    def test_complete_with_abort_reason(self):
        with self.assertRaises(ValueError):self.a.attempt('C0','initial','complete',11,abort_reason='bad')
    def test_replay(self):
        self.initial_abort()
        with self.assertRaises(ValueError):self.initial_abort()
    def test_recovery_valid(self):
        self.initial_abort();self.assertEqual(self.recovery()['parent'],'C0')
    def test_recovery_requires_parent(self):
        with self.assertRaises(ValueError):self.recovery()
    def test_recovery_after_complete_rejected(self):
        self.a.attempt('C0','initial','complete',11)
        with self.assertRaises(ValueError):self.recovery()
    def test_unapproved_fallback(self):
        self.initial_abort()
        with self.assertRaises(ValueError):self.recovery(source='attacker')
    def test_double_retry(self):
        self.initial_abort();self.recovery()
        with self.assertRaises(ValueError):self.recovery(attempt_id='C2')
    def test_recovery_abort(self):
        self.initial_abort();self.recovery(outcome='abort',abort_reason='withheld')
        self.assertEqual(self.a.report()['aborted_recovery'],1)
    def test_missing_recovery_report(self):
        self.initial_abort();self.assertEqual(self.a.report()['unrecovered_initial_aborts'],1)
    def test_wrong_stage(self):
        with self.assertRaises(ValueError):self.a.attempt('C0','unknown','complete',11)
    def test_atomic_rejection(self):
        n=len(self.a.records)
        with self.assertRaises(ValueError):self.recovery()
        self.assertEqual(len(self.a.records),n)
    def test_tamper(self):
        self.initial_abort();self.a.records[2]['payload']['outcome']='complete';self.assertFalse(self.a.verify())
    def test_fisher(self):
        self.assertAlmostEqual(fisher_two_sided(16,4,7,2),1.0)

if __name__=='__main__':unittest.main()
