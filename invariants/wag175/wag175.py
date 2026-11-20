from fractions import Fraction as F
E=((0,1),(2,3),(1,2),(3,4))
# Integer numerators, common denominator: exact arithmetic without fraction churn.
D=625*401

def step(x,sign,reverse=False):
    y=list(x)
    def bright(s,edges):
        for i,j in edges:
            a,b=y[i],y[j]
            y[:]=[5*v for v in y]
            y[i],y[j]=3*a-s*4*b,s*4*a+3*b
    def gap(s):
        for i in range(5):
            a,b=y[i],y[i+5]
            y[i],y[i+5]=399*a-s*40*b,s*40*a+399*b
    if reverse: gap(-sign); bright(-1,E[::-1])
    else: bright(1,E); gap(sign)
    return tuple(y)

def run(n=360):
    initial=(0,0,0,0,0,1,0,0,0,0)
    print('interval,phase,mean,min,final')
    for h in (1,2,3,5,8,13,21,34,55,360):
        for phase in (1,-1):
            x=initial; den=1; vals=[1.0]
            for k in range(n):
                sign=phase*(-1)**(k//h)
                y=step(x,sign); den*=D
                assert sum(v*v for v in y)==den*den
                assert step(y,sign,True)==tuple(v*D*D for v in x)
                x=y; vals.append(float(F(x[0]**2+x[5]**2,den*den)))
            for k in reversed(range(n)):
                y=step(x,phase*(-1)**(k//h),True)
                assert all(v%(D*D)==0 for v in y)
                x=tuple(v//(D*D) for v in y)
            assert x==initial
            print(f'{h},{phase},{sum(vals)/len(vals):.9f},{min(vals):.9f},{vals[-1]:.9f}')
    print('PASS: 7200 exact norm/inverse checks; 20 full rewinds')
if __name__=='__main__':run()
