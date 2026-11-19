from fractions import Fraction as F
C,S=F(3,5),F(4,5)
R=tuple((i,9-i) for i in range(5))
L=tuple((i,i+1) for i in (0,2,5,7))
M=tuple((i,i+1) for i in (1,3,6,8))
def mix(x,edges,sign=1):
    y=list(x)
    for i,j in edges:
        a,b=y[i],y[j]
        y[i]=tuple(C*u-sign*S*v for u,v in zip(a,b))
        y[j]=tuple(sign*S*u+C*v for u,v in zip(a,b))
    return tuple(y)
def rot(x,sign):
    return tuple((-sign*(1 if i>=5 else -1)*b,sign*(1 if i>=5 else -1)*a) for i,(a,b) in enumerate(x))
def step(x,reverse=False):
    if reverse:return rot(mix(mix(mix(x,M,-1),L,-1),R,-1),-1)
    return mix(mix(mix(rot(x,1),R),L),M)
def norm(x):return sum(a*a+b*b for a,b in x)
def initial():return tuple((F(i==0),F(0)) for i in range(10))
def run():
    x=initial();start=x;seen={x}; repeats=0
    for n in range(1,172):
        y=step(x);assert norm(y)==1 and step(y,True)==x
        x=y;repeats+=x in seen;seen.add(x)
        if n in (1,2,4,9,19,171):print(n, sum(p!=(0,0) for p in x), float(norm(x[:5])),float(norm(x[5:])))
    assert repeats==0
    for _ in range(171):x=step(x,True)
    assert x==start
    for i in range(10):
        for j in range(2):
            x=tuple(tuple(F(k==i and l==j) for l in range(2)) for k in range(10))
            assert step(step(x),True)==x and norm(step(x))==1
    print('PASS: 171 steps, 171 inverse checks, 20 basis vectors, full rewind; no repeats in sampled orbit')
if __name__=='__main__':run()
