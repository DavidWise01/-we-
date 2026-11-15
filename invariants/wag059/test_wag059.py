import unittest
from dataclasses import replace
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from wag059 import Witness,Head,GossipMonitor,message,demonstration,tree_root

class Tests(unittest.TestCase):
    def setUp(self):
        self.keys={f'W{i}':Ed25519PrivateKey.generate() for i in range(1,6)}
        self.ws=[Witness(n,'origin'+n,'domain'+n,k.public_key().public_bytes(
            serialization.Encoding.Raw,serialization.PublicFormat.Raw)) for n,k in self.keys.items()]
        self.m=GossipMonitor('log',self.ws,max_age=5)
    def send(self,n,leaves=('a','b'),t=10,recv=None):
        leaves=tuple(leaves)
        return self.m.observe(Head(n,leaves,t,self.keys[n].sign(message(n,'log',leaves,t))),t if recv is None else recv)
    def send_all(self,leaves=('a','b'),t=10):
        for n in self.keys:self.send(n,leaves,t)
    def test_demo(self):
        m,a,b=demonstration();self.assertEqual(a['state'],'HOLD_PARTITION');self.assertEqual(b['state'],'CURRENT');self.assertTrue(m.verify_history())
    def test_current(self):
        self.send_all();self.assertEqual(self.m.assess(12)['state'],'CURRENT')
    def test_partition_hold_despite_quorum(self):
        for i in range(1,4):self.send(f'W{i}')
        self.assertEqual(self.m.assess(12,('W4','W5'))['state'],'HOLD_PARTITION')
    def test_rejoin(self):
        for i in range(1,4):self.send(f'W{i}')
        self.m.assess(12,('W4','W5'))
        self.send('W4',t=12);self.send('W5',t=12)
        self.assertEqual(self.m.assess(13)['state'],'CURRENT')
    def test_missing(self):self.assertEqual(self.m.assess(1)['state'],'HOLD_STALE_OR_MISSING')
    def test_stale(self):
        self.send_all();self.assertEqual(self.m.assess(16)['state'],'HOLD_STALE_OR_MISSING')
    def test_boundary_fresh(self):
        self.send_all();self.assertEqual(self.m.assess(15)['state'],'CURRENT')
    def test_lagging_same_prefix(self):
        self.send_all()
        self.send('W1',('a','b','c'),11)
        self.assertEqual(self.m.assess(12)['state'],'HOLD_LAGGING')
    def test_fork_same_size(self):
        self.send('W1',('a','b'));self.send('W2',('a','x'))
        self.assertEqual(self.m.assess(12)['state'],'QUARANTINE_FORK')
    def test_fork_different_size(self):
        self.send('W1',('a','b'));self.send('W2',('a','x','y'))
        self.assertEqual(self.m.assess(12)['state'],'QUARANTINE_FORK')
    def test_known_fork_even_offline(self):
        self.send('W1',('a','b'));self.send('W2',('a','x'))
        self.assertEqual(self.m.assess(12,('W2',))['state'],'QUARANTINE_FORK')
    def test_no_future_timestamp(self):
        with self.assertRaises(ValueError):self.send('W1',t=12,recv=10)
    def test_replay(self):
        self.send('W1')
        with self.assertRaises(ValueError):self.send('W1')
    def test_monotonic_time(self):
        self.send('W1',t=12)
        with self.assertRaises(ValueError):self.send('W1',t=11)
    def test_bad_signature(self):
        h=Head('W1',('a',),10,b'0'*64)
        with self.assertRaises(ValueError):self.m.observe(h,10)
    def test_modified_payload(self):
        good=self.keys['W1'].sign(message('W1','log',('a',),10))
        with self.assertRaises(ValueError):self.m.observe(Head('W1',('b',),10,good),10)
    def test_unknown_witness(self):
        with self.assertRaises(ValueError):self.m.observe(Head('W9',('a',),10,b''),10)
    def test_unknown_partition(self):
        with self.assertRaises(ValueError):self.m.assess(12,('W9',))
    def test_duplicate_origin(self):
        w=replace(self.ws[1],origin=self.ws[0].origin)
        with self.assertRaises(ValueError):GossipMonitor('log',[self.ws[0],w,*self.ws[2:]])
    def test_duplicate_domain(self):
        w=replace(self.ws[1],failure_domain=self.ws[0].failure_domain)
        with self.assertRaises(ValueError):GossipMonitor('log',[self.ws[0],w,*self.ws[2:]])
    def test_min_coverage_policy(self):
        with self.assertRaises(ValueError):GossipMonitor('log',self.ws,min_coverage=6)
    def test_empty_log_root(self):self.assertEqual(len(tree_root(())),64)
    def test_history_valid(self):
        self.send('W1');self.assertTrue(self.m.verify_history())
    def test_history_tamper(self):
        self.send('W1');self.m.history[1]['payload']['root']='tampered';self.assertFalse(self.m.verify_history())

if __name__=='__main__':unittest.main()