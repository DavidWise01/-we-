"""WAG-063 — formal torus-to-spheroid topology surgery; not physical gravity."""
from dataclasses import dataclass
from math import isfinite
from hashlib import sha256
import json

def digest(x): return sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

@dataclass(frozen=True)
class Witness:
    ident: str
    ancestry: str
    angle: float

@dataclass(frozen=True)
class Stage:
    tick: int
    pinch: float
    hole_radius: float
    genus: int | None
    state: str
    witnesses: tuple

class PinchAudit:
    def __init__(self,witnesses,outer_radius=2.0,hole_radius=1.0):
        self.witnesses=tuple(witnesses)
        if len(self.witnesses)!=3 or not all(isinstance(w,Witness) and w.ident and w.ancestry and isfinite(w.angle) for w in self.witnesses):
            raise ValueError("three finite witnesses required")
        if len({w.ident for w in self.witnesses})!=3 or len({w.ancestry for w in self.witnesses})!=3:raise ValueError("duplicate identity or ancestry")
        a=sorted(w.angle%360 for w in self.witnesses)
        if any(abs((a[(i+1)%3]-a[i])%360-120)>1e-7 for i in range(3)):raise ValueError("not 120 degrees")
        if not all(isfinite(v) and v>0 for v in (outer_radius,hole_radius)):raise ValueError("radius")
        self.outer_radius=outer_radius;self.initial_hole=hole_radius
        self.stages=[];self.ledger=[]
        self._append("genesis",{"witnesses":[vars(w) for w in self.witnesses],"outer_radius":outer_radius,"hole_radius":hole_radius})
    def _append(self,kind,data):
        e={"seq":len(self.ledger),"previous":self.ledger[-1]["hash"] if self.ledger else "0"*64,"kind":kind,"data":data}
        e["hash"]=digest(e);self.ledger.append(e)
    def verify(self):
        return all(e["seq"]==i and e["previous"]==(self.ledger[i-1]["hash"] if i else "0"*64) and e["hash"]==digest({k:v for k,v in e.items() if k!="hash"}) for i,e in enumerate(self.ledger))
    def step(self,pinch):
        if isinstance(pinch,bool) or not isinstance(pinch,(int,float)) or not isfinite(pinch) or not 0<=pinch<=1:raise ValueError("pinch")
        if self.stages and pinch<=self.stages[-1].pinch:raise ValueError("nonmonotonic")
        stage=Stage(len(self.stages),float(pinch),self.initial_hole*(1-pinch),1 if pinch<1 else None,"TORUS" if pinch<1 else "SINGULAR_PINCH",self.witnesses)
        self.stages.append(stage);self._append("pinch",{"pinch":stage.pinch,"hole_radius":stage.hole_radius,"genus":stage.genus,"state":stage.state})
        return stage
    def close(self):
        if not self.stages or self.stages[-1].state!="SINGULAR_PINCH":raise ValueError("pinch before surgery")
        stage=Stage(len(self.stages),1.0,0.0,0,"SPHEROID_AFTER_SURGERY",self.witnesses)
        self.stages.append(stage);self._append("surgery",{"from":"SINGULAR_PINCH","to":stage.state,"genus_before":1,"genus_after":0,"ancestry":[w.ancestry for w in self.witnesses]})
        return stage
    def ancestry_preserved(self):return all(s.witnesses==self.witnesses for s in self.stages)

def demo():
    a=PinchAudit((Witness("W1","root-A",0),Witness("W2","root-B",120),Witness("W3","root-C",240)))
    for p in (0,.25,.5,.75,1):a.step(p)
    a.close();return a

if __name__=="__main__":
    a=demo();print({"states":[s.state for s in a.stages],"genus":[s.genus for s in a.stages],"records":len(a.ledger),"verified":a.verify(),"ancestors_retained":a.ancestry_preserved()})
