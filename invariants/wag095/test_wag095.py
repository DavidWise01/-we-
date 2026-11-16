import unittest
from wag095 import GossipGate, Observation

def pkt(op, rnd=5, digest="same", anchor=None, root=None, verified=True, anchored=True):
    return Observation(op, rnd, digest, anchor or "anchor-"+op,
                       root or "root-"+op, verified, anchored)

class GossipTests(unittest.TestCase):
    def setUp(self):
        self.g = GossipGate()
    def good(self):
        for op in "ABC":
            self.assertEqual("RECORDED", self.g.observe(pkt(op)))
    def test_agreement(self):
        self.good()
        self.assertEqual("ELIGIBLE_FOR_EXTERNAL_VERIFICATION", self.g.evaluate(5))
    def test_partition(self):
        for op in "AB": self.g.observe(pkt(op))
        self.assertEqual("HOLD_PARTITION_OR_MISSING", self.g.evaluate(5))
    def test_partition_recovery(self):
        for op in "AB": self.g.observe(pkt(op))
        self.assertEqual("HOLD_PARTITION_OR_MISSING", self.g.evaluate(5))
        self.g.observe(pkt("C"))
        self.assertEqual("ELIGIBLE_FOR_EXTERNAL_VERIFICATION", self.g.evaluate(5))
    def test_same_operator_fork(self):
        self.g.observe(pkt("A",digest="x"))
        self.assertEqual("QUARANTINE_EQUIVOCATION",self.g.observe(pkt("A",digest="y")))
        self.assertEqual(1,len(self.g.forks))
        self.assertEqual("QUARANTINE_EQUIVOCATION",self.g.evaluate(5))
    def test_old_round_is_not_fresh(self):
        for op in "ABC":self.g.observe(pkt(op,rnd=4))
        self.assertEqual("HOLD_PARTITION_OR_MISSING",self.g.evaluate(5))
    def test_shared_roots(self):
        for op in "ABC":self.g.observe(pkt(op,root="single"))
        self.assertEqual("HOLD_SHARED_ANCESTRY",self.g.evaluate(5))
    def test_shared_anchor(self):
        for op in "ABC":self.g.observe(pkt(op,anchor="single"))
        self.assertEqual("HOLD_SHARED_ANCHOR",self.g.evaluate(5))
    def test_different_digest_across_operators(self):
        for op in "ABC":self.g.observe(pkt(op,digest=op))
        self.assertEqual("HOLD_CROSS_OPERATOR_DISAGREEMENT",self.g.evaluate(5))
    def test_unsigned(self):
        self.assertEqual("HOLD_UNVERIFIED_EVIDENCE",self.g.observe(pkt("A",verified=False)))
    def test_no_external_receipt(self):
        self.assertEqual("HOLD_UNVERIFIED_EVIDENCE",self.g.observe(pkt("A",anchored=False)))
    def test_unknown_operator(self):
        self.assertEqual("HOLD_INVALID_SCOPE",self.g.observe(pkt("Z")))
    def test_bad_round(self):
        self.assertEqual("HOLD_INVALID_SCOPE",self.g.observe(pkt("A",rnd=-1)))
    def test_duplicate_same_statement_not_fork(self):
        self.g.observe(pkt("A"))
        self.assertEqual("RECORDED",self.g.observe(pkt("A")))
        self.assertFalse(self.g.forks)
    def test_fork_preserved(self):
        self.g.observe(pkt("A",digest="x"));self.g.observe(pkt("A",digest="y"))
        self.assertEqual(2,self.g.transcript()["observations"])
        self.assertEqual(1,self.g.transcript()["forks"])

if __name__ == "__main__":
    unittest.main()
