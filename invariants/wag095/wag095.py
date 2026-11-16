"""WAG-095 deterministic gossip/partition policy model.

Not a live transparency service, cryptographic verifier, or demonstration of
independent custody. Callers must separately authenticate proof and ancestry.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Observation:
    operator: str
    round_id: int
    digest: str
    anchor: str
    root: str
    authenticated: bool = False
    externally_anchored: bool = False

class GossipGate:
    def __init__(self, operators=("A", "B", "C"), min_roots=3):
        self.operators = frozenset(operators)
        self.min_roots = min_roots
        self.observations = []
        self.latest = {}
        self.forks = []
        self.holds = []

    def observe(self, x):
        if x.operator not in self.operators or x.round_id < 0:
            self.holds.append(("INVALID_SCOPE", x))
            return "HOLD_INVALID_SCOPE"
        if not x.authenticated or not x.externally_anchored:
            self.holds.append(("UNVERIFIED_EVIDENCE", x))
            return "HOLD_UNVERIFIED_EVIDENCE"
        prior = [o for o in self.observations if
                 o.operator == x.operator and o.round_id == x.round_id]
        if prior and any(o.digest != x.digest for o in prior):
            self.forks.append((prior[0], x))
            self.observations.append(x)
            return "QUARANTINE_EQUIVOCATION"
        self.observations.append(x)
        if x.round_id > self.latest.get(x.operator, -1):
            self.latest[x.operator] = x.round_id
        return "RECORDED"

    def evaluate(self, required_round):
        if self.forks:
            return "QUARANTINE_EQUIVOCATION"
        observations = [o for o in self.observations if
                        o.round_id == required_round and
                        o.authenticated and o.externally_anchored]
        by_operator = {}
        for o in observations:
            by_operator.setdefault(o.operator, o)
        if len(by_operator) < len(self.operators):
            return "HOLD_PARTITION_OR_MISSING"
        if len({o.root for o in by_operator.values()}) < self.min_roots:
            return "HOLD_SHARED_ANCESTRY"
        if len({o.anchor for o in by_operator.values()}) < self.min_roots:
            return "HOLD_SHARED_ANCHOR"
        if len({o.digest for o in by_operator.values()}) != 1:
            return "HOLD_CROSS_OPERATOR_DISAGREEMENT"
        if any(self.latest.get(op, -1) < required_round for op in self.operators):
            return "HOLD_STALE"
        return "ELIGIBLE_FOR_EXTERNAL_VERIFICATION"

    def transcript(self):
        return {"observations": len(self.observations),
                "forks": len(self.forks), "holds": len(self.holds),
                "latest": dict(self.latest)}
