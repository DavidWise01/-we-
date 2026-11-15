"""WAG-062: witnesses, deformable surface, and topology bookkeeping.
A geometric reference, not a physical gravity model or Byzantine consensus protocol.
"""
from dataclasses import dataclass
from math import pi,cos,sin,isclose
from hashlib import sha256
import json

@dataclass(frozen=True)
class Witness:
    identity: str
    ancestor: str
    angle: float

@dataclass(frozen=True)
class Surface:
    a: float
    b: float
    c: float
    genus: int

class GeometricGate:
    def __init__(self, witnesses):
        self.witnesses=tuple(witnesses)
        if len(self.witnesses)!=3 or len({w.identity for w in self.witnesses})!=3:
            raise ValueError('exactly three witness identities required')
        if len({w.ancestor for w in self.witnesses})!=3:
            raise ValueError('shared declared ancestry')
        angles=sorted(w.angle%(2*pi) for w in self.witnesses)
        gaps=[(angles[(i+1)%3]-angles[i])%(2*pi) for i in range(3)]
        if not all(isclose(g,2*pi/3,abs_tol=1e-10) for g in gaps):
            raise ValueError('witness ring is not equally spaced')
        self.history=[]
        self._append('genesis',{'witnesses':[w.__dict__ for w in self.witnesses]})
    def _append(self,kind,data):
        prev=self.history[-1]['hash'] if self.history else '0'*64
        event={'seq':len(self.history),'previous':prev,'kind':kind,'data':data}
        event['hash']=sha256(json.dumps(event,sort_keys=True).encode()).hexdigest()
        self.history.append(event)
    def verify(self):
        return all(row['seq']==i and row['previous']==(self.history[i-1]['hash'] if i else '0'*64)
          and row['hash']==sha256(json.dumps({k:v for k,v in row.items() if k!='hash'},sort_keys=True).encode()).hexdigest()
          for i,row in enumerate(self.history))
    def deform(self,surface):
        if not isinstance(surface,Surface) or min(surface.a,surface.b,surface.c)<=0 or surface.genus not in (0,1):
            raise ValueError('invalid surface')
        coords=[(surface.a*cos(w.angle),surface.b*sin(w.angle),0) for w in self.witnesses]
        self._append('deform',{'axes':(surface.a,surface.b,surface.c),'genus':surface.genus,'coordinates':coords})
        return {'shape':'sphere' if isclose(surface.a,surface.b) and isclose(surface.b,surface.c) else 'spheroid' if isclose(surface.a,surface.b) or isclose(surface.b,surface.c) or isclose(surface.a,surface.c) else 'triaxial ellipsoid',
                'topology':'torus' if surface.genus==1 else 'sphere-like',
                'witnesses':coords}

def demo():
    ws=[Witness(f'W{i}',f'root{i}',2*pi*i/3) for i in range(3)]
    gate=GeometricGate(ws)
    torus=gate.deform(Surface(2,2,1,1))
    ellipsoid=gate.deform(Surface(3,2,1,0))
    sphere=gate.deform(Surface(2,2,2,0))
    return gate,(torus,ellipsoid,sphere)
if __name__=='__main__':
    gate,states=demo()
    print(json.dumps({'states':[{'shape':s['shape'],'topology':s['topology']} for s in states], 'audit_valid':gate.verify(),'records':len(gate.history)},indent=2))