"""GitHub reference regression tests for WAG-036 (unittest)."""
import unittest
from decimal import Decimal
from wag036 import ClaimGraph

class TestClaimGraph(unittest.TestCase):
    def setUp(self):
        self.g=ClaimGraph()
        for c in "ABCD":self.g.claim(c,c,"example")

    def test_unknown(self):self.assertEqual(self.g.relation("A","B"),"unknown")
    def test_equivalent(self):
        self.g.relate("A","B","equivalent","reviewer",["e"])
        self.assertEqual(self.g.relation("B","A"),"equivalent")
    def test_equivalence_transitive(self):
        self.g.relate("A","B","equivalent","reviewer",["e"])
        self.g.relate("B","C","equivalent","reviewer",["f"])
        self.assertEqual(self.g.relation("A","C"),"equivalent")
    def test_entailment(self):
        self.g.relate("A","B","entails","reviewer",["e"])
        self.assertEqual(self.g.relation("A","B"),"entails")
        self.assertEqual(self.g.relation("B","A"),"entailed_by")
    def test_overlap(self):
        self.g.relate("A","B","overlaps","reviewer",["e"])
        self.assertEqual(self.g.relation("B","A"),"overlaps")
    def test_disjoint(self):
        self.g.relate("A","B","disjoint","reviewer",["e"])
        self.assertEqual(self.g.relation("A","B"),"disjoint")
    def test_conflict_blocked(self):
        self.g.relate("A","B","equivalent","reviewer",["e"])
        with self.assertRaises(ValueError):self.g.relate("A","B","disjoint","reviewer",["f"])
    def test_same_evidence_one_root(self):
        self.g.observe("A","root");self.g.observe("B","root")
        self.assertEqual(self.g.distinct_roots(["A","B"]),1)
    def test_duplicate_evidence_blocked(self):
        self.g.observe("A","root")
        with self.assertRaises(ValueError):self.g.observe("A","root")
    def test_spend(self):
        self.g.register("t","A",["r"],".02")
        self.assertEqual(self.g.remaining,Decimal(".03"))
    def test_no_reuse(self):
        self.g.register("t","A",["r"],".02")
        with self.assertRaises(ValueError):self.g.register("u","B",["r"],".01")
    def test_no_overspend(self):
        with self.assertRaises(ValueError):self.g.register("t","A",["r"],".06")
    def test_ledger_valid(self):self.assertTrue(self.g.verify())
    def test_ledger_tamper(self):
        self.g.log[1]["data"]["proposition"]="tampered"
        self.assertFalse(self.g.verify())

if __name__=="__main__":unittest.main()
