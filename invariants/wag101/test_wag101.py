import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag101 import Actor,Gate,canon
class Tests(unittest.TestCase):
 def setUp(self):
  self.keys={n:Ed25519PrivateKey.generate() for n in ('W1','W2','W3','W4','E')}
  self.actors=[Actor(n,k.public_key().public_bytes_raw(),n+'c') for n,k in self.keys.items()]
  self.g=Gate(self.actors,100,'root100','nonce101');self.graph={a.controller:[] for a in self.actors}
 def packet(self):
  s=self.g.snapshot(self.graph);return s,self.keys['E'].sign(canon(s)),{n:self.keys[n].sign(canon(self.g.approval(s))) for n in ('W2','W3')}
 def run_gate(self):return self.g.evaluate(*self.packet())
 def test_good(self):self.assertEqual(self.run_gate(),'LOCAL_ROTATION_ELIGIBLE')
 def test_replay(self):self.run_gate();self.assertEqual(self.run_gate(),'HOLD_CONSUMED')
 def test_shared_reviewers(self):self.graph.update(W2c=['X'],W3c=['X'],X=[]);self.assertEqual(self.run_gate(),'HOLD_SHARED_CONTROL')
 def test_transitive(self):self.graph.update(W2c=['A'],W3c=['B'],A=['X'],B=['X'],X=[]);self.assertEqual(self.run_gate(),'HOLD_SHARED_CONTROL')
 def test_retired_controller(self):self.graph['W4c']=['W1c'];self.assertEqual(self.run_gate(),'HOLD_SHARED_CONTROL')
 def test_external_conflict(self):self.graph['Ec']=['W2c'];self.assertEqual(self.run_gate(),'HOLD_SHARED_CONTROL')
 def test_candidate_reviewer(self):self.graph['W4c']=['W3c'];self.assertEqual(self.run_gate(),'HOLD_SHARED_CONTROL')
 def test_unknown(self):self.graph['W2c']=['X'];self.assertEqual(self.run_gate(),'HOLD_UNKNOWN_ANCESTRY')
 def test_cycle(self):self.graph['W2c']=['W2c'];self.assertEqual(self.run_gate(),'HOLD_UNKNOWN_ANCESTRY')
 def test_missing_controller(self):del self.graph['W4c'];self.assertEqual(self.run_gate(),'HOLD_UNKNOWN_ANCESTRY')
 def test_malformed_graph(self):self.graph['W2c']='X';self.assertEqual(self.run_gate(),'HOLD_UNKNOWN_ANCESTRY')
 def test_bad_external(self):s,e,r=self.packet();self.assertEqual(self.g.evaluate(s,b'x',r),'HOLD_EXTERNAL_SIGNATURE')
 def test_bad_review(self):s,e,r=self.packet();r['W2']=b'x';self.assertEqual(self.g.evaluate(s,e,r),'HOLD_REVIEWS')
 def test_missing_review(self):s,e,r=self.packet();del r['W3'];self.assertEqual(self.g.evaluate(s,e,r),'HOLD_REVIEWS')
 def test_wrong_review(self):s,e,r=self.packet();r['W2']=r['W3'];self.assertEqual(self.g.evaluate(s,e,r),'HOLD_REVIEWS')
 def test_stale_scope(self):s,e,r=self.packet();s['proposal']='old';e=self.keys['E'].sign(canon(s));self.assertEqual(self.g.evaluate(s,e,r),'HOLD_SCOPE')
 def test_incomplete(self):s,e,r=self.packet();s['complete']=False;e=self.keys['E'].sign(canon(s));self.assertEqual(self.g.evaluate(s,e,r),'HOLD_SCOPE')
 def test_changed_graph(self):s,e,r=self.packet();s['graph']['X']=[];e=self.keys['E'].sign(canon(s));self.assertEqual(self.g.evaluate(s,e,r),'HOLD_REVIEWS')
 def test_audit(self):self.run_gate();self.run_gate();self.assertTrue(self.g.verify_audit())
 def test_tamper(self):self.run_gate();self.g.records[0]['status']='fake';self.assertFalse(self.g.verify_audit())
 def test_preserve(self):s,e,r=self.packet();self.g.evaluate(s,e,r);s['graph']['W2c'].append('X');self.assertEqual(self.g.records[0]['snapshot']['graph']['W2c'],[])
 def test_retry_after_rejection(self):self.graph['W2c']=['X'];self.run_gate();self.graph['W2c']=[];self.assertEqual(self.run_gate(),'LOCAL_ROTATION_ELIGIBLE');self.assertEqual(len(self.g.records),2)
 def test_key_collision(self):a=list(self.actors);a[-1]=Actor('E',a[0].key,'Ec');self.assertRaises(ValueError,Gate,a,100,'r','n')
 def test_detached_component_cycle(self):self.graph['X']=['X'];self.assertEqual(self.run_gate(),'HOLD_UNKNOWN_ANCESTRY')
if __name__=='__main__':unittest.main()