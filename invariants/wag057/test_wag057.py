import unittest
from dataclasses import replace
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag057 import TransparencyAuditor,make_head,tree_root,demonstration,head_message

class Tests(unittest.TestCase):
    def setUp(self):
        self.a=TransparencyAuditor()
    def add(self,i,entries=('a','b','c'),**kw):
        h=make_head(f'W{i}',f'root{i}',f'domain{i}',entries,Ed25519PrivateKey.generate())
        self.a.ingest(replace(h,**kw))
    def test_demo(self):
        a,result=demonstration()
        self.assertEqual(result['status'],'QUARANTINE_SPLIT_VIEW')
        self.assertTrue(a.verify_chain())
    def test_demo_records(self):self.assertEqual(len(demonstration()[0].events),5)
    def test_same_head_consistent(self):
        for i in range(3):self.add(i)
        self.assertEqual(self.a.evaluate()['status'],'CONSISTENT_DISCLOSED_PREFIXES')
    def test_append_only_consistent(self):
        for i,e in enumerate((('a',),('a','b'),('a','b','c'))):self.add(i,e)
        self.assertEqual(self.a.evaluate()['status'],'CONSISTENT_DISCLOSED_PREFIXES')
    def test_same_size_fork(self):
        self.add(1,('a','x'));self.add(2,('a','y'));self.add(3,('a','x'))
        self.assertIn('SAME_SIZE_FORK',[v['kind'] for v in self.a.evaluate()['conflicts']])
    def test_prefix_fork(self):
        self.add(1,('a','x'));self.add(2,('a','y','z'));self.add(3,('a','x','z'))
        self.assertIn('PREFIX_FORK',[v['kind'] for v in self.a.evaluate()['conflicts']])
    def test_not_enough(self):
        self.add(1)
        self.assertEqual(self.a.evaluate()['status'],'HOLD_INSUFFICIENT')
    def test_duplicate_witness(self):
        self.add(1)
        with self.assertRaises(ValueError):self.add(1)
    def test_shared_origin(self):
        self.add(1)
        with self.assertRaises(ValueError):self.add(2,origin='root1')
    def test_shared_domain(self):
        self.add(1)
        with self.assertRaises(ValueError):self.add(2,failure_domain='domain1')
    def test_wrong_root(self):
        with self.assertRaises(ValueError):self.add(1,root='0'*64)
    def test_wrong_signature(self):
        with self.assertRaises(ValueError):self.add(1,signature_hex='00'*64)
    def test_wrong_public_key(self):
        with self.assertRaises(ValueError):self.add(1,public_key_hex='bad')
    def test_wrong_log(self):
        with self.assertRaises(ValueError):self.add(1,log_id='other-log')
    def test_bad_epoch(self):
        with self.assertRaises(ValueError):self.add(1,epoch=-1)
    def test_invalid_size(self):
        with self.assertRaises(ValueError):self.add(1,size=9)
    def test_no_add_after_decision(self):
        self.add(1);self.a.evaluate()
        with self.assertRaises(ValueError):self.add(2)
    def test_no_repeat_decision(self):
        self.a.evaluate()
        with self.assertRaises(ValueError):self.a.evaluate()
    def test_empty_tree(self):self.assertEqual(tree_root(()),'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')
    def test_domain_separation(self):self.assertNotEqual(tree_root(('x',)),tree_root(('x','x')))
    def test_tamper(self):
        self.add(1);self.a.events[1]['payload']['root']='malicious'
        self.assertFalse(self.a.verify_chain())
    def test_atomic_rejection(self):
        n=len(self.a.events)
        with self.assertRaises(ValueError):self.add(1,root='bad')
        self.assertEqual(n,len(self.a.events))
    def test_invalid_policy(self):
        with self.assertRaises(ValueError):TransparencyAuditor(min_witnesses=1)
    def test_different_operators_audited(self):
        for i in range(3):self.add(i)
        self.assertEqual(len(self.a.heads),3)

if __name__=='__main__':unittest.main()