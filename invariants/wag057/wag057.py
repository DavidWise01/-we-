"""WAG-057: signed, witnessed transparency-head conflict auditor.

Uses fully disclosed leaf lists to verify Merkle heads and cross-size prefixes;
this is NOT an RFC 6962 logarithmic consistency proof or a public log.
"""
from dataclasses import dataclass
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
import json


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def leaf(value):
    return sha256(b'\x00' + value.encode()).digest()


def tree_root(entries):
    """RFC6962-style left-balanced Merkle root over ordered string leaves."""
    if not entries:
        return sha256(b'').hexdigest()
    def subtree(start, size):
        if size == 1:
            return leaf(entries[start])
        k = 1 << ((size-1).bit_length()-1)
        return sha256(b'\x01' + subtree(start, k) + subtree(start+k, size-k)).digest()
    return subtree(0, len(entries)).hex()


def head_message(log_id, epoch, size, root):
    return canon({'domain': 'WAG057:tree-head:v1', 'log':log_id,
                  'epoch':epoch, 'size':size, 'root':root})


@dataclass(frozen=True)
class Head:
    witness: str
    origin: str
    failure_domain: str
    log_id: str
    epoch: int
    size: int
    root: str
    entries: tuple
    public_key_hex: str
    signature_hex: str


class TransparencyAuditor:
    def __init__(self, log_id='jane-log', min_witnesses=3):
        if not log_id or type(min_witnesses) is not int or min_witnesses < 2:
            raise ValueError('policy')
        self.log_id = log_id
        self.min_witnesses = min_witnesses
        self.heads = {}
        self.events = []
        self.state = 'COLLECTING'
        self._append('policy', {'log':log_id,'min_witnesses':min_witnesses})

    def _append(self, event, payload):
        record = {'seq':len(self.events), 'prev':self.events[-1]['hash'] if self.events else '0'*64,
                  'event':event,'payload':payload}
        record['hash'] = sha256(canon(record)).hexdigest()
        self.events.append(record)

    def verify_chain(self):
        return all(r['seq']==i and r['prev']==(self.events[i-1]['hash'] if i else '0'*64)
                   and r['hash']==sha256(canon({k:v for k,v in r.items() if k!='hash'})).hexdigest()
                   for i,r in enumerate(self.events))

    def ingest(self, head):
        if not isinstance(head, Head) or self.state!='COLLECTING' or not head.witness or not head.origin or not head.failure_domain or head.log_id!=self.log_id or head.witness in self.heads or type(head.epoch) is not int or head.epoch<0 or type(head.size) is not int or head.size<0 or not isinstance(head.entries,tuple) or len(head.entries)!=head.size or any(not isinstance(v,str) for v in head.entries):
            raise ValueError('invalid signed head')
        if any(head.origin==h.origin or head.failure_domain==h.failure_domain for h in self.heads.values()):
            raise ValueError('declared witness lineage overlap')
        if tree_root(head.entries)!=head.root:
            raise ValueError('disclosed leaves mismatch root')
        try:
            key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(head.public_key_hex))
            key.verify(bytes.fromhex(head.signature_hex),head_message(head.log_id,head.epoch,head.size,head.root))
        except (ValueError,InvalidSignature):
            raise ValueError('signature invalid')
        self.heads[head.witness]=head
        self._append('head', {'witness':head.witness, 'origin':head.origin,
            'failure_domain':head.failure_domain, 'epoch':head.epoch,
            'size':head.size, 'root':head.root,
            'entries':head.entries,'public_key_hex':head.public_key_hex,
            'signature_hex':head.signature_hex})

    def evaluate(self):
        if self.state!='COLLECTING':
            raise ValueError('audit already evaluated')
        if len(self.heads)<self.min_witnesses:
            result={'status':'HOLD_INSUFFICIENT','witnesses':len(self.heads),'conflicts':[]}
        else:
            conflicts=[]
            hs=list(self.heads.values())
            for i, a in enumerate(hs):
                for b in hs[i+1:]:
                    # Same-size disagreement is signed equivocation evidence.
                    # Cross-size mismatch in disclosed prefixes is a conflicting history.
                    shortest=min(a.size,b.size)
                    if a.entries[:shortest]!=b.entries[:shortest]:
                        conflicts.append({'a':a.witness,'b':b.witness,
                            'kind':'SAME_SIZE_FORK' if a.size==b.size else 'PREFIX_FORK'})
            result={'status':'QUARANTINE_SPLIT_VIEW' if conflicts else 'CONSISTENT_DISCLOSED_PREFIXES',
                    'witnesses':len(hs),'conflicts':conflicts}
        self.state=result['status']
        self._append('decision',result)
        return result


def make_head(witness,origin,domain,entries,key,epoch=100,log_id='jane-log'):
    from cryptography.hazmat.primitives import serialization
    entries=tuple(entries);root=tree_root(entries)
    pk=key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()
    sig=key.sign(head_message(log_id,epoch,len(entries),root)).hex()
    return Head(witness,origin,domain,log_id,epoch,len(entries),root,entries,pk,sig)


def demonstration():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    audit=TransparencyAuditor()
    common=('e1','e2','e3')
    paths=(common+('a',),common+('b',),common+('a','x'))
    for i,entries in enumerate(paths):
        audit.ingest(make_head(f'W{i+1}',f'root{i+1}',f'domain{i+1}',entries,Ed25519PrivateKey.generate()))
    return audit,audit.evaluate()


if __name__=='__main__':
    a,r=demonstration()
    print(json.dumps({'result':r,'records':len(a.events),'chain_valid':a.verify_chain()},indent=2))