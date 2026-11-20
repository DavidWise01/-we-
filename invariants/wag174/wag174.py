from fractions import Fraction as F
E=((0,1),(2,3),(1,2),(3,4))
def gap(ad,mode):
    if mode=='fixed': return F(1,20)
    if mode=='signed': return F(1,20) if ad%360<180 else -F(1,20)
    if mode=='echo': return F(1,20) if ad%2==0 else -F(1,20)
    if mode=='zero': return F(0)
    raise ValueError(mode)
def step(x,ad,mode,reverse=False):
    y=list(x); t=gap(ad,mode); c=(1-t*t)/(1+t*t); s=2*t/(1+t*t)
    def mix(i,j,c,s):
        a,b=y[i],y[j]; y[i],y[j]=c*a-s*b,s*a+c*b
    if reverse:
        for i in range(5):mix(i,i+5,c,-s)
        for i,j in reversed(E):mix(i,j,F(3,5),-F(4,5))
    else:
        for i,j in E:mix(i,j,F(3,5),F(4,5))
        for i in range(5):mix(i,i+5,c,s)
    return tuple(y)
def initial():return tuple(F(i==5) for i in range(10))
def norm(x):return sum(v*v for v in x)
def retention(x):return x[0]**2+x[5]**2
def run(n=360):
    for mode in ('zero','fixed','signed','echo'):
        x=initial(); values=[1.0]
        for k in range(n):
            y=step(x,k%360,mode);assert norm(y)==1 and step(y,k%360,mode,True)==x
            x=y;values.append(float(retention(x)))
        for k in reversed(range(n)):x=step(x,k%360,mode,True)
        assert x==initial()
        print(mode,'min', f'{min(values):.9f}','mean',f'{sum(values)/len(values):.9f}','final',f'{values[-1]:.9f}', 'samples',*[f'{values[i]:.9f}' for i in (19,90,174,180,270,360)])
    print('PASS: 1440 exact forward/inverse checks; four full rewinds')
if __name__=='__main__':run()
