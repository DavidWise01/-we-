"""WAG-059: authenticated freshness, partition holds, and rejoin reconciliation.

Deterministic reference. Public keys and failure-domain claims must be independently
attested before deployment. Full-leaf histories are used instead of compact proofs.
"""
from dataclasses import dataclass
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
import json


def enc(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def digest(x):
    return sha256(enc(x)).hexdigest()


def tree_root(leaves):
    if not leaves:
        return sha256(b'WAG059:empty').hexdigest()
    nodes=[sha256(b'\x00'+x.encode()).digest() for x in leaves]
    while len(nodes)>1:
        next_nodes=[]
        for i in range(0,len(nodes),2):
            if i+1==len(nodes):
                next_nodes.append(nodes[i])
            else:
                next_nodes.append(sha256(b'\x01'+nodes[i]+nodes[i+1]).digest())
        nodes=next_nodes
    return nodes[0].hex()


def message(witness, log_id, leaves, timestamp):
    return enc({'domain':'WAG059:gossip:v1','witness':witness,
                'log':log_id,'root':tree_root(leaves),
                'size':len(leaves),'timestamp':timestamp})


@dataclass(frozen=True)
class Witness:
    name: str
    origin: str
    failure_domain: str
    public_key: bytes


@dataclass(frozen=True)
class Head:
    witness: str
    leaves: tuple
    timestamp: int
    signature: bytes


class GossipMonitor:
    def __init__(self, log_id, witnesses, max_age=5, min_coverage=3):
        if not log_id or not isinstance(max_age,int) or max_age<0 or not isinstance(min_coverage,int) or min_coverage<3:
            raise ValueError('policy')
        self.witnesses={}
        origins=set();domains=set()
        for w in witnesses:
            if (not isinstance(w,Witness) or not all((w.name,w.origin,w.failure_domain))
                or w.name in self.witnesses or w.origin in origins or w.failure_domain in domains):
                raise ValueError('witness identity or claimed ancestry collision')
            Ed25519PublicKey.from_public_bytes(w.public_key)
            self.witnesses[w.name]=w
            origins.add(w.origin);domains.add(w.failure_domain)
        if min_coverage>len(self.witnesses):
            raise ValueError('insufficient registered witnesses')
        self.log_id=log_id;self.max_age=max_age;self.min_coverage=min_coverage
        self.heads={};self.history=[]
        self._append('policy',{'log':log_id,'max_age':max_age,'min_coverage':min_coverage,
                               'witnesses':sorted(self.witnesses)})

    def _append(self,kind,payload):
        entry={'seq':len(self.history),'prev':self.history[-1]['hash'] if self.history else '0'*64,
               'kind':kind,'payload':payload}
        entry['hash']=digest(entry)
        self.history.append(entry)

    def verify_history(self):
        return all(r['seq']==i and r['prev']==(self.history[i-1]['hash'] if i else '0'*64)
                   and r['hash']==digest({k:v for k,v in r.items() if k!='hash'})
                   for i,r in enumerate(self.history))

    def observe(self, head, received_at):
        if (not isinstance(head,Head) or head.witness not in self.witnesses or
            not isinstance(head.timestamp,int) or not isinstance(received_at,int) or
            head.timestamp<0 or head.timestamp>received_at or
            not isinstance(head.leaves,tuple) or not all(isinstance(x,str) and x for x in head.leaves)):
            raise ValueError('invalid report')
        old=self.heads.get(head.witness)
        if old and head.timestamp<=old.timestamp:
            raise ValueError('replayed or non-monotonic head')
        try:
            Ed25519PublicKey.from_public_bytes(self.witnesses[head.witness].public_key).verify(
                head.signature,message(head.witness,self.log_id,head.leaves,head.timestamp))
        except (InvalidSignature,ValueError,TypeError):
            raise ValueError('invalid signature')
        self.heads[head.witness]=head
        self._append('head',{'witness':head.witness,'timestamp':head.timestamp,
                             'root':tree_root(head.leaves),'leaves':list(head.leaves),
                             'signature':head.signature.hex()})

    def assess(self,now,unreachable=()):
        if not isinstance(now,int) or now<0:
            raise ValueError('invalid clock')
        offline=set(unreachable)
        if not offline.issubset(self.witnesses):
            raise ValueError('unknown partition member')
        fresh={w:h for w,h in self.heads.items() if w not in offline and 0<=now-h.timestamp<=self.max_age}
        # A witnessed conflicting history remains actionable even during a partition.
        # Inspect received (not just fresh) evidence to preserve known forks.
        observed=list(self.heads.items())
        forks=[]
        for i in range(len(observed)):
            for j in range(i+1,len(observed)):
                wa,ha=observed[i];wb,hb=observed[j]
                upto=min(len(ha.leaves),len(hb.leaves))
                if ha.leaves[:upto]!=hb.leaves[:upto]:
                    forks.append((wa,wb))
        if forks:
            state='QUARANTINE_FORK'
        elif offline:
            state='HOLD_PARTITION'
        elif len(fresh)<self.min_coverage or len(fresh)<len(self.witnesses):
            state='HOLD_STALE_OR_MISSING'
        else:
            heads={(len(h.leaves),tree_root(h.leaves)) for h in fresh.values()}
            state='CURRENT' if len(heads)==1 else 'HOLD_LAGGING'
        result={'state':state,'fresh':len(fresh),'expected':len(self.witnesses),
                'unreachable':sorted(offline),'conflicts':[list(pair) for pair in forks]}
        self._append('assessment',{'time':now,**result})
        return result


def demonstration():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    keys={f'W{i}':Ed25519PrivateKey.generate() for i in range(1,6)}
    witnesses=[Witness(n,'origin-'+n,'domain-'+n,k.public_key().public_bytes(
      serialization.Encoding.Raw,serialization.PublicFormat.Raw)) for n,k in keys.items()]
    m=GossipMonitor('L-C1',witnesses,max_age=5,min_coverage=3)
    def send(n,leaves,t):
        leaves=tuple(leaves)
        m.observe(Head(n,leaves,t,keys[n].sign(message(n,m.log_id,leaves,t))),t)
    for i in range(1,4):send(f'W{i}',('a','b','c'),10+i)
    isolated=m.assess(15,('W4','W5'))
    for i in (4,5):send(f'W{i}',('a','b','c'),16)
    rejoined=m.assess(16)
    return m,isolated,rejoined

if __name__=='__main__':
    m,a,b=demonstration()
    print(json.dumps({'partition':a,'rejoined':b,'records':len(m.history),
                      'ledger_valid':m.verify_history()},indent=2))