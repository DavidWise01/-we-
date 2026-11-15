import unittest
from hashlib import sha256
from wag050 import Contributor, EntropyAudit, demonstration

class TestWAG050(unittest.TestCase):
    def setUp(self):
        self.a = EntropyAudit()
        self.secrets = {}
    def add(self, i, **changes):
        name = 's'+str(i)
        secret = sha256(('test:'+name).encode()).hexdigest()
        self.secrets[name] = secret
        fields = dict(name=name, origin='origin'+str(i), operator='operator'+str(i),
                      infrastructure='infra'+str(i), failure_domain='failure'+str(i),
                      commitment=self.a.pledge(name, secret, self.a.protocol_id))
        fields.update(changes)
        self.a.add(Contributor(**fields), i+1)
    def ready(self):
        for i in range(3): self.add(i)
        self.a.seal(10)
    def test_good(self):
        a,r=demonstration(); self.assertEqual(r['status'],'ELIGIBLE_FOR_EXTERNAL_VERIFICATION'); self.assertTrue(a.verify())
    def test_shared_domain(self):
        _,r=demonstration(shared=True); self.assertEqual(r['status'],'HOLD_SHARED_DOMAIN')
    def test_withholding(self):
        _,r=demonstration(withheld=True); self.assertEqual(r['status'],'ABORT_WITHHELD_REVEAL')
    def test_three_required(self):
        self.add(0)
        with self.assertRaises(ValueError): self.a.seal(10)
    def test_early_seal(self):
        for i in range(3): self.add(i)
        with self.assertRaises(ValueError): self.a.seal(9)
    def test_duplicate_name(self):
        self.add(0)
        with self.assertRaises(ValueError): self.add(0)
    def test_late_commit(self):
        with self.assertRaises(ValueError): self.a.add(Contributor('x','a','b','c','d','0'*64),10)
    def test_bad_hash(self):
        with self.assertRaises(ValueError): self.a.add(Contributor('x','a','b','c','d','bad'),1)
    def test_empty_domain(self):
        with self.assertRaises(ValueError): self.add(0,operator='')
    def test_shared_operator(self):
        self.add(0); self.add(1,operator='operator0'); self.add(2)
        self.assertEqual(self.a.seal(10),'HOLD_SHARED_DOMAIN')
    def test_shared_origin(self):
        self.add(0); self.add(1,origin='origin0'); self.add(2)
        self.assertEqual(self.a.seal(10),'HOLD_SHARED_DOMAIN')
    def test_shared_infrastructure(self):
        self.add(0); self.add(1,infrastructure='infra0'); self.add(2)
        self.assertEqual(self.a.seal(10),'HOLD_SHARED_DOMAIN')
    def test_no_reveal_on_hold(self):
        self.add(0); self.add(1,operator='operator0'); self.add(2); self.a.seal(10)
        with self.assertRaises(ValueError): self.a.reveal('s0',self.secrets['s0'],11)
    def test_reveal_before_seal(self):
        with self.assertRaises(ValueError): self.a.reveal('x','0'*64,11)
    def test_reveal_before_cutoff(self):
        self.ready()
        with self.assertRaises(ValueError): self.a.reveal('s0',self.secrets['s0'],10)
    def test_invalid_reveal(self):
        self.ready()
        with self.assertRaises(ValueError): self.a.reveal('s0','0'*64,11)
    def test_repeat_reveal(self):
        self.ready(); self.a.reveal('s0',self.secrets['s0'],11)
        with self.assertRaises(ValueError): self.a.reveal('s0',self.secrets['s0'],12)
    def test_unknown_reveal(self):
        self.ready()
        with self.assertRaises(ValueError): self.a.reveal('unknown','0'*64,11)
    def test_reseal(self):
        self.ready()
        with self.assertRaises(ValueError): self.a.seal(10)
    def test_no_finalize_before_seal(self):
        with self.assertRaises(ValueError): self.a.finalize(12)
    def test_finalize_no_retry_after_withholding(self):
        self.ready(); self.a.finalize(12)
        with self.assertRaises(ValueError): self.a.finalize(13)
    def test_tamper(self):
        self.add(0); self.a.history[1]['payload']['tick']=9
        self.assertFalse(self.a.verify())
    def test_atomic_rejection(self):
        n=len(self.a.history)
        with self.assertRaises(ValueError): self.a.add(Contributor('x','a','b','c','d','bad'),1)
        self.assertEqual(n,len(self.a.history))
    def test_invalid_policy(self):
        with self.assertRaises(ValueError): EntropyAudit(minimum=2)

if __name__=='__main__':
    unittest.main()
