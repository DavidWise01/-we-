"""WAG-048: precommitted, reproducible allocation and concealment assertions.
Demonstration only: hash commitments do not prove random seed secrecy.
"""
from dataclasses import dataclass
from hashlib import sha256
from hmac import new as hmac_new
import json


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def generate_allocation(subjects, n_treated, secret):
    """Deterministic selection from committed seed; biased seeds remain possible."""
    if len(set(subjects)) != len(subjects) or not subjects or not 0 < n_treated < len(subjects):
        raise ValueError('invalid cohort')
    if not isinstance(secret, bytes) or len(secret) < 16:
        raise ValueError('invalid secret')
    scored = sorted((hmac_new(secret, ('WAG048:'+s).encode(), 'sha256').digest(), s) for s in subjects)
    treated = {s for _, s in scored[:n_treated]}
    return {s: ('treatment' if s in treated else 'control') for s in sorted(subjects)}


@dataclass(frozen=True)
class Witness:
    name: str
    origin: str
    observed_commit: str


class AllocationLedger:
    def __init__(self):
        self.events = []
        self.subjects = None
        self.precommit_hash = None
        self.assigned = None
        self.revealed = False
        self.witnesses = ()
        self.attested_concealment = False
        self._append('init', {})

    def _append(self, event, detail):
        row = {'seq': len(self.events), 'prev': self.events[-1]['hash'] if self.events else '0'*64,
               'event': event, 'detail': detail}
        row['hash'] = digest(row)
        self.events.append(row)

    def verify(self):
        return all(row['seq'] == i and row['prev'] == (self.events[i-1]['hash'] if i else '0'*64)
                   and row['hash'] == digest({k: v for k, v in row.items() if k != 'hash'})
                   for i, row in enumerate(self.events))

    def precommit(self, subjects, n_treated, commitment, witnesses, concealment_attested):
        if self.precommit_hash is not None or len(set(subjects)) != len(subjects) or not subjects:
            raise ValueError('invalid cohort or repeated precommit')
        if not 0 < n_treated < len(subjects) or not isinstance(commitment, str) or len(commitment) != 64:
            raise ValueError('invalid commitment')
        if len(witnesses) < 3 or len({w.name for w in witnesses}) != len(witnesses) or len({w.origin for w in witnesses}) != len(witnesses):
            raise ValueError('insufficient declared witnesses')
        if any(w.observed_commit != commitment for w in witnesses) or not concealment_attested:
            raise ValueError('witness or concealment mismatch')
        self.subjects = tuple(sorted(subjects))
        self.n_treated = n_treated
        self.precommit_hash = commitment
        self.witnesses = tuple(witnesses)
        self.attested_concealment = concealment_attested
        self._append('precommit', {'cohort_hash': digest(self.subjects), 'n_treated': n_treated,
                                   'seed_hash': commitment, 'witness_origins': [w.origin for w in witnesses],
                                   'concealment_attested': True})

    def commit_assignment(self, assignment):
        if self.precommit_hash is None or self.assigned is not None or set(assignment) != set(self.subjects):
            raise ValueError('invalid allocation')
        if set(assignment.values()) != {'control','treatment'} or sum(v == 'treatment' for v in assignment.values()) != self.n_treated:
            raise ValueError('invalid arm counts')
        self.assigned = dict(assignment)
        self.assignment_hash = digest(self.assigned)
        self._append('assignment', {'assignment_hash': self.assignment_hash})

    def reveal(self, secret):
        if self.assigned is None or self.revealed:
            raise ValueError('cannot reveal')
        if not isinstance(secret, bytes) or sha256(secret).hexdigest() != self.precommit_hash:
            raise ValueError('seed commitment mismatch')
        expected = generate_allocation(self.subjects, self.n_treated, secret)
        if expected != self.assigned:
            raise ValueError('reproducibility mismatch')
        self.revealed = True
        self._append('verified_reveal', {'assignment_hash': self.assignment_hash,
                                         'seed_hash': self.precommit_hash, 'mechanism': 'HMAC-SHA256 rank'})
        return 'CONSISTENT_WITH_PRECOMMITMENT_NOT_PROOF_OF_RANDOMNESS'


def demonstration():
    seed = b'synthetic-demo-seed-48-subjects-2026'
    cohort = [f'S{i:02d}' for i in range(48)]
    commitment = sha256(seed).hexdigest()
    witnesses = [Witness(f'w{i}', f'origin{i}', commitment) for i in range(3)]
    ledger = AllocationLedger()
    ledger.precommit(cohort, 24, commitment, witnesses, True)
    ledger.commit_assignment(generate_allocation(cohort, 24, seed))
    verdict = ledger.reveal(seed)
    return ledger, verdict

if __name__ == '__main__':
    l, verdict = demonstration()
    print(json.dumps({'verdict': verdict, 'records': len(l.events), 'ledger_valid': l.verify(),
                      'control': sum(x == 'control' for x in l.assigned.values()),
                      'treatment': sum(x == 'treatment' for x in l.assigned.values())}, indent=2))