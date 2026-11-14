import unittest
from wag020 import ForkLedger, Packet, demonstration

class ForkTests(unittest.TestCase):
    def setUp(self):
        self.l=ForkLedger()
        self.c=self.l.head

    def branch(self,name,value='7',root=None,event='E1',scope='t0'):
        return self.l.branch(self.c,Packet(event,scope,value,root or name,'packet-'+name),name)

    def test_valid_merge(self):
        self.assertEqual(self.l.reconcile(self.branch('a'),self.branch('b'))['decision'],'MERGE')
    def test_preserves_parent_nodes(self):
        a,b=self.branch('a'),self.branch('b')
        self.l.reconcile(a,b)
        self.assertIn(a,self.l.nodes)
        self.assertIn(b,self.l.nodes)
    def test_conflict(self):
        self.assertEqual(self.l.reconcile(self.branch('a'),self.branch('b','9'))['decision'],'CONFLICT')
    def test_conflict_does_not_change_head(self):
        a,b=self.branch('a'),self.branch('b','9')
        self.l.reconcile(a,b)
        self.assertEqual(self.l.head,self.c)
    def test_same_root_hold(self):
        self.assertEqual(self.l.reconcile(self.branch('a',root='shared'),self.branch('b',root='shared'))['decision'],'HOLD')
    def test_scope_mismatch(self):
        self.assertEqual(self.l.reconcile(self.branch('a'),self.branch('b',scope='t1'))['decision'],'HOLD')
    def test_event_mismatch(self):
        self.assertEqual(self.l.reconcile(self.branch('a'),self.branch('b',event='E2'))['decision'],'HOLD')
    def test_replay(self):
        self.branch('a')
        with self.assertRaises(ValueError): self.branch('a')
    def test_unknown_parent(self):
        with self.assertRaises(ValueError):
            self.l.branch('missing',Packet('E1','t0','7','r','p'),'a')
    def test_same_branch_cannot_merge(self):
        a=self.branch('a')
        with self.assertRaises(ValueError): self.l.reconcile(a,a)
    def test_different_parent(self):
        a=self.branch('a')
        b=self.l.branch(a,Packet('E1','t0','7','b','packet-b'),'b')
        with self.assertRaises(ValueError): self.l.reconcile(a,b)
    def test_cannot_reconcile_reconciliation(self):
        a,b=self.branch('a'),self.branch('b')
        r=self.l.reconcile(a,b)['node']
        with self.assertRaises(ValueError): self.l.reconcile(a,r)
    def test_ledger_valid(self):
        self.branch('a')
        self.assertTrue(self.l.verify())
    def test_tamper_detected(self):
        self.branch('a')
        self.l.records[1]['data']['payload']['author']='attacker'
        self.assertFalse(self.l.verify())
    def test_order_invariant_parents(self):
        a,b=self.branch('a'),self.branch('b')
        r=self.l.reconcile(b,a)
        self.assertEqual(r['parents'],tuple(sorted((a,b))))
    def test_demo(self):
        l,r=demonstration()
        self.assertEqual(r['decision'],'MERGE')
        self.assertTrue(l.verify())

if __name__=='__main__': unittest.main()
