import unittest
from wag091 import Gate,Policy,demo
def fresh(retries=1):return Gate(Policy('f','r',17,3,retries))
def frozen(g):
    for w,s in zip(g.ws,('a','b','c')):g.commit(w,g.binding(w,s))
    g.freeze()
def abort(g):
    frozen(g);g.reveal('W1','a');g.reveal('W2','b');g.abort('W3 withheld')
class TestWag091(unittest.TestCase):
    def test_demo(self):self.assertEqual(demo()[0].state,'FINAL')
    def test_demo_audit(self):self.assertTrue(demo()[0].audit())
    def test_demo_three_unique(self):self.assertEqual(len(set(demo()[1])),3)
    def test_policy_rejects_invalid(self):
        with self.assertRaises(ValueError):Policy('f','r',2,3,1)
    def test_witness_duplicate(self):
        with self.assertRaises(ValueError):Gate(Policy('f','r',3,2,1),('W1','W1','W3'))
    def test_context_binding(self):
        g=fresh();self.assertNotEqual(g.binding('W1','a'),g.binding('W2','a'))
    def test_incomplete_freeze(self):
        with self.assertRaises(ValueError):fresh().freeze()
    def test_valid_freeze(self):g=fresh();frozen(g);self.assertEqual(g.state,'FROZEN')
    def test_invalid_reveal(self):
        g=fresh();frozen(g)
        with self.assertRaises(ValueError):g.reveal('W1','other')
    def test_duplicate_reveal(self):
        g=fresh();frozen(g);g.reveal('W1','a')
        with self.assertRaises(ValueError):g.reveal('W1','a')
    def test_abort_missing(self):
        g=fresh();abort(g);self.assertEqual(g.log[-1]['data']['missing'],['W3'])
    def test_no_finish_after_abort(self):
        g=fresh();abort(g)
        with self.assertRaises(ValueError):g.finish()
    def test_retry(self):
        g=fresh();abort(g);g.retry('b','value');self.assertEqual(g.epoch,1)
    def test_no_replay_beacon(self):
        g=fresh(2);abort(g);g.retry('b','value');abort(g)
        with self.assertRaises(ValueError):g.retry('b','value')
    def test_exhausted(self):
        g=fresh(0);abort(g)
        with self.assertRaises(ValueError):g.retry('b','value')
        self.assertEqual(g.state,'TERMINAL_HOLD')
    def test_no_retry_without_abort(self):
        with self.assertRaises(ValueError):fresh().retry('b','value')
    def test_wrong_state_abort(self):
        with self.assertRaises(ValueError):fresh().abort('why')
    def test_tamper(self):
        g=fresh();abort(g);g.log[1]['data']['w']='intruder';self.assertFalse(g.audit())
    def test_epoch_binding_changes(self):
        g=fresh();old=g.binding('W1','a');abort(g);g.retry('b','value')
        self.assertNotEqual(old,g.binding('W1','a'))
    def test_no_double_finish(self):
        g=fresh();frozen(g)
        for w,s in zip(g.ws,('a','b','c')):g.reveal(w,s)
        g.finish()
        with self.assertRaises(ValueError):g.finish()
if __name__=='__main__':unittest.main()
