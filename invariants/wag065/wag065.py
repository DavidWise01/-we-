"""WAG-065 edge cut auditor. Connectivity is not Byzantine consensus."""
from dataclasses import dataclass
from itertools import combinations
from hashlib import sha256
import json

def H(x): return sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
@dataclass(frozen=True)
class Witness:
    name:str
    root:str
class CutAudit:
    def __init__(self,ws):
        self.ws=tuple(ws)
        if len(self.ws)!=3 or len({w.name for w in ws})!=3 or len({w.root for w in ws})!=3 or any(not w.name or not w.root for w in ws):raise ValueError('witness ancestry')
        self.vertices={w.name for w in ws}
        self.full={frozenset(p) for p in combinations(self.vertices,2)}
        self.edges=set(self.full);self.events=[]
        self.append('genesis',{'roots':[(w.name,w.root) for w in self.ws]})
    def append(self,kind,data):
        event={'n':len(self.events),'previous':self.events[-1]['hash'] if self.events else '0'*64,'kind':kind,'data':data}
        event['hash']=H(event);self.events.append(event)
    def verify(self):
        return all(e['n']==i and e['previous']==(self.events[i-1]['hash'] if i else '0'*64) and e['hash']==H({k:v for k,v in e.items() if k!='hash'}) for i,e in enumerate(self.events))
    def edge(self,a,b):
        if a==b or frozenset((a,b)) not in self.full:raise ValueError('invalid edge')
        return frozenset((a,b))
    def cut(self,a,b):
        edge=self.edge(a,b)
        if edge not in self.edges:raise ValueError('already cut')
        self.edges.remove(edge);self.append('cut',sorted(edge))
    def repair(self,a,b):
        edge=self.edge(a,b)
        if edge in self.edges:raise ValueError('already present')
        self.edges.add(edge);self.append('repair',sorted(edge))
    def connected(self,edges=None):
        edges=self.edges if edges is None else edges
        seen={next(iter(self.vertices))}
        while True:
            grown=seen|{v for e in edges if e & seen for v in e}
            if grown==seen:return seen==self.vertices
            seen=grown
    def minimum_edge_cut(self):
        for k in range(len(self.full)+1):
            for missing in combinations(self.full,k):
                if not self.connected(self.full.difference(missing)):return k
        raise RuntimeError('no cut')
    def paths(self,a,b):
        self.edge(a,b);found=[]
        def walk(cur,path):
            if cur==b:found.append(tuple(path));return
            for e in self.edges:
                if cur in e:
                    nxt=next(iter(e-{cur}))
                    if nxt not in path:walk(nxt,path+[nxt])
        walk(a,[a]);return sorted(found,key=lambda p:(len(p),p))
    def state(self):
        return 'CONNECTED_REDUNDANT' if len(self.edges)==3 else ('CONNECTED_DEGRADED' if self.connected() else 'HOLD_DISCONNECTED')
def demo():
    a=CutAudit([Witness('W1','A'),Witness('W2','B'),Witness('W3','C')]);states=[a.state()]
    a.cut('W1','W2');states.append(a.state())
    a.cut('W1','W3');states.append(a.state())
    a.repair('W1','W2');states.append(a.state())
    a.repair('W1','W3');states.append(a.state())
    return a,states
if __name__=='__main__':
    a,states=demo();print({'states':states,'min_edge_cut':a.minimum_edge_cut(),'records':len(a.events),'valid':a.verify()})
