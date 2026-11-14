import unittest
from decimal import Decimal
from wag033 import HiveBudget, demo

class TestWAG033(unittest.TestCase):
    def setUp(self):
        self.h=HiveBudget()
        self.h.spawn("a")
        self.h.advance_epoch()

    def reg(self, name="t", owner="a", alpha=".02"):
        return self.h.register(name,owner,alpha,4,evidence_epoch=0)

    def test_exact_budget(self):
        self.reg()
        self.h.register("t2","Jane",".03",1,evidence_epoch=0)
        self.assertEqual(self.h.remaining,Decimal(0))
    def test_budget_overflow_rejected(self):
        self.reg()
        with self.assertRaises(ValueError): self.h.register("t2","a",".031",2,evidence_epoch=0)
    def test_allocation_locked(self):
        t=self.reg()
        with self.assertRaises(ValueError): self.reg()
        self.assertEqual(t.alpha,Decimal(".02"))
    def test_prior_epoch_only(self):
        with self.assertRaises(ValueError): self.h.register("t","a",".02",4,evidence_epoch=1)
    def test_no_unfrozen_epoch(self):
        h=HiveBudget()
        with self.assertRaises(ValueError): h.register("t","Jane",".02",4,evidence_epoch=0)
    def test_priority_validated(self):
        with self.assertRaises(ValueError): self.h.register("t","a",".02",6,evidence_epoch=0)
    def test_child_inherits_without_refund(self):
        self.reg()
        self.h.spawn("b","a")
        self.h.inherit("t","b")
        self.assertEqual(self.h.spent,Decimal(".02"))
        self.assertEqual(self.h.tests["t"].owner,"b")
    def test_unrelated_inheritance_rejected(self):
        self.reg()
        self.h.spawn("b","Jane")
        with self.assertRaises(ValueError): self.h.inherit("t","b")
    def test_owner_permissions(self):
        self.reg()
        with self.assertRaises(ValueError): self.h.observe("t","Jane","p","r",1,1)
    def test_predictable_e_process(self):
        self.reg()
        self.assertEqual(self.h.observe("t","a","p","r",1,1),Decimal("1.5"))
    def test_alarm_threshold(self):
        self.reg(alpha=".02")
        for i in range(1,11): self.h.observe("t","a",f"p{i}",f"r{i}",i,1)
        self.assertTrue(self.h.tests["t"].alarmed)
    def test_replay_packet(self):
        self.reg()
        self.h.observe("t","a","p","r",1,1)
        with self.assertRaises(ValueError): self.h.observe("t","a","p","r2",2,1)
    def test_recycled_root(self):
        self.reg()
        self.h.observe("t","a","p","r",1,1)
        with self.assertRaises(ValueError): self.h.observe("t","a","p2","r",2,1)
    def test_bad_tick(self):
        self.reg()
        self.h.observe("t","a","p","r",2,1)
        with self.assertRaises(ValueError): self.h.observe("t","a","p2","r2",1,1)
    def test_nonfinite_or_unbounded(self):
        self.reg()
        for x in ("NaN","Infinity","1.1","-.1"):
            with self.assertRaises(ValueError): self.h.observe("t","a","p","r",1,x)
    def test_rejected_update_atomic(self):
        self.reg()
        n=len(self.h.records)
        with self.assertRaises(ValueError): self.h.observe("t","a","p","r",1,2)
        self.assertEqual(n,len(self.h.records))
    def test_ledger_tamper(self):
        self.reg()
        self.h.records[1]["payload"]["agent"]="attacker"
        self.assertFalse(self.h.verify())
    def test_policy_invalid(self):
        with self.assertRaises(ValueError): HiveBudget(total="1.5")
    def test_demo(self):
        h=demo()
        self.assertTrue(h.verify())
        self.assertEqual(h.remaining,Decimal(".015"))
        self.assertEqual(h.tests["high"].owner,"scout-child")
    def test_no_alpha_reset_on_spawn(self):
        self.reg()
        before=self.h.remaining
        self.h.spawn("b","a")
        self.assertEqual(self.h.remaining,before)

if __name__=="__main__":
    unittest.main()
