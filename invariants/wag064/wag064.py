"""WAG-064: Three-witness routing through a singular topological transition.
Synthetic graph model: ancestry labels are declared, not authenticated.
"""
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json

def digest(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

@dataclass(frozen=True)
class Witness:
    name: str
    ancestor: str
    domain: str

class RoutingGate:
    def __init__(self,witnesses):
        self.witnesses=tuple(witnesses)
        if (len(self.witnesses)!=3 or any(not isinstance(w,Witness) for w in self.witnesses)
            or any(not all((w.name,w.ancestor,w.domain)) for w in self.witnesses)
            or any(len(set(getattr(w,k) for w in self.witnesses))!=3 for k in ('name','ancestor','domain'))):
            raise ValueError('three distinct declared witnesses required')
        self.names=frozenset(w.name for w in self.witnesses)
        self.edges=set(frozenset(p) for p in combinations(self.names,2))
        self.frozen_edges=frozenset(self.edges)
        self.phase='PRE_PINCH';self.attestations={};self.events=[]
        self._append('genesis',{'witnesses':[vars(w) for w in self.witnesses],
                                'edges':self._serialize(self.edges)})
    @staticmethod
    def _serialize(edges):return sorted(sorted(e) for e in edges)
    def _append(self,kind,data):
        rec={'seq':len(self.events),'prev':self.events[-1]['hash'] if self.events else '0'*64,'kind':kind,'data':data}
        rec['hash']=digest(rec);self.events.append(rec)
    def verify(self):
        return all(r['seq']==i and r['prev']==(self.events[i-1]['hash'] if i else '0'*64)
                   and r['hash']==digest({k:v for k,v in r.items() if k!='hash'}) for i,r in enumerate(self.events))
    def connected(self):
        pending=[next(iter(self.names))];seen=set()
        while pending:
            x=pending.pop()
            if x in seen:continue
            seen.add(x)
            pending.extend(y for e in self.edges if x in e for y in e if y not in seen)
        return seen==self.names
    def pinch(self,broken_edges):
        if self.phase!='PRE_PINCH':raise ValueError('phase')
        removed=[frozenset(e) for e in broken_edges]
        if not removed or len(removed)!=len(set(removed)) or any(len(e)!=2 or e not in self.edges for e in removed):
            raise ValueError('invalid cut')
        self.edges.difference_update(removed);self.phase='SINGULAR'
        self._append('pinch',{'broken':self._serialize(removed),'remaining':self._serialize(self.edges),'connected':self.connected()})
        return {'phase':self.phase,'connected':self.connected(),'trust':'HOLD_SINGULAR'}
    def repair(self,edges):
        if self.phase!='SINGULAR':raise ValueError('phase')
        additions=[frozenset(e) for e in edges]
        if len(additions)!=len(set(additions)) or any(len(e)!=2 or not e.issubset(self.names) for e in additions):
            raise ValueError('invalid repair')
        joined=self.edges.union(additions)
        if frozenset(joined)!=self.frozen_edges:raise ValueError('original paths not restored')
        self.edges=joined;self.phase='RECONSTRUCTED'
        self._append('repair',{'edges':self._serialize(self.edges),'connected':self.connected()})
        return 'HOLD_FRESH_QUORUM'
    def attest(self,who,observed_edges,packet):
        if self.phase!='RECONSTRUCTED' or who not in self.names or who in self.attestations or not packet:raise ValueError('bad attestation')
        reported=frozenset(frozenset(e) for e in observed_edges)
        if any(len(e)!=2 or not e.issubset(self.names) for e in reported) or reported!=frozenset(self.edges):
            raise ValueError('conflicting observation')
        if packet in (x['packet'] for x in self.attestations.values()):raise ValueError('packet reused')
        self.attestations[who]={'packet':packet,'hash':digest(self._serialize(reported))}
        self._append('attest',{'who':who,'packet':packet,'graph_hash':self.attestations[who]['hash']})
    def certify(self):
        if self.phase!='RECONSTRUCTED':raise ValueError('phase')
        if not self.connected() or frozenset(self.edges)!=self.frozen_edges or set(self.attestations)!=self.names:
            return 'HOLD_QUORUM_OR_PATH'
        self.phase='RECERTIFIED'
        self._append('certify',{'witnesses':sorted(self.attestations),'edges':self._serialize(self.edges)})
        return 'RECERTIFIED_DECLARED_WITNESSES'

def demonstration():
    g=RoutingGate([Witness('W1','rootA','domainA'),Witness('W2','rootB','domainB'),Witness('W3','rootC','domainC')])
    original=[list(e) for e in g.frozen_edges]
    g.pinch([('W1','W2'),('W1','W3')])
    g.repair([('W1','W2'),('W1','W3')])
    for i in range(1,4):g.attest(f'W{i}',original,f'fresh-{i}')
    return g,g.certify()

if __name__=='__main__':
    g,result=demonstration()
    print({'decision':result,'phase':g.phase,'records':len(g.events),'verified':g.verify()})
