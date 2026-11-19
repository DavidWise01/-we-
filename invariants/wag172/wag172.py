from fractions import Fraction as F
from math import sqrt
# Two identical five-site banks, indexed by radial rank.
# Opposite parity channels are mixed into a symmetric/antisymmetric pair.
C,S=F(3,5),F(4,5)
def mix(x,i,j,sign=1):
    a,b=x[i],x[j]; x[i]=C*a-sign*S*b; x[j]=sign*S*a+C*b

def step(x,reverse=False):
    # Bright channel propagates; dark channel is left invariant.
    # Basis change is an orthogonal rational coupler.
    y=list(x)
    for i in range(5): mix(y,i,i+5)
    edges=[(0,1),(2,3),(1,2),(3,4)]
    for i,j in (reversed(edges) if reverse else edges): mix(y,i,j,-1 if reverse else 1)
    for i in range(5): mix(y,i,i+5,-1)
    return tuple(y)

def norm(x):return sum(a*a for a in x)
def dark():return (S,0,0,0,0,C,0,0,0,0)
def bright():return (C,0,0,0,0,-S,0,0,0,0)
def single():return (F(1),)+(F(0),)*9

def run():
    for name,initial in [('dark',dark()),('bright',bright()),('single',single())]:
        x=tuple(map(F,initial)); assert norm(x)==1
        for n in range(173):
            if n in (0,1,4,19,172):print(name,n,float(x[0]**2+x[5]**2),sum(v!=0 for v in x))
            if n==172:break
            y=step(x);assert norm(y)==1 and step(y,True)==x;x=y
            if name=='dark':assert x==initial
        for _ in range(172):x=step(x,True)
        assert x==initial
    print('PASS: 516 forward/inverse checks; 3 full rewinds; exact dark-state persistence')
if __name__=='__main__':run()
