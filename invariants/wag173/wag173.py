from fractions import Fraction as F

EDGES=((0,1),(2,3),(1,2),(3,4))
def mix(x,i,j,c,s):
    a,b=x[i],x[j]; x[i]=c*a-s*b; x[j]=s*a+c*b

def step(x,t,reverse=False):
    y=list(x); c=(1-t*t)/(1+t*t); s=2*t/(1+t*t)
    if reverse:
        for i in range(5): mix(y,i,i+5,c,-s)
        for i,j in reversed(EDGES): mix(y,i,j,F(3,5),-F(4,5))
    else:
        for i,j in EDGES: mix(y,i,j,F(3,5),F(4,5))
        for i in range(5): mix(y,i,i+5,c,s)
    return tuple(y)

def norm(x): return sum(v*v for v in x)
def initial(): return (F(0),)*5+(F(1),)+(F(0),)*4

def run():
    for t in map(F,('0','1/100','1/20','1/5')):
        x=initial(); minimum=F(1); first=None
        for n in range(1,174):
            y=step(x,t); assert norm(y)==1 and step(y,t,True)==x
            x=y; local=x[0]**2+x[5]**2; minimum=min(minimum,local)
            if local<F(1,2) and first is None: first=n
            if n in (1,19,50,173): print(str(t),n,f'{float(local):.9f}',f'{float(norm(x[5:])):.9f}')
        print('minimum',f'{float(minimum):.9f}','first below half',first)
        for _ in range(173): x=step(x,t,True)
        assert x==initial()
    print('PASS: 692 exact norm and inverse checks; four complete rewinds')
if __name__=='__main__': run()
