import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from wag060 import RecoveryGate,Head,head_message,demonstration

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.key=Ed25519PrivateKey.generate()
        public=self.key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()
        self.g=RecoveryGate('log-A',public,max_age=5)
    def signed(self,leaves=('a','b','c'),epoch=10,log='log-A'):
        l=tuple(leaves)
        return Head(log,l,epoch,self.key.sign(head_message(log,l,epoch)).hex())
    def started(self):
        self.g.freeze(self.signed());self.g.partition('network lost')
    def test_demo(self):
        g,r=demonstration();self.assertEqual(r,'RESTORED');self.assertTrue(g.verify_history())
    def test_frozen_root_retained_until_success(self):
        self.started();old=self.g.frozen.root
        self.g.reconnect(self.signed(('a','b'),13),14)
        self.assertEqual(self.g.frozen.root,old)
    def test_valid_extension(self):
        self.started();self.assertEqual(self.g.reconnect(self.signed(('a','b','c','d'),13),14),'RESTORED')
    def test_equal_head_allowed(self):
        self.started();self.assertEqual(self.g.reconnect(self.signed(epoch=11),12),'RESTORED')
    def test_rollback(self):
        self.started();self.assertEqual(self.g.reconnect(self.signed(('a','b'),13),14),'HOLD_ROLLBACK')
    def test_prior_epoch(self):
        self.started();self.assertEqual(self.g.reconnect(self.signed(epoch=9),14),'HOLD_ROLLBACK')
    def test_fork(self):
        self.started();self.assertEqual(self.g.reconnect(self.signed(('a','x','c','d'),13),14),'QUARANTINE_FORK')
    def test_fork_is_terminal_hold(self):
        self.started();self.g.reconnect(self.signed(('x','b','c'),13),14)
        with self.assertRaises(ValueError):self.g.reconnect(self.signed(('a','b','c','d'),14),15)
    def test_known_fork_blocks_restoration(self):
        self.started();self.g.known_fork('conflict');self.assertEqual(self.g.status,'QUARANTINE_FORK')
    def test_stale(self):
        self.started();self.assertEqual(self.g.reconnect(self.signed(epoch=13),19),'HOLD_STALE')
    def test_fresh_retry_after_stale(self):
        self.started();self.g.reconnect(self.signed(epoch=11),20)
        self.assertEqual(self.g.reconnect(self.signed(('a','b','c','d'),21),22),'RESTORED')
    def test_invalid_signature(self):
        self.started();h=self.signed(('a','b','c','d'),13)
        with self.assertRaises(ValueError):self.g.reconnect(Head(h.log_id,h.leaves,h.epoch,'00'*64),14)
    def test_wrong_log(self):
        self.started()
        with self.assertRaises(ValueError):self.g.reconnect(self.signed(log='log-B'),14)
    def test_bad_time(self):
        self.started()
        with self.assertRaises(ValueError):self.g.reconnect(self.signed(epoch=14),13)
    def test_no_freeze_duplicate(self):
        self.g.freeze(self.signed())
        with self.assertRaises(ValueError):self.g.freeze(self.signed())
    def test_partition_without_freeze(self):
        with self.assertRaises(ValueError):self.g.partition('lost')
    def test_reconnect_without_partition(self):
        self.g.freeze(self.signed())
        with self.assertRaises(ValueError):self.g.reconnect(self.signed(),12)
    def test_double_partition(self):
        self.started()
        with self.assertRaises(ValueError):self.g.partition('again')
    def test_empty_reason(self):
        self.g.freeze(self.signed())
        with self.assertRaises(ValueError):self.g.partition('')
    def test_chain_valid(self):
        self.started();self.assertTrue(self.g.verify_history())
    def test_chain_tamper(self):
        self.started();self.g.history[1]['payload']['size']=900
        self.assertFalse(self.g.verify_history())
    def test_rejected_atomic(self):
        self.started();n=len(self.g.history)
        with self.assertRaises(ValueError):self.g.reconnect(self.signed(log='wrong'),14)
        self.assertEqual(len(self.g.history),n)
    def test_fork_preserves_freeze(self):
        self.started();old=self.g.frozen.root
        self.g.reconnect(self.signed(('z','b','c'),13),14)
        self.assertEqual(old,self.g.frozen.root)
    def test_policy_validation(self):
        with self.assertRaises(ValueError):RecoveryGate('log-A','00'*32,max_age=-1)
if __name__=='__main__':unittest.main()
