"""WAG-061: synthetic anchored quorum recertification.

Locally generated signatures and an anchor receipt are NOT public anchoring.
"""
from dataclasses import dataclass, replace
from hashlib import sha256
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

def canonical(data):
    return json.dumps(data,sort_keys=True,separators=(',',':')).encode()

def digest(data):
    return sha256(canonical(data)).hexdigest()

def message(kind,payload):
    return canonical({'domain':'WAG061:'+kind+':v1','payload':payload})

@dataclass(frozen=True)
class Witness:
    identity:str
    ancestry:str
    operator:str
    failure_domain:str
    public_key:str
    signature:str
    head_digest:str
    tick:int

@dataclass(frozen=True)
class Anchor:
    identity:str
    operator:str
    failure_domain:str
    public_key:str
    signature:str
    head_digest:str
    tick:int

def sign(key,kind,payload):
    return key.sign(message(kind,payload)).hex()

def pubhex(key):
    return key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()

def verify(pub,signature,kind,payload):
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub)).verify(bytes.fromhex(signature),message(kind,payload))
    except (ValueError,InvalidSignature) as exc:
        raise ValueError('invalid signature') from exc

class QuorumGate:
    def __init__(self,history,*,min_quorum=3,max_age=5,frozen_tick=10):
        if not history or min_quorum<3 or max_age<0 or frozen_tick<0:
            raise ValueError('invalid policy')
        self.old=tuple(history);self.old_digest=digest(self.old)
        self.min_quorum,self.max_age,self.frozen_tick=min_quorum,max_age,frozen_tick
        self.new=None;self.witnesses={};self.anchor_receipt=None
        self.fork=False;self.status='FROZEN';self.events=[]
        self._append('freeze',{'root':self.old_digest,'size':len(self.old),'tick':frozen_tick})

    def _append(self,action,data):
        rec={'index':len(self.events),'prev':self.events[-1]['hash'] if self.events else '0'*64,'action':action,'data':data}
        rec['hash']=digest(rec);self.events.append(rec)

    def verify_chain(self):
        return all(r['index']==i and r['prev']==(self.events[i-1]['hash'] if i else '0'*64)
                   and r['hash']==digest({k:v for k,v in r.items() if k!='hash'})
                   for i,r in enumerate(self.events))

    @property
    def head_digest(self):
        return digest(self.new) if self.new is not None else None

    def reconnect(self,history):
        if self.new is not None or self.status!='FROZEN' or not history:
            raise ValueError('invalid reconnection')
        self.new=tuple(history)
        self._append('reconnect',{'head':self.head_digest,'size':len(self.new)})
        if len(self.new)<len(self.old):
            self.status='HOLD_ROLLBACK'
        elif self.new[:len(self.old)]!=self.old:
            self.status='QUARANTINE_FORK';self.fork=True
        elif len(self.new)==len(self.old):
            self.status='HOLD_NO_ADVANCE'
        else:
            self.status='PENDING_QUORUM'
        self._append('extension_audit',{'status':self.status,'frozen':self.old_digest,'new':self.head_digest})
        return self.status

    def witness(self,w):
        if (self.status!='PENDING_QUORUM' or not isinstance(w,Witness)
            or not all((w.identity,w.ancestry,w.operator,w.failure_domain))
            or w.identity in self.witnesses or w.head_digest!=self.head_digest
            or w.tick<self.frozen_tick or w.tick>self.frozen_tick+100):
            raise ValueError('witness packet')
        payload={'id':w.identity,'head':w.head_digest,'tick':w.tick,'ancestry':w.ancestry,
                 'operator':w.operator,'failure_domain':w.failure_domain}
        verify(w.public_key,w.signature,'witness',payload)
        for prior in self.witnesses.values():
            if w.ancestry==prior.ancestry or w.operator==prior.operator or w.failure_domain==prior.failure_domain:
                raise ValueError('shared declared provenance')
        self.witnesses[w.identity]=w;self._append('witness',payload)

    def anchor(self,a):
        if (self.status!='PENDING_QUORUM' or self.anchor_receipt is not None or
            not isinstance(a,Anchor) or not a.identity or a.head_digest!=self.head_digest or
            not a.operator or not a.failure_domain):
            raise ValueError('anchor')
        payload={'id':a.identity,'head':a.head_digest,'tick':a.tick,
                 'operator':a.operator,'failure_domain':a.failure_domain}
        verify(a.public_key,a.signature,'anchor',payload)
        if any(a.operator==w.operator or a.failure_domain==w.failure_domain for w in self.witnesses.values()):
            raise ValueError('shared anchor domain')
        self.anchor_receipt=a;self._append('anchor',payload)

    def certify(self,now):
        if self.status!='PENDING_QUORUM' or not isinstance(now,int):
            raise ValueError('cannot certify')
        if len(self.witnesses)<self.min_quorum or self.anchor_receipt is None:
            decision='HOLD_INCOMPLETE'
        elif (any(now<w.tick or now-w.tick>self.max_age for w in self.witnesses.values())
              or now<self.anchor_receipt.tick or now-self.anchor_receipt.tick>self.max_age):
            decision='HOLD_STALE'
        else:
            decision='RECERTIFIED_LOCAL_ANCHOR'
        self.status=decision
        self._append('decision',{'status':decision,'now':now,'quorum':len(self.witnesses)})
        return decision

def make_witness(key,identity,ancestry,operator,failure_domain,head,tick):
    payload={'id':identity,'head':head,'tick':tick,'ancestry':ancestry,
             'operator':operator,'failure_domain':failure_domain}
    return Witness(identity,ancestry,operator,failure_domain,pubhex(key),
                   sign(key,'witness',payload),head,tick)

def make_anchor(key,identity,operator,failure_domain,head,tick):
    payload={'id':identity,'head':head,'tick':tick,'operator':operator,'failure_domain':failure_domain}
    return Anchor(identity,operator,failure_domain,pubhex(key),sign(key,'anchor',payload),head,tick)

def demo():
    gate=QuorumGate(['a','b','c'])
    assert gate.reconnect(['a','b','c','d'])=='PENDING_QUORUM'
    for i in range(3):
        gate.witness(make_witness(Ed25519PrivateKey.generate(),f'W{i}',f'root{i}',
                                  f'operator{i}',f'failure{i}',gate.head_digest,12))
    gate.anchor(make_anchor(Ed25519PrivateKey.generate(),'A1','anchor-operator',
                            'anchor-domain',gate.head_digest,12))
    return gate,gate.certify(13)

if __name__=='__main__':
    g,result=demo()
    print(json.dumps({'decision':result,'events':len(g.events),'verified':g.verify_chain()},indent=2))
