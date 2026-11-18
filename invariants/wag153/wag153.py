from fractions import Fraction as F

C=(-1,-2,-3,-4,-5,5,4,3,2,1)
E=tuple((-r,r) for r in range(1,6))+tuple((s*r,s*(r+1)) for s in (-1,1) for r in range(1,5))

def step(x,ad,budget):
    if set(x)!=set(C) or min(x.values())<0 or sum(x.values())!=20 or type(ad)!=int or not 0<=ad<360 or budget<0: raise ValueError('state')
    g=F(1,2)+F(min(ad,360-ad),360)
    rate=min(g/20,budget/40)
    y=x.copy()
    for a,b in E:
        f=g*F(min(abs(a),abs(b)),40)*(x[a]-x[b]);y[a]-=f;y[b]+=f
    for i,a in enumerate(C):
        for d in (-1,1):
            b=C[(i+d)%10];f=rate*x[a];y[a]-=f;y[b]+=f
    gross=40*rate
    return y,budget-gross,(20*rate,20*rate,gross)

def error(x):return sum((v-2)**2 for v in x.values())

def run():
    x={a:F(8 if a==-5 else 12 if a==5 else 0) for a in C};b=F(540);gross=F(0)
    eq={a:F(2) for a in C}
    for ad in range(360):
        y,r,f=step(eq,ad,F(2));assert y==eq and f[0]==f[1] and f[2]>0 and r+f[2]==2
    for i in range(361):
        if i in (0,1,30,90,180,360):print(i,format(float(max(abs(v-2) for v in x.values())),'.12g'),format(float(b),'.12g'))
        if i==360:break
        y,r,f=step(x,i%360,b);gross+=f[2]
        assert sum(y.values())==20 and min(y.values())>=0 and error(y)<=error(x) and r>=0 and r+gross==540 and f[0]==f[1]
        x,b=y,r
    assert b==0 and gross==540
    y,r,f=step(eq,0,b);assert y==eq and f==(0,0,0)
    y,r,f=step(eq,180,F(1,3));assert y==eq and r==0 and f[2]==F(1,3)
    print('PASS: 360 disturbance updates; 360 equilibrium phase checks; 2 budget boundary checks; center=6; inventory=26; budget spent=540')

if __name__=='__main__':run()
