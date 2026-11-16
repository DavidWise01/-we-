"""WAG-095: independently signed *declared* commitment observation receipts.

Security boundary: logical sequence slots are signed claims, not trusted real time.
External identity/independence and public transparency must be verified separately.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def h(x):
    return sha256(canonical(x)).hexdigest()


@dataclass(frozen=True)
class Authority:
    name: str
    ancestry: str
    controller: str
    domain: str
    public_key: object


def sign(key, statement):
    return key.sign(canonical(statement)).hex()


def valid(key, statement, sig):
    try:
        key.verify(bytes.fromhex(sig), canonical(statement))
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


class ReceiptGate:
    def __init__(self, authorities, beacon, epoch, checkpoint, round_id):
        self.authorities = dict(authorities)
        self.beacon = beacon
        if len(self.authorities) != 3 or len(set(self.authorities)) != 3:
            raise ValueError('exactly three log authorities')
        for field in ('ancestry', 'controller', 'domain'):
            values = [getattr(a, field) for a in self.authorities.values()]
            if any(not isinstance(v, str) or not v for v in values) or len(set(values)) != 3:
                raise ValueError('shared declared control')
        if beacon.name in self.authorities or not all([beacon.ancestry, beacon.controller, beacon.domain]):
            raise ValueError('invalid beacon')
        if any(getattr(beacon, f) in {getattr(a, f) for a in self.authorities.values()} for f in ('ancestry','controller','domain')):
            raise ValueError('beacon shares declared authority')
        if not isinstance(epoch, int) or epoch < 0 or not isinstance(round_id, int) or round_id < 0:
            raise ValueError('bad epoch or round')
        if not isinstance(checkpoint, str) or len(checkpoint) != 64:
            raise ValueError('checkpoint must be a SHA-256 hex string')
        bytes.fromhex(checkpoint)
        self.epoch, self.checkpoint, self.round_id = epoch, checkpoint, round_id
        self.receipts = {}
        self.frozen = False
        self.freeze_hash = None
        self.release = None
        self.history = []
        self._record('genesis', {'epoch': epoch, 'checkpoint': checkpoint, 'round': round_id})

    def _record(self, event, data):
        value = {'sequence': len(self.history), 'previous': self.history[-1]['hash'] if self.history else '0'*64,
                 'event': event, 'data': data}
        value['hash'] = h(value)
        self.history.append(value)

    def audit_valid(self):
        return all(record['sequence'] == i and record['previous'] == (self.history[i-1]['hash'] if i else '0'*64)
                   and record['hash'] == h({k:v for k,v in record.items() if k != 'hash'})
                   for i,record in enumerate(self.history))

    def expected(self):
        return {'kind':'commit-observed', 'epoch':self.epoch,'round':self.round_id,'root':self.checkpoint}

    def observe(self, name, statement, signature):
        if self.frozen or self.release is not None:
            raise ValueError('receipt window frozen')
        if name not in self.authorities or name in self.receipts:
            raise ValueError('unknown or duplicate observer')
        if not isinstance(statement, dict) or any(statement.get(k) != v for k,v in self.expected().items()):
            raise ValueError('wrong committed checkpoint')
        if not isinstance(statement.get('slot'), int) or statement['slot'] < 0:
            raise ValueError('invalid logical slot')
        if not valid(self.authorities[name].public_key, statement, signature):
            raise ValueError('invalid observer signature')
        self.receipts[name] = (dict(statement), signature)
        self._record('observation', {'name': name, 'statement': statement, 'signature': signature})

    def freeze(self):
        if self.frozen or len(self.receipts) != 3:
            raise ValueError('missing receipts or already frozen')
        if len({r[0]['slot'] for r in self.receipts.values()}) != 1:
            raise ValueError('observers disagree on declared slot')
        self.freeze_hash = h({name:self.receipts[name] for name in sorted(self.receipts)})
        self.frozen = True
        self._record('freeze', {'receipt_set':self.freeze_hash})
        return self.freeze_hash

    def release_beacon(self, statement, signature):
        if not self.frozen or self.release is not None:
            raise ValueError('freeze required or duplicate release')
        template={'kind':'beacon-released','epoch':self.epoch,'round':self.round_id,
                  'root':self.checkpoint,'receipt_set':self.freeze_hash}
        if not isinstance(statement,dict) or any(statement.get(k) != v for k,v in template.items()):
            raise ValueError('release not bound to receipts')
        if not isinstance(statement.get('slot'),int) or statement['slot'] <= next(iter(self.receipts.values()))[0]['slot']:
            raise ValueError('release not later in declared order')
        entropy = statement.get('entropy')
        if not isinstance(entropy,str) or len(entropy) != 64:
            raise ValueError('bad entropy format')
        try: bytes.fromhex(entropy)
        except ValueError: raise ValueError('bad entropy hex') from None
        if not valid(self.beacon.public_key, statement, signature):
            raise ValueError('invalid beacon signature')
        self.release = (dict(statement), signature)
        self._record('beacon-release', {'statement':statement, 'signature':signature})
        return 'LOCAL_DECLARED_ORDER_ACCEPTED'

    def decision(self):
        if self.release is not None: return 'LOCAL_DECLARED_ORDER_ACCEPTED'
        if self.frozen: return 'HOLD_BEACON_MISSING'
        return 'HOLD_OBSERVERS_MISSING'


def demo():
    keys = {n:Ed25519PrivateKey.generate() for n in ('A','B','C','beacon')}
    authorities = {n:Authority(n,'root-'+n,'operator-'+n,'domain-'+n,keys[n].public_key()) for n in ('A','B','C')}
    beacon = Authority('beacon','root-beacon','operator-beacon','domain-beacon',keys['beacon'].public_key())
    root = sha256(b'frozen archive').hexdigest()
    gate = ReceiptGate(authorities,beacon,95,root,1)
    for n in ('A','B','C'):
        stmt={**gate.expected(),'slot':12}
        gate.observe(n,stmt,sign(keys[n],stmt))
    frozen=gate.freeze()
    release={'kind':'beacon-released','epoch':95,'round':1,'root':root,'receipt_set':frozen,
             'slot':13,'entropy':sha256(b'revealed beacon seed').hexdigest()}
    status=gate.release_beacon(release,sign(keys['beacon'],release))
    return gate, {'decision':status,'records':len(gate.history),'verified':gate.audit_valid(), 'receipt_set':frozen}

if __name__=='__main__':
    print(json.dumps(demo()[1],indent=2))