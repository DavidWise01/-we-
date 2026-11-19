from fractions import Fraction as F
N=(-1,-2,-3,-4,-5,5,4,3,2,1)

def step(x,b,e,d,ad):
    x,b=list(map(F,x)),list(map(F,b)); e,d=F(e),F(d)
    assert len(x)==len(b)==10 and min(*x,*b,e,d)>=0 and sum(x)==20
    g=F(1,2)+F(min(ad,360-ad),360)
    incoming=min(e,2); e-=incoming; b[5]+=incoming
    old=b[:]
    for i in range(10):
        j=(i+1)%10; f=(old[i]-old[j])/8; b[i]-=f;b[j]+=f
    y=x[:]; modes=[]
    # Pairwise transfer only from surplus to deficit; source pays.
    for i in range(10):
        surplus=max(F(0),x[i]-2)
        neighbors=[j for j in ((i-1)%10,(i+1)%10) if x[j]<2]
        if not surplus or not neighbors or not b[i]: modes.append('hide');continue
        mode='fight' if b[i]>=g*surplus/10 else 'flight'
        modes.append(mode)
        for j in neighbors:
            f=min(b[i],g*surplus/20,max(F(0),y[i]-2),max(F(0),2-y[j]))
            y[i]-=f;y[j]+=f;b[i]-=f;d+=f
    return y,b,e,d,modes

def run():
    x=[F(8 if n==-5 else 12 if n==5 else 0) for n in N]; b=[F(0)]*10;e=F(540);d=F(0)
    for a in range(360):
        before=sum((v-2)**2 for v in x)
        x,b,e,d,m=step(x,b,e,d,a)
        assert sum(x)==20 and sum(b)+e+d==540 and min(*x,*b,e,d)>=0
        assert sum((v-2)**2 for v in x)<=before
    print('360 updates: inventory=26; resources=540; max residual=',float(max(abs(v-2) for v in x)))
    print('external, local, dissipated:',float(e),float(sum(b)),float(d))
    # Uniform inventory must remain uniform despite asymmetric resource custody.
    x,b,e,d,m=step([2]*10,[0]*9+[10],0,0,180)
    assert x==[2]*10 and d==0 and set(m)=={'hide'}
    print('PASS: asymmetric custody preserves equilibrium')
    # A surplus with no adjacent deficit is stranded under this policy.
    x=[3,2,1,2,2,2,2,2,2,2]
    y,*_=step(x,[10]*10,0,0,180)
    assert y==x
    print('PASS: stranded surplus counterexample reproduced')
if __name__=='__main__':run()
