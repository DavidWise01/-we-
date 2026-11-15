"""WAG-066: vertex connectivity and three-witness quorum; synthetic reference."""
from dataclasses import dataclass
from itertools import combinations
from hashlib import sha256
import json
def digest(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
@dataclass(frozen=True)
class Witness:
    name:str
    ancestor:str
    operator:str
    failure_domain:str
class VertexQuorumAudit:
    def __init__(self,witnesses,quorum=3):
        self.witnesses=tuple(witnesses)
        if len(self.witnesses)!=3 or quorum!=3:raise ValueError('three witnesses required')
        for field in ('name','ancestor','operator','failure_domain'):
            vals=[getattr(w,field) for w in self.witnesses]
            if len(vals)!=len(set(vals)) or any(not isinstance(v,str) or not v for v in vals):raise ValueError('declared provenance')
        self.names=frozenset(w.name for w in self.witnesses);self.alive=set(self.names)
        self.edges={frozenset(e) for e in combinations(sorted(self.names),2)}
        self.ledger=[];self._append('genesis',{'witnesses':[vars(w) for w in self.witnesses],'quorum':quorum})
    def _append(self,event,data):
        r={'seq':len(self.ledger),'prior':self.ledger[-1]['hash'] if self.ledger else '0'*64,'event':event,'data':data}
        r['hash']=digest(r);self.ledger.append(r)
    def verify_ledger(self):
        return all(r['seq']==i and r['prior']==(self.ledger[i-1]['hash'] if i else '0'*64)
                   and r['hash']==digest({k:v for k,v in r.items() if k!='hash'}) for i,r in enumerate(self.ledger))
    def connected(self,survivors=None):
        nodes=self.alive if survivors is None else set(survivors)
        if not nodes or not nodes.issubset(self.names):return False
        seen={min(nodes)}
        while True:
            more=seen|{v for edge in self.edges if edge.issubset(nodes) and edge&seen for v in edge}
            if more==seen:return seen==nodes
            seen=more
    def vertex_connectivity(self):
        for size in range(1,len(self.names)):
            for removed in combinations(sorted(self.names),size):
                remains=self.names.difference(removed)
                if len(remains)<=1 or not self.connected(remains):return size
        return len(self.names)-1
    def fail(self,name):
        if name not in self.alive:raise ValueError('unknown or failed')
        self.alive.remove(name);self._append('fail',{'name':name,'state':self.status()})
    def restore(self,name):
        if name not in self.names or name in self.alive:raise ValueError('unknown or live')
        self.alive.add(name);self._append('restore',{'name':name,'state':self.status()})
    def status(self):
        if len(self.alive)<3:return 'HOLD_QUORUM_LOSS'
        if not self.connected():return 'HOLD_DISCONNECTED'
        return 'ELIGIBLE_FOR_FRESH_ATTESTATION'
    def certify(self,attestations):
        if self.status()!='ELIGIBLE_FOR_FRESH_ATTESTATION':raise ValueError('quorum')
        if not isinstance(attestations,dict) or set(attestations)!=self.alive:raise ValueError('missing attestation')
        ids=list(attestations.values())
        if any(not isinstance(x,str) or not x for x in ids) or len(set(ids))!=3:raise ValueError('replayed attestation')
        self._append('attest',{'witnesses':sorted(self.alive),'receipt_ids':sorted(ids)})
        return 'LOCAL_DECLARED_QUORUM_ACCEPTED'
def demonstration():
    a=VertexQuorumAudit((Witness('W1','A','opA','fdA'),Witness('W2','B','opB','fdB'),Witness('W3','C','opC','fdC')))
    first=a.status();a.fail('W1');lost={'status':a.status(),'connected_survivors':a.connected(),'count':len(a.alive)}
    a.restore('W1');restored=a.status()
    accepted=a.certify({'W1':'fresh-a','W2':'fresh-b','W3':'fresh-c'})
    return a,{'initial':first,'failure':lost,'restored':restored,'certified':accepted,'vertex_connectivity':a.vertex_connectivity(),'records':len(a.ledger),'verified':a.verify_ledger()}
if __name__=='__main__':
    print(json.dumps(demonstration()[1],indent=2))
