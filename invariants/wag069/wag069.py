"""WAG-069 synthetic ordered repair and fresh-attestation reference.
Declarations are not cryptographic source or physical infrastructure verification.
"""
from dataclasses import dataclass
from hashlib import sha256
import json

def hash_event(e):
    return sha256(json.dumps(e,sort_keys=True,separators=(',',':')).encode()).hexdigest()

@dataclass(frozen=True)
class Witness:
    name:str
    ancestor:str
    operator:str
    failure_domain:str
    host:str

class RecoveryGate:
    def __init__(self,witnesses,dependencies):
        self.witnesses=tuple(witnesses)
        self.dependencies={k:frozenset(ds) for k,ds in dependencies.items()}
        if len(self.witnesses)!=3:raise ValueError('three witnesses required')
        for key in ('name','ancestor','operator','failure_domain','host'):
            vals=[getattr(w,key) for w in self.witnesses]
            if len(set(vals))!=3 or any(not isinstance(x,str) or not x for x in vals):raise ValueError('provenance collision')
        self.nodes=set(self.dependencies)
        if any(not isinstance(k,str) or not k or any(d not in self.nodes for d in ds) for k,ds in self.dependencies.items()):
            raise ValueError('invalid dependency')
        if any(w.host not in self.nodes for w in self.witnesses):raise ValueError('host missing')
        self.order=self.topological_order()
        self.broken=set();self.verified=set(self.nodes);self.receipts={};self.ledger=[]
        self.append('genesis',{'nodes':{k:sorted(v) for k,v in self.dependencies.items()},'witnesses':[vars(w) for w in self.witnesses]})
    def topological_order(self):
        remaining=set(self.nodes);order=[]
        while remaining:
            ready=sorted(n for n in remaining if self.dependencies[n]<=set(order))
            if not ready:raise ValueError('dependency cycle')
            order+=ready;remaining-=set(ready)
        return tuple(order)
    def append(self,kind,data):
        e={'seq':len(self.ledger),'previous':self.ledger[-1]['hash'] if self.ledger else '0'*64,'kind':kind,'data':data}
        e['hash']=hash_event(e);self.ledger.append(e)
    def audit_ok(self):
        return all(e['seq']==i and e['previous']==(self.ledger[i-1]['hash'] if i else '0'*64)
                   and e['hash']==hash_event({k:v for k,v in e.items() if k!='hash'}) for i,e in enumerate(self.ledger))
    def dependent_closure(self,seeds):
        impacted=set(seeds)
        if not impacted<=self.nodes:raise ValueError('unknown node')
        while True:
            new=impacted|{n for n,ds in self.dependencies.items() if ds&impacted}
            if new==impacted:return frozenset(impacted)
            impacted=new
    def available_witnesses(self):
        return frozenset(w.name for w in self.witnesses if w.host in self.verified and w.host not in self.broken)
    def status(self):
        if self.broken:return 'HOLD_UPSTREAM_OR_NODE_FAILURE'
        if self.verified!=self.nodes or len(self.available_witnesses())!=3:return 'HOLD_UNVERIFIED_INFRASTRUCTURE'
        if set(self.receipts)!={w.name for w in self.witnesses}:return 'HOLD_FRESH_ATTESTATIONS'
        return 'LOCAL_DECLARED_QUORUM_ACCEPTED'
    def fail(self,node):
        if node not in self.nodes or node in self.broken:raise ValueError('invalid fail')
        affected=self.dependent_closure({node})
        self.broken.update(affected);self.verified.difference_update(affected);self.receipts.clear()
        self.append('fail',{'origin':node,'cascade':sorted(affected)})
    def repair(self,node):
        if node not in self.broken:raise ValueError('not failed')
        if not self.dependencies[node]<=self.verified:raise ValueError('unverified upstream')
        self.broken.remove(node);self.append('repair',{'node':node})
    def verify(self,node,evidence_id):
        if node not in self.nodes or node in self.broken or node in self.verified:raise ValueError('cannot verify')
        if not self.dependencies[node]<=self.verified:raise ValueError('upstream not verified')
        if not isinstance(evidence_id,str) or not evidence_id:raise ValueError('missing evidence')
        self.verified.add(node);self.append('verify',{'node':node,'evidence_id':evidence_id})
    def attest(self,witness,receipt_id):
        if witness not in {w.name for w in self.witnesses}:raise ValueError('unknown witness')
        if self.broken or self.verified!=self.nodes or len(self.available_witnesses())!=3:raise ValueError('infrastructure hold')
        if witness in self.receipts or not isinstance(receipt_id,str) or not receipt_id or receipt_id in self.receipts.values():
            raise ValueError('invalid or duplicate receipt')
        self.receipts[witness]=receipt_id;self.append('attest',{'witness':witness,'receipt_id':receipt_id})

def demo():
    graph={'power-y':(), 'network-x':('power-y',), 'router-a':('network-x',),
           'router-b':('network-x',),'power-z':(), 'router-c':('power-z',)}
    a=RecoveryGate((Witness('W1','A','opA','fdA','router-a'),Witness('W2','B','opB','fdB','router-b'),
                    Witness('W3','C','opC','fdC','router-c')),graph)
    a.fail('power-y');hold=a.status()
    for n in ('power-y','network-x','router-a','router-b'):
        a.repair(n);a.verify(n,'inspection-'+n)
    hold_fresh=a.status()
    for name in ('W1','W2','W3'):a.attest(name,'fresh-'+name)
    return a,{'failure_hold':hold,'pre_attestation':hold_fresh,'final':a.status(),
              'records':len(a.ledger),'valid':a.audit_ok()}
if __name__=='__main__':print(json.dumps(demo()[1],indent=2))
