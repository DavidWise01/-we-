"""WAG-050 declared entropy contributor independence and withholding audit.
Synthetic reference; does not verify actual entropy quality or source identity.
"""
from dataclasses import dataclass
from hashlib import sha256
import json

def digest(x):
    return sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

@dataclass(frozen=True)
class Contributor:
    name: str
    origin: str
    operator: str
    infrastructure: str
    failure_domain: str
    commitment: str

class EntropyAudit:
    def __init__(self, protocol_id='WAG050', minimum=3, cutoff=10):
        if not protocol_id or type(minimum) is not int or minimum < 3 or type(cutoff) is not int or cutoff < 1:
            raise ValueError('policy')
        self.protocol_id, self.minimum, self.cutoff = protocol_id, minimum, cutoff
        self.sources = {}
        self.reveals = {}
        self.sealed = False
        self.status = 'OPEN'
        self.history = []
        self._append('plan', {'protocol': protocol_id, 'minimum': minimum,
                              'cutoff': cutoff, 'withholding_policy': 'ABORT_NO_RETRY'})

    def _append(self, event, payload):
        entry = {'seq': len(self.history), 'prev': self.history[-1]['hash'] if self.history else '0'*64,
                 'event': event, 'payload': payload}
        entry['hash'] = digest(entry)
        self.history.append(entry)

    def verify(self):
        return all(r['seq'] == i and r['prev'] == (self.history[i-1]['hash'] if i else '0'*64)
                   and r['hash'] == digest({k: v for k, v in r.items() if k != 'hash'})
                   for i, r in enumerate(self.history))

    @staticmethod
    def pledge(name, secret, protocol_id):
        if not isinstance(secret, str) or len(secret) != 64 or any(c not in '0123456789abcdef' for c in secret):
            raise ValueError('secret')
        return digest({'domain': 'WAG050:contribution:v1', 'name': name,
                       'secret': secret, 'protocol': protocol_id})

    def add(self, source, tick):
        if (self.sealed or self.status != 'OPEN' or not isinstance(source, Contributor)
            or type(tick) is not int or not 0 <= tick < self.cutoff
            or source.name in self.sources or not all((source.name, source.origin,
                source.operator, source.infrastructure, source.failure_domain))
            or len(source.commitment) != 64
            or any(c not in '0123456789abcdef' for c in source.commitment)):
            raise ValueError('invalid contributor')
        self.sources[source.name] = source
        self._append('commit', {'tick': tick, 'source': vars(source)})

    def seal(self, tick):
        if self.sealed or self.status != 'OPEN' or type(tick) is not int or tick != self.cutoff or len(self.sources) < self.minimum:
            raise ValueError('seal')
        self.sealed = True
        self._append('seal', {'tick': tick, 'sources': sorted(self.sources)})
        problems = []
        for field in ('origin', 'operator', 'infrastructure', 'failure_domain'):
            values = [getattr(s, field) for s in self.sources.values()]
            if len(values) != len(set(values)):
                problems.append('SHARED_' + field.upper())
        self.status = 'HOLD_SHARED_DOMAIN' if problems else 'SEALED'
        self._append('domain_audit', {'status': self.status, 'problems': problems})
        return self.status

    def reveal(self, name, secret, tick):
        if (not self.sealed or self.status != 'SEALED' or name not in self.sources
            or name in self.reveals or type(tick) is not int or tick <= self.cutoff
            or self.pledge(name, secret, self.protocol_id) != self.sources[name].commitment):
            raise ValueError('reveal')
        self.reveals[name] = secret
        self._append('reveal', {'name': name, 'tick': tick, 'secret': secret})

    def finalize(self, tick):
        if not self.sealed or self.status != 'SEALED' or type(tick) is not int or tick <= self.cutoff:
            raise ValueError('finalize')
        if len(self.reveals) != len(self.sources):
            self.status = 'ABORT_WITHHELD_REVEAL'
            result = {'status': self.status, 'missing': sorted(set(self.sources)-set(self.reveals))}
        else:
            material = b'WAG050:combine:v1\0' + b''.join(bytes.fromhex(self.reveals[name]) for name in sorted(self.sources))
            self.status = 'ELIGIBLE_FOR_EXTERNAL_VERIFICATION'
            result = {'status': self.status, 'combined_digest': sha256(material).hexdigest(),
                      'source_count': len(self.sources)}
        self._append('finalize', result)
        return result

def demonstration(shared=False, withheld=False):
    audit = EntropyAudit()
    for i, name in enumerate(('physical', 'beacon', 'astronomical')):
        secret = sha256(('SYNTHETIC:' + name).encode()).hexdigest()
        audit.add(Contributor(name, 'origin'+str(i), 'operator'+str(i),
                 'infra'+str(i), 'failure0' if shared and i == 1 else 'failure'+str(i),
                 EntropyAudit.pledge(name, secret, audit.protocol_id)), i+1)
    audit.seal(10)
    if audit.status == 'SEALED':
        for name in audit.sources:
            if withheld and name == 'astronomical':
                continue
            audit.reveal(name, sha256(('SYNTHETIC:' + name).encode()).hexdigest(), 11)
        return audit, audit.finalize(12)
    return audit, {'status': audit.status}

if __name__ == '__main__':
    for mode in ({}, {'shared': True}, {'withheld': True}):
        a, r = demonstration(**mode)
        print(json.dumps({'mode': mode, 'result': r, 'ledger_ok': a.verify(),
                          'records': len(a.history)}, indent=2))
