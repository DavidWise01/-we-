"""WAG-067: dependency-domain cuts over a strict three-witness quorum.

These are declared dependencies and local deterministic simulations, not
cryptographically authenticated failure-domain identities or Byzantine consensus.
"""
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


@dataclass(frozen=True)
class Witness:
    name: str
    ancestor: str
    dependencies: tuple[str, ...]


class DomainCutAudit:
    def __init__(self, witnesses, quorum=3):
        self.witnesses = tuple(witnesses)
        if len(self.witnesses) != 3 or quorum != 3:
            raise ValueError('three witnesses and strict quorum required')
        if any(not isinstance(w, Witness) for w in self.witnesses):
            raise ValueError('invalid witness')
        for key in ('name', 'ancestor'):
            fields = [getattr(w, key) for w in self.witnesses]
            if any(not isinstance(x, str) or not x for x in fields) or len(set(fields)) != 3:
                raise ValueError('invalid witness identity or origin')
        for w in self.witnesses:
            if not w.dependencies or any(not isinstance(d, str) or not d for d in w.dependencies):
                raise ValueError('empty dependency')
            if len(set(w.dependencies)) != len(w.dependencies):
                raise ValueError('repeated dependency')
        self.names = frozenset(w.name for w in self.witnesses)
        self.domain_to_witnesses = {
            d: frozenset(w.name for w in self.witnesses if d in w.dependencies)
            for d in sorted({d for w in self.witnesses for d in w.dependencies})
        }
        self.failed = set()
        self.history = []
        self._append('genesis', {'quorum': quorum, 'witnesses': [vars(w) for w in self.witnesses]})

    def _append(self, event, data):
        record = {'seq': len(self.history), 'prev': self.history[-1]['hash'] if self.history else '0'*64,
                  'event': event, 'data': data}
        record['hash'] = digest(record)
        self.history.append(record)

    def verify(self):
        return all(r['seq'] == i and r['prev'] == (self.history[i-1]['hash'] if i else '0'*64)
                   and r['hash'] == digest({k:v for k,v in r.items() if k != 'hash'})
                   for i,r in enumerate(self.history))

    def impacted(self, failures=None):
        failures = self.failed if failures is None else set(failures)
        if not failures.issubset(self.domain_to_witnesses):
            raise ValueError('unknown domain')
        affected = set()
        for d in failures:
            affected.update(self.domain_to_witnesses[d])
        return frozenset(affected)

    def survivors(self, failures=None):
        return self.names - self.impacted(failures)

    def state(self, failures=None):
        return 'ELIGIBLE_DECLARED_QUORUM' if len(self.survivors(failures)) == 3 else 'HOLD_COMMON_CAUSE'

    def minimal_cut_sets(self, minimum_affected=1):
        if not isinstance(minimum_affected, int) or not 1 <= minimum_affected <= 3:
            raise ValueError('invalid cut objective')
        domains = tuple(sorted(self.domain_to_witnesses))
        minimal = []
        for size in range(1, len(domains)+1):
            for group in combinations(domains, size):
                group_set = frozenset(group)
                if any(prior.issubset(group_set) for prior in minimal):
                    continue
                if len(self.impacted(group_set)) >= minimum_affected:
                    minimal.append(group_set)
        return sorted([tuple(sorted(c)) for c in minimal], key=lambda x: (len(x), x))

    def fail(self, domain):
        if domain not in self.domain_to_witnesses or domain in self.failed:
            raise ValueError('unknown or already failed domain')
        self.failed.add(domain)
        self._append('failure', {'domain': domain, 'affected': sorted(self.impacted()), 'state': self.state()})

    def repair(self, domain):
        if domain not in self.failed:
            raise ValueError('domain not failed')
        self.failed.remove(domain)
        self._append('repair', {'domain': domain, 'survivors': sorted(self.survivors()),
                                'state': self.state(), 'requires_fresh_attestation': True})

    def validate_fresh(self, receipts):
        if self.state() != 'ELIGIBLE_DECLARED_QUORUM' or not isinstance(receipts, dict) or set(receipts) != self.names:
            raise ValueError('quorum not restored')
        values = list(receipts.values())
        if any(not isinstance(x, str) or not x for x in values) or len(set(values)) != 3:
            raise ValueError('duplicate or absent attestations')
        self._append('reattest', {'receipt_ids': sorted(values), 'status': 'LOCAL_DECLARED_QUORUM'})
        return 'LOCAL_DECLARED_QUORUM'


def demo():
    a = DomainCutAudit((
        Witness('W1','A',('network-x','host-a')),
        Witness('W2','B',('network-x','host-b')),
        Witness('W3','C',('network-x','host-c'))))
    baseline = a.state()
    initial_cuts = a.minimal_cut_sets(3)
    a.fail('network-x')
    failed = {'affected': sorted(a.impacted()), 'survivors': sorted(a.survivors()), 'state': a.state()}
    a.repair('network-x')
    decision = a.validate_fresh({'W1':'new-a','W2':'new-b','W3':'new-c'})
    return a, {'baseline': baseline, 'minimum_all_three_cut_sets': initial_cuts,
               'failed': failed, 'after_repair': decision,
               'records': len(a.history), 'ledger_valid': a.verify()}

if __name__ == '__main__':
    print(json.dumps(demo()[1], indent=2))