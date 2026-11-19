from fractions import Fraction as F
from itertools import product
N=10
C,S=F(3,5),F(4,5)
def norm(x): return sum(v*v for p in x for v in p)
def rotate(p,k):
    a,b=p
    for _ in range(k%4): a,b=-b,a
    return a,b
def mix(x,i,j,sign=1):
    y=list(x); a,b=x[i],x[j]; s=sign*S
    y[i]=tuple(C*u-s*v for u,v in zip(a,b))
    y[j]=tuple(s*u+C*v for u,v in zip(a,b))
    return tuple(y)
def step(x,reverse=False):
    if reverse:
        for i in reversed(range(5)): x=mix(x,i,9-i,-1)
        return tuple(rotate(p,1 if i<5 else -1) for i,p in enumerate(x))
    x=tuple(rotate(p,-1 if i<5 else 1) for i,p in enumerate(x))
    for i in range(5): x=mix(x,i,9-i)
    return x
def run():
    x=tuple((F(1),F(0)) if i<5 else (F(0),F(0)) for i in range(10)); initial=x
    for n in range(1,171):
        y=step(x); assert norm(y)==5 and step(y,True)==x
        x=y
        if n in (1,2,5,10,170): print(n, float(norm(x[:5])),float(norm(x[5:])),norm(x))
    for _ in range(170): x=step(x,True)
    assert x==initial
    for mask in product((0,1),repeat=5):
        x=tuple((F(mask[i%5]),F(1-mask[i%5])) for i in range(10));assert step(step(x),True)==x and norm(step(x))==norm(x)
    print('PASS: 170 norm/inverse updates, full rewind, 32 configurations; fixed external fulcrum 0')
if __name__=='__main__':run()
