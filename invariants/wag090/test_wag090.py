import unittest
from hashlib import sha256
from wag090 import RoundID, ChallengeRound, commit_digest, unbiased_without_replacement, example

def setup(N=17,k=3):
    rid=RoundID(90,'root-A','nonce-90',N,k)
    r=ChallengeRound(rid)
    seeds={'W1':b'a'*32,'W2':b'b'*32,'W3':b'c'*32}
    return r,seeds

def committed():
    r,s=setup()
    for w in r.witnesses:r.commit(w,commit_digest(vars(r.rid),w,s[w]))
    return r,s

def ready(order=('W1','W2','W3')):
    r,s=committed();r.freeze()
    for w in order:r.reveal(w,s[w])
    r.close_reveals()
    return r,s

class TestWAG090(unittest.TestCase):
    def test_example(self):self.assertTrue(example()['audit_valid'])
    def test_example_three(self):self.assertEqual(len(example()['indices']),3)
    def test_commit_three(self):self.assertEqual(len(committed()[0].commits),3)
    def test_initial(self):self.assertEqual(setup()[0].phase,'COMMIT')
    def test_two_commits_hold(self):
        r,s=setup();r.commit('W1',commit_digest(vars(r.rid),'W1',s['W1']));r.commit('W2',commit_digest(vars(r.rid),'W2',s['W2']))
        with self.assertRaises(ValueError):r.freeze()
    def test_freeze(self):r,s=committed();r.freeze();self.assertEqual(r.phase,'REVEAL')
    def test_late_commit(self):
        r,s=committed();r.freeze()
        with self.assertRaises(ValueError):r.commit('W1',commit_digest(vars(r.rid),'W1',s['W1']))
    def test_dup_commit(self):
        r,s=setup();r.commit('W1',commit_digest(vars(r.rid),'W1',s['W1']))
        with self.assertRaises(ValueError):r.commit('W1',commit_digest(vars(r.rid),'W1',s['W1']))
    def test_unknown_commit(self):
        r,s=setup()
        with self.assertRaises(ValueError):r.commit('W4','0'*64)
    def test_bad_commit(self):
        r,s=setup()
        with self.assertRaises(ValueError):r.commit('W1','bad')
    def test_early_reveal(self):
        r,s=committed()
        with self.assertRaises(ValueError):r.reveal('W1',s['W1'])
    def test_good_reveal(self):
        r,s=committed();r.freeze();self.assertEqual(r.reveal('W1',s['W1']),'REVEAL_ACCEPTED')
    def test_wrong_seed_hold(self):
        r,s=committed();r.freeze();self.assertEqual(r.reveal('W1',b'x'*32),'HOLD_INVALID_REVEAL')
    def test_wrong_seed_terminal(self):
        r,s=committed();r.freeze();r.reveal('W1',b'x'*32)
        with self.assertRaises(ValueError):r.reveal('W2',s['W2'])
    def test_missing_reveal_hold(self):
        r,s=committed();r.freeze();r.reveal('W1',s['W1']);self.assertEqual(r.close_reveals(),'HOLD_SELECTIVE_ABORT')
    def test_selective_abort_terminal(self):
        r,s=committed();r.freeze();r.close_reveals()
        with self.assertRaises(ValueError):r.reveal('W1',s['W1'])
    def test_hold_no_derive(self):
        r,s=committed();r.freeze();r.close_reveals()
        with self.assertRaises(ValueError):r.derive()
    def test_incomplete_no_derive(self):
        r,s=committed();r.freeze()
        with self.assertRaises(ValueError):r.derive()
    def test_full_ready(self):self.assertEqual(ready()[0].phase,'READY')
    def test_reveal_order_invariant(self):self.assertEqual(ready()[0].derive(),ready(('W3','W1','W2'))[0].derive())
    def test_same_input_deterministic(self):self.assertEqual(ready()[0].derive(),ready()[0].derive())
    def test_three_unique_indexes(self):
        indexes=ready()[0].derive();self.assertEqual(len(indexes),len(set(indexes)))
    def test_indexes_range(self):self.assertTrue(all(0<=i<17 for i in ready()[0].derive()))
    def test_challenge_domain_separation(self):
        r,s=ready();a=r.derive()
        changed=RoundID(90,'root-A','nonce-91',17,3)
        rr=ChallengeRound(changed)
        for w in rr.witnesses:rr.commit(w,commit_digest(vars(changed),w,s[w]))
        rr.freeze()
        for w in rr.witnesses:rr.reveal(w,s[w])
        rr.close_reveals();self.assertNotEqual(r.commits['W1'],rr.commits['W1'])
    def test_epoch_separation(self):
        a=RoundID(90,'root-A','n',17,3);b=RoundID(91,'root-A','n',17,3)
        self.assertNotEqual(commit_digest(vars(a),'W1',b'x'*32),commit_digest(vars(b),'W1',b'x'*32))
    def test_root_separation(self):
        a=RoundID(90,'A','n',17,3);b=RoundID(90,'B','n',17,3)
        self.assertNotEqual(commit_digest(vars(a),'W1',b'x'*32),commit_digest(vars(b),'W1',b'x'*32))
    def test_identity_separation(self):
        rid=vars(setup()[0].rid);self.assertNotEqual(commit_digest(rid,'W1',b'x'*32),commit_digest(rid,'W2',b'x'*32))
    def test_weak_seed_reject(self):
        with self.assertRaises(ValueError):commit_digest({},'W1',b'weak')
    def test_nonbytes_reject(self):
        with self.assertRaises(ValueError):commit_digest({},'W1','not bytes')
    def test_duplicate_witnesses(self):
        with self.assertRaises(ValueError):ChallengeRound(setup()[0].rid,('W1','W1','W3'))
    def test_missing_witness(self):
        with self.assertRaises(ValueError):ChallengeRound(setup()[0].rid,('W1','W2'))
    def test_empty_witness(self):
        with self.assertRaises(ValueError):ChallengeRound(setup()[0].rid,('W1','','W3'))
    def test_invalid_epoch(self):
        with self.assertRaises(ValueError):RoundID(-1,'r','n',17,3)
    def test_invalid_root(self):
        with self.assertRaises(ValueError):RoundID(90,'','n',17,3)
    def test_invalid_nonce(self):
        with self.assertRaises(ValueError):RoundID(90,'r','',17,3)
    def test_invalid_archive(self):
        with self.assertRaises(ValueError):RoundID(90,'r','n',0,1)
    def test_invalid_sample(self):
        with self.assertRaises(ValueError):RoundID(90,'r','n',3,4)
    def test_zero_sample(self):
        with self.assertRaises(ValueError):RoundID(90,'r','n',3,0)
    def test_audit_ok(self):self.assertTrue(ready()[0].audit_valid())
    def test_audit_tamper(self):
        r,s=ready();r.events[1]['data']['witness']='other';self.assertFalse(r.audit_valid())
    def test_audit_seq_tamper(self):
        r,s=ready();r.events[1]['seq']=99;self.assertFalse(r.audit_valid())
    def test_precommit_seed_not_logged(self):
        r,s=committed();self.assertNotIn(s['W1'].hex(),str(r.events))
    def test_valid_sampler_one(self):self.assertEqual(unbiased_without_replacement(b'\x00'*32,1,1),(0,))
    def test_sampler_complete(self):self.assertEqual(set(unbiased_without_replacement(b'\x00'*32,7,7)),set(range(7)))
    def test_sampler_invalid_key(self):
        with self.assertRaises(ValueError):unbiased_without_replacement(b'x',7,3)
    def test_sampler_invalid_k(self):
        with self.assertRaises(ValueError):unbiased_without_replacement(b'\0'*32,7,8)
    def test_sampler_repeat(self):self.assertEqual(unbiased_without_replacement(b'\0'*32,17,3),unbiased_without_replacement(b'\0'*32,17,3))
    def test_reveal_duplicate(self):
        r,s=committed();r.freeze();r.reveal('W1',s['W1'])
        with self.assertRaises(ValueError):r.reveal('W1',s['W1'])
    def test_freeze_duplicate(self):
        r,s=committed();r.freeze()
        with self.assertRaises(ValueError):r.freeze()
    def test_close_duplicate(self):
        r,s=ready()
        with self.assertRaises(ValueError):r.close_reveals()
    def test_hold_audit(self):
        r,s=committed();r.freeze();r.close_reveals();self.assertTrue(r.audit_valid())
    def test_invalid_reveal_audit(self):
        r,s=committed();r.freeze();r.reveal('W1',b'badbadbadbadbadbad');self.assertTrue(r.audit_valid())

if __name__=='__main__':unittest.main()
