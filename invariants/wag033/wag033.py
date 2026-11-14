"""WAG-033: irrevocable adaptive statistical budget registration.

Reference model. Uses Decimal budgets, an append-only hash ledger, and a
predictable bounded e-process. Declared roots are NOT authenticated identity.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json

def D(value):
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("invalid decimal")
    if not d.is_finite():
        raise ValueError("nonfinite decimal")
    return d

def hash_data(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

@dataclass
class RegisteredTest:
    test_id: str
    owner: str
    alpha: Decimal
    priority: int
    registered_epoch: int
    e_value: Decimal = Decimal("1")
    last_tick: int = -1
    alarmed: bool = False

class HiveBudget:
    """An alpha-spending reference for any predeclared finite registration sequence."""
    def __init__(self, total="0.05", mu="0.5", bet="1"):
        self.total, self.mu, self.bet = D(total), D(mu), D(bet)
        if not (0 < self.total < 1 and 0 < self.mu < 1 and 0 <= self.bet <= 1/self.mu):
            raise ValueError("invalid policy")
        self.spent = Decimal("0")
        self.epoch = 0
        self.tests = {}
        self.agents = {"Jane": None}
        self.packet_ids = set()
        self.root_ids = set()
        self.records = []
        self._append("genesis", {"total": str(self.total), "mu": str(self.mu), "bet": str(self.bet)})

    def _append(self, kind, payload):
        rec = {"index": len(self.records), "kind": kind, "payload": payload,
               "previous": self.records[-1]["hash"] if self.records else "0"*64}
        rec["hash"] = hash_data(rec)
        self.records.append(rec)

    def verify(self):
        for i, rec in enumerate(self.records):
            if rec["index"] != i or rec["previous"] != (
                self.records[i-1]["hash"] if i else "0"*64):
                return False
            if rec["hash"] != hash_data({k:v for k,v in rec.items() if k!="hash"}):
                return False
        return True

    def spawn(self, name, parent="Jane"):
        if not name or name in self.agents or parent not in self.agents:
            raise ValueError("invalid agent lineage")
        self.agents[name] = parent
        self._append("spawn", {"agent": name, "parent": parent})

    def advance_epoch(self):
        self.epoch += 1
        self._append("epoch", {"epoch": self.epoch})

    def register(self, test_id, owner, alpha, priority, *, evidence_epoch):
        """Allocation is irrevocable, based only on a completed earlier epoch."""
        a = D(alpha)
        if not test_id or test_id in self.tests or owner not in self.agents:
            raise ValueError("invalid registration")
        if not isinstance(priority, int) or isinstance(priority, bool) or not 1<=priority<=5:
            raise ValueError("invalid priority")
        if not isinstance(evidence_epoch,int) or evidence_epoch < 0 or evidence_epoch >= self.epoch:
            raise ValueError("priority must use a prior completed epoch")
        if not 0 < a <= self.total-self.spent:
            raise ValueError("insufficient family budget")
        test = RegisteredTest(test_id, owner, a, priority, self.epoch)
        self.tests[test_id] = test
        self.spent += a
        self._append("register", {"test":test_id,"owner":owner,"alpha":str(a),
                                  "priority":priority,"evidence_epoch":evidence_epoch})
        return test

    def inherit(self, test_id, child):
        if test_id not in self.tests or child not in self.agents:
            raise ValueError("unknown test or child")
        current = self.tests[test_id].owner
        x = child
        while x is not None and x != current:
            x = self.agents[x]
        if x != current or child == current:
            raise ValueError("child must descend from owner")
        self.tests[test_id].owner = child
        self._append("inherit", {"test": test_id, "owner": child})

    def observe(self, test_id, owner, packet_id, root_id, tick, x):
        if test_id not in self.tests:
            raise ValueError("unregistered test")
        t = self.tests[test_id]
        v = D(x)
        if (owner != t.owner or not packet_id or not root_id or
            packet_id in self.packet_ids or root_id in self.root_ids or
            not isinstance(tick,int) or isinstance(tick,bool) or tick<=t.last_tick or
            not 0<=v<=1):
            raise ValueError("invalid observation")
        factor = 1 + self.bet*(v-self.mu)
        if factor < 0:
            raise ValueError("invalid betting factor")
        t.e_value *= factor
        t.last_tick = tick
        self.packet_ids.add(packet_id)
        self.root_ids.add(root_id)
        if t.e_value >= 1/t.alpha:
            t.alarmed = True
        self._append("observe", {"test":test_id,"owner":owner,"packet":packet_id,
                   "root":root_id,"tick":tick,"value":str(v),"e":str(t.e_value),
                   "alarmed":t.alarmed})
        return t.e_value

    @property
    def remaining(self):
        return self.total-self.spent

def demo():
    hive = HiveBudget()
    hive.spawn("scout")
    hive.advance_epoch()
    hive.register("high","scout","0.03",5,evidence_epoch=0)
    hive.register("low","Jane","0.005",1,evidence_epoch=0)
    hive.spawn("scout-child","scout")
    hive.inherit("high","scout-child")
    for tick in range(1,11):
        hive.observe("high","scout-child",f"p{tick}",f"root{tick}",tick,1)
    return hive

if __name__=="__main__":
    h = demo()
    print(json.dumps({"spent":str(h.spent),"remaining":str(h.remaining),
                      "high_alpha":str(h.tests["high"].alpha),
                      "owner":h.tests["high"].owner,
                      "e":str(h.tests["high"].e_value),
                      "alarm":h.tests["high"].alarmed,
                      "ledger_valid":h.verify()},indent=2))
