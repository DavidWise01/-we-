import unittest
from wag068 import Node,CascadeAudit,demonstration

class TestWAG068(unittest.TestCase):
    def setUp(self):
        self.g=CascadeAudit(quorum=3)
        for x in ('power','power2','host1','host2','host3'):
            self.g.add(Node(x,'domain'))
        self.g.add(Node('net','component',('power',)))
        self.g.add(Node('r1','component',('net','host1')))
        self.g.add(Node('r2','component',('net','host2')))
        self.g.add(Node('r3','component',('power2','host3')))
        for w,r,a in [('w1','r1','a'),('w2','r2','b'),('w3','r3','c')]:self.g.add(Node(w,'witness',(r,),a))

    def test_demo(self):self.assertTrue(demonstration()[1]['valid'])
    def test_no_failures(self):self.assertTrue(self.g.status(())['quorum'])
    def test_power_cascade(self):self.assertEqual(self.g.status(('power',))['survivors'],['w3'])
    def test_host1(self):self.assertEqual(self.g.status(('host1',))['survivors'],['w2','w3'])
    def test_power2(self):self.assertEqual(self.g.status(('power2',))['survivors'],['w1','w2'])
    def test_shared_network(self):self.assertIn('net',self.g.failed_nodes(('power',)))
    def test_transitive_ancestor(self):self.assertIn('w1',self.g.failed_nodes(('power',)))
    def test_transitive_two(self):self.assertIn('w2',self.g.failed_nodes(('power',)))
    def test_no_transitive_three(self):self.assertNotIn('w3',self.g.failed_nodes(('power',)))
    def test_no_duplicate_failure_count(self):self.assertEqual(self.g.status(('power','power'))['survivors'],['w3'])
    def test_minimal_quorum_cut_power(self):self.assertIn(('power',),self.g.minimal_cuts())
    def test_minimal_quorum_cut_host(self):self.assertIn(('host1',),self.g.minimal_cuts())
    def test_all_witness_cut(self):self.assertIn(('power','power2'),self.g.minimal_cuts('all_witnesses'))
    def test_all_witness_cut_three_hosts(self):self.assertIn(('host1','host2','host3'),self.g.minimal_cuts('all_witnesses'))
    def test_no_superset_minimal(self):
        cuts=[set(x) for x in self.g.minimal_cuts('all_witnesses')]
        self.assertTrue(all(not (a < b) for a in cuts for b in cuts))
    def test_parent_first(self):
        with self.assertRaises(ValueError):self.g.add(Node('bad','component',('missing',)))
    def test_cycle_self(self):
        with self.assertRaises(ValueError):self.g.add(Node('loop','component',('loop',)))
    def test_duplicate_node(self):
        with self.assertRaises(ValueError):self.g.add(Node('power','domain'))
    def test_duplicate_parent(self):
        with self.assertRaises(ValueError):self.g.add(Node('bad','component',('power','power')))
    def test_domain_parent(self):
        with self.assertRaises(ValueError):self.g.add(Node('bad','domain',('power',)))
    def test_component_no_parent(self):
        with self.assertRaises(ValueError):self.g.add(Node('bad','component'))
    def test_duplicate_witness_ancestor(self):
        with self.assertRaises(ValueError):self.g.add(Node('w4','witness',('r3',),'a'))
    def test_missing_witness_ancestor(self):
        with self.assertRaises(ValueError):self.g.add(Node('w4','witness',('r3',)))
    def test_nonwitness_ancestor(self):
        with self.assertRaises(ValueError):self.g.add(Node('extra','component',('power',),'wrong'))
    def test_unknown_failure_domain(self):
        with self.assertRaises(ValueError):self.g.status(('unknown',))
    def test_invalid_target(self):
        with self.assertRaises(ValueError):self.g.minimal_cuts('unknown')
    def test_bad_policy(self):
        with self.assertRaises(ValueError):CascadeAudit(quorum=0)
    def test_bounded_cut(self):
        g=CascadeAudit(quorum=3,max_cut_size=1)
        for x in ('a','b','c'):g.add(Node(x,'domain'))
        for i,x in enumerate(('a','b','c')):g.add(Node('w'+str(i),'witness',(x,),str(i)))
        self.assertEqual(g.minimal_cuts('all_witnesses'),[])
    def test_history_verified(self):self.assertTrue(self.g.verify())
    def test_tamper(self):
        self.g.history[1]['payload']['name']='changed';self.assertFalse(self.g.verify())
    def test_inspection_append(self):
        n=len(self.g.history);self.g.inspect_failure(('power',));self.assertEqual(len(self.g.history),n+1)
    def test_atomic_rejection(self):
        n=len(self.g.history)
        with self.assertRaises(ValueError):self.g.inspect_failure(('fake',))
        self.assertEqual(len(self.g.history),n)
    def test_unique_origins(self):self.assertEqual({w.ancestor for w in self.g.nodes.values() if w.kind=='witness'},{'a','b','c'})
    def test_recovery_not_implicit(self):
        self.g.inspect_failure(('power',))
        self.assertTrue(self.g.status(())['quorum'])
        self.assertEqual(self.g.history[-1]['kind'],'failure')

if __name__=='__main__':unittest.main()
