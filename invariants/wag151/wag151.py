from fractions import Fraction as F

NODES=tuple(range(-5,0))+tuple(range(1,6))
EDGES=tuple(( -r,r) for r in range(1,6))+tuple((s*r,s*(r+1)) for s in (-1,1) for r in range(1,5))

def step(x,ad):
    if set(x)!=set(NODES) or min(x.values())<0 or sum(x.values())!=20 or type(ad)!=int or not 0<=ad<360: raise ValueError('state')
    y=x.copy()
    # Exact triangular phase gate, bounded between 1/2 and 1.
    phase=F(1,2)+F(min(ad,360-ad),360)
    for a,b in EDGES:
        k=phase*F(min(abs(a),abs(b)),40)
        f=k*(x[a]-x[b]); y[a]-=f; y[b]+=f
    return y,(ad+1)%360

def error(x):return sum((v-2)**2 for v in x.values())

def run(n=360):
    x=dict(zip(NODES,map(F,[8,0,0,0,0,0,0,0,0,12])))
    ad=0; rows=[]
    for i in range(n+1):
        rows.append((i,ad,float(error(x)),float(max(abs(v-2) for v in x.values()))))
        if i==n:break
        y,a=step(x,ad)
        assert sum(y.values())==20 and min(y.values())>=0 and error(y)<=error(x)
        x,ad=y,a
    return rows

if __name__=='__main__':
    for row in run():
        if row[0] in (0,1,30,90,180,360):print(*row)
