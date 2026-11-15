import unittest
from hashlib import sha256
from wag051 import CeremonyLedger, Contributor, demo

class TestWAG051(unittest.TestCase):
    def setUp(self):
        self.g=CeremonyLedger()
        self.g.open_round('r')
        self.secrets={n:sha256(n.encode()).hexdigest() for n in 'ABC'}
    def commit_all(self):
        for i,n in enumerate('ABC'):
            self.g.commit('r',Contributor(n,'root'+n,'domain'+n,
                          self.g.pledge('r',n,self.secrets[n])),i+1)
    def sealed(self):
        self.commit_all();self.g.seal('r',10)
    def test_demo(self):
        l=demo();self.assertTrue(l.verify());self.assertEqual(l.audit()['aborted'],1)
    def test_three_attempts(self):self.assertEqual(demo().audit()['attempts'],3)
    def test_abort_rate(self):self.assertAlmostEqual(demo().audit()['abort_rate'],1/3)
    def test_good_commit(self):self.commit_all();self.assertEqual(len(self.g.rounds['r']['sources']),3)
    def test_bad_commit_digest(self):
        with self.assertRaises(ValueError):self.g.commit('r',Contributor('A','rootA','domainA','bad'),1)
    def test_late_commit(self):
        with self.assertRaises(ValueError):self.g.commit('r',Contributor('A','rootA','domainA','0'*64),10)
    def test_duplicate_commit(self):
        self.commit_all()
        with self.assertRaises(ValueError):self.g.commit('r',Contributor('A','rootA','domainA','0'*64),4)
    def test_insufficient_seal(self):
        with self.assertRaises(ValueError):self.g.seal('r',10)
    def test_wrong_seal_time(self):
        self.commit_all()
        with self.assertRaises(ValueError):self.g.seal('r',9)
    def test_shared_root(self):
        self.commit_all();self.g.rounds['r']['sources']['B']=Contributor('B','rootA','domainB','0'*64)
        with self.assertRaises(ValueError):self.g.seal('r',10)
    def test_shared_domain(self):
        self.commit_all();self.g.rounds['r']['sources']['B']=Contributor('B','rootB','domainA','0'*64)
        with self.assertRaises(ValueError):self.g.seal('r',10)
    def test_reveal_before_seal(self):
        with self.assertRaises(ValueError):self.g.reveal('r','A',self.secrets['A'],11)
    def test_reveal_at_cutoff(self):
        self.sealed()
        with self.assertRaises(ValueError):self.g.reveal('r','A',self.secrets['A'],10)
    def test_wrong_reveal(self):
        self.sealed()
        with self.assertRaises(ValueError):self.g.reveal('r','A','0'*64,11)
    def test_duplicate_reveal(self):
        self.sealed();self.g.reveal('r','A',self.secrets['A'],11)
        with self.assertRaises(ValueError):self.g.reveal('r','A',self.secrets['A'],12)
    def test_full_completion(self):
        self.sealed()
        for n in 'ABC':self.g.reveal('r',n,self.secrets[n],11)
        self.assertEqual(self.g.finalize('r',12)['status'],'COMPLETE')
    def test_withheld_aborts(self):
        self.sealed();self.g.reveal('r','A',self.secrets['A'],11)
        self.assertEqual(self.g.finalize('r',12)['missing'],['B','C'])
    def test_no_late_reveal_after_abort(self):
        self.sealed();self.g.finalize('r',12)
        with self.assertRaises(ValueError):self.g.reveal('r','A',self.secrets['A'],13)
    def test_no_same_round_retry(self):
        self.sealed();self.g.finalize('r',12)
        with self.assertRaises(ValueError):self.g.finalize('r',13)
    def test_new_round_has_parent(self):
        self.sealed();self.g.finalize('r',12);self.g.open_round('new',parent='r')
        self.assertEqual(self.g.rounds['new']['parent'],'r')
    def test_cannot_recover_nonaborted(self):
        self.sealed()
        with self.assertRaises(ValueError):self.g.open_round('new',parent='r')
    def test_no_duplicate_round(self):
        with self.assertRaises(ValueError):self.g.open_round('r')
    def test_ledger_tamper(self):
        self.commit_all();self.g.events[1]['value']['round']='tampered';self.assertFalse(self.g.verify())
    def test_rejected_atomic(self):
        before=len(self.g.events)
        with self.assertRaises(ValueError):self.g.reveal('r','A',self.secrets['A'],11)
        self.assertEqual(len(self.g.events),before)

if __name__=='__main__':unittest.main()
