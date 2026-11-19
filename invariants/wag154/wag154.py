from fractions import Fraction as F
from dataclasses import dataclass

@dataclass(frozen=True)
class Ledger:
    external: F = F(540)
    reserve: F = F(0)
    dissipated: F = F(0)
    def total(self): return self.external+self.reserve+self.dissipated

def step(s,ad,absorb=F(2)):
    if min(s.external,s.reserve,s.dissipated,absorb)<0 or type(ad)!=int or not 0<=ad<360:
        raise ValueError('invalid state')
    g=F(1,2)+F(min(ad,360-ad),360)
    incoming=min(s.external,absorb)
    available=s.reserve+incoming
    gross=min(2*g,available)
    out=Ledger(s.external-incoming,available-gross,s.dissipated+gross)
    assert out.total()==s.total()
    return out,incoming,gross/2,gross/2

if __name__=='__main__':
    s=Ledger()
    for n in range(361):
        if n in (0,90,180,270,360): print(n,*(str(v) for v in (s.external,s.reserve,s.dissipated)))
        if n<360: s,*_=step(s,n%360)
