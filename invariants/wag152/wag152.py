from fractions import Fraction as F

N=(-5,-4,-3,-2,-1,1,2,3,4,5)
C=(-1,-2,-3,-4,-5,5,4,3,2,1)
EDGES=tuple((-r,r) for r in range(1,6))+tuple((s*r,s*(r+1)) for s in (-1,1) for r in range(1,5))

def step(x,ad):
    if set(x)!=set(N) or min(x.values())<0 or sum(x.values())!=20 or type(ad)!=int or not 0<=ad<360: raise ValueError('state')
    g=F(1,2)+F(min(ad,360-ad),360)
    y=x.copy(); flux=[]
    for a,b in EDGES:
        f=g*F(min(abs(a),abs(b)),40)*(x[a]-x[b]); y[a]-=f; y[b]+=f
    for a,b in zip(C,C[1:]+C[:1]):
        f=g*x[a]/10; y[a]-=f; y[b]+=f; flux.append(f)
    return y,tuple(flux)

def error(x):return sum((v-2)**2 for v in x.values())

def run():
    x={a:F(8 if a==-5 else 12 if a==5 else 0) for a in N}
    equilibrium={a:F(2) for a in N}
    for ad in range(360):
        y,f=step(equilibrium,ad)
        assert y==equilibrium and sum(f)==2*(F(1,2)+F(min(ad,360-ad),360)) and min(f)>0
    for i in range(361):
        if i in (0,1,30,90,180,360):print(i,float(max(abs(v-2) for v in x.values())),float(error(x)))
        if i==360:break
        y,f=step(x,i%360)
        assert sum(y.values())==20 and min(y.values())>=0 and error(y)<=error(x)
        x=y
    print('PASS: 360 disturbed updates; 360 equilibrium phase checks; center=6; total=26')

if __name__=='__main__':run()
