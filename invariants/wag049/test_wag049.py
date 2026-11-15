import unittest
from dataclasses import replace
from hashlib import sha256
from wag049 import Ceremony,Protocol,commitment,demonstration

class Tests(unittest.TestCase):
 def setUp(self):
  self.p=Protocol(('s1','s2','s3','s4'),2,10,('a','b','c'),('ff','cf','rr'))
  self.g=Ceremony(self.p)
  self.secrets={s:sha256(('synthetic:'+s).encode()).hexdigest() for s in self.p.entropy_source_ids}
 def commits(self):
  for s in self.p.entropy_source_ids:self.g.commit(s,commitment(s,self.secrets[s],self.g.protocol_hash),2)
 def cutoff(self):self.commits();self.g.seal_cutoff(10,('ff','cf','rr'))
 def reveals(self):
  self.cutoff()
  for s in self.p.entropy_source_ids:self.g.reveal(s,self.secrets[s],11)
 def test_demo(self):
  c,r=demonstration();self.assertTrue(c.verify());self.assertEqual(r['counts'],{'control':24,'intervention':24})
 def test_duplicate_subjects(self):
  with self.assertRaises(ValueError):Ceremony(replace(self.p,subjects=('x','x','y','z')))
 def test_insufficient_sources(self):
  with self.assertRaises(ValueError):Ceremony(replace(self.p,entropy_source_ids=('a','b')))
 def test_duplicate_roots(self):
  with self.assertRaises(ValueError):Ceremony(replace(self.p,witness_roots=('a','a','b')))
 def test_invalid_count(self):
  with self.assertRaises(ValueError):Ceremony(replace(self.p,treatment_count=4))
 def test_invalid_cutoff(self):
  with self.assertRaises(ValueError):Ceremony(replace(self.p,cutoff_tick=0))
 def test_commit_valid(self):
  self.g.commit('a',commitment('a',self.secrets['a'],self.g.protocol_hash),1);self.assertEqual(len(self.g.commits),1)
 def test_commit_late(self):
  with self.assertRaises(ValueError):self.g.commit('a','0'*64,10)
 def test_commit_bad_digest(self):
  with self.assertRaises(ValueError):self.g.commit('a','invalid',1)
 def test_commit_duplicate(self):
  self.g.commit('a','0'*64,1)
  with self.assertRaises(ValueError):self.g.commit('a','1'*64,2)
 def test_cutoff_requires_all_sources(self):
  with self.assertRaises(ValueError):self.g.seal_cutoff(10,('ff','cf','rr'))
 def test_cutoff_requires_three_roots(self):
  self.commits()
  with self.assertRaises(ValueError):self.g.seal_cutoff(10,('ff','cf'))
 def test_cutoff_wrong_tick(self):
  self.commits()
  with self.assertRaises(ValueError):self.g.seal_cutoff(11,('ff','cf','rr'))
 def test_cutoff_cannot_repeat(self):
  self.cutoff()
  with self.assertRaises(ValueError):self.g.seal_cutoff(10,('ff','cf','rr'))
 def test_reveal_before_cutoff(self):
  with self.assertRaises(ValueError):self.g.reveal('a',self.secrets['a'],11)
 def test_reveal_wrong_secret(self):
  self.cutoff()
  with self.assertRaises(ValueError):self.g.reveal('a','0'*64,11)
 def test_reveal_before_cutoff_tick(self):
  self.cutoff()
  with self.assertRaises(ValueError):self.g.reveal('a',self.secrets['a'],10)
 def test_reveal_duplicate(self):
  self.cutoff();self.g.reveal('a',self.secrets['a'],11)
  with self.assertRaises(ValueError):self.g.reveal('a',self.secrets['a'],12)
 def test_finalize_needs_reveals(self):
  self.cutoff()
  with self.assertRaises(ValueError):self.g.finalize(12,True,('ff','cf','rr'))
 def test_finalize_needs_concealment(self):
  self.reveals()
  with self.assertRaises(ValueError):self.g.finalize(12,False,('ff','cf','rr'))
 def test_finalize_needs_witnesses(self):
  self.reveals()
  with self.assertRaises(ValueError):self.g.finalize(12,True,('ff','cf'))
 def test_finalize_balanced(self):
  self.reveals();self.assertEqual(self.g.finalize(12,True,('ff','cf','rr'))['counts'],{'control':2,'intervention':2})
 def test_finalize_no_repeat(self):
  self.reveals();self.g.finalize(12,True,('ff','cf','rr'))
  with self.assertRaises(ValueError):self.g.finalize(13,True,('ff','cf','rr'))
 def test_ledger_tamper(self):
  self.commits();self.g.ledger[1]['payload']['source']='changed';self.assertFalse(self.g.verify())

if __name__=='__main__':unittest.main()
