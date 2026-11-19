from fractions import Fraction as F
from dataclasses import dataclass
N=(-1,-2,-3,-4,-5,5,4,3,2,1)
@dataclass(frozen=True)
class State:
    x: tuple
    b: tuple
    external: F
    spent: F

def initial():
    return State(tuple(F(8 if n==-5 else 12 if n==5 else 0) for n in N),(F(0),)*10,F(540),F(0))

def step(s,ad,absorb=F(2)):
    if len(s.x)!=10 or len(s.b)!=10 or min(*s.x,*s.b,s.external,s.spent,absorb)<0 or sum(s.x)!=20 or not 0<=ad<360 or type(ad)!=int: raise ValueError('state')
    g=F(1,2)+F(min(ad,360-ad),360)
    b=list(s.b); x=list(s.x)
    incoming=min(s.external,absorb); b[5]+=incoming
    # Simultaneous reserve diffusion on the ring, separate from inventory.
    old=b[:]
    for i in range(10):
        j=(i+1)%10; f=(old[i]-old[j])/8; b[i]-=f; b[j]+=f
    # Each source pays for its two outgoing inventory transfers.
    spent=F(0)
    for i in range(10):
        gross=min(b[i],g*s.x[i]/10); b[i]-=gross; spent+=gross
        x[i]-=gross; x[(i-1)%10]+=gross/2; x[(i+1)%10]+=gross/2
    return State(tuple(x),tuple(b),s.external-incoming,s.spent+spent)

def run():
    s=initial()
    for n in range(361):
        if n in (0,30,90,180,270,360): print(n, float(s.external),float(sum(s.b)),float(s.spent),float(max(abs(v-2) for v in s.x)))
        if n==360:break
        s=step(s,n%360)
        assert sum(s.x)==20 and sum(s.b)+s.external+s.spent==540 and min(*s.x,*s.b)>=0
if __name__=='__main__':run()
