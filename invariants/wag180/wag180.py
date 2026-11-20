from random import Random
D=625*401
E=((0,1),(2,3),(1,2),(3,4))
def bright(x,rev=False):
    y=list(x); s=-1 if rev else 1
    for i,j in (E[::-1] if rev else E):
        a,b=y[i],y[j]; y=[5*v for v in y]; y[i],y[j]=3*a-s*4*b,s*4*a+3*b
    return tuple(y)
def gap(x,signs,rev=False):
    y=list(x)
    for i,s in enumerate(signs):
        if rev:s=-s
        a,b=y[i],y[i+5]; y[i],y[i+5]=399*a-s*40*b,s*40*a+399*b
    return tuple(y)
def choose(b,old,older,prev,policy,k):
    if policy=='echo':return ((-1)**k,)*5,0
    signs=[]; accepted=0
    for i in range(5):
        j=i+5; use=policy=='half' and old is not None
        if policy=='confidence' and older is not None:
            u=(b[i]-D*old[i],b[j]-D*old[j]); v=(D*old[i]-D*D*older[i],D*old[j]-D*D*older[j])
            dot=sum(a*c for a,c in zip(u,v)); nu=sum(a*a for a in u); nv=sum(a*a for a in v)
            use=dot>0 and 4*dot*dot>=nu*nv and nu<=4*nv and nv<=4*nu
        a,c=(3*b[i]-D*old[i],3*b[j]-D*old[j]) if use else (b[i],b[j]); accepted+=use
        signs.append(1 if a*c>0 else -1 if a*c<0 else -prev[i])
    return tuple(signs),accepted

def fixtures():
    rng=Random(180)
    for k in range(12):
        r=k%5; x=[rng.randint(-2,2) for _ in range(10)]; x[r]+=6; x[r+5]+=8
        yield k,r,tuple(x)
def run():
    print('fixture,policy,mean,min,final,derivative_uses')
    rows=[]
    for k,r,seed in fixtures():
        for policy in ('echo','local','half','confidence'):
            x=seed; den=sum(v*v for v in x); vals=[(x[r]**2+x[r+5]**2)/den]; history=[]; prev=(-1,)*5; old=older=None; uses=0
            for n in range(180):
                b=bright(x); signs,u=choose(b,old,older,prev,policy,n); uses+=u; y=gap(b,signs); den*=D*D
                assert sum(v*v for v in y)==den
                assert bright(gap(y,signs,True),True)==tuple(v*D*D for v in x)
                x=y; older,old=old,b; history.append(signs); prev=signs; vals.append((x[r]**2+x[r+5]**2)/den)
            for signs in reversed(history):
                y=bright(gap(x,signs,True),True); assert all(v%(D*D)==0 for v in y); x=tuple(v//(D*D) for v in y)
            assert x==seed
            row=(k,policy,sum(vals)/len(vals),min(vals),vals[-1],uses); rows.append(row)
            print(f'{k},{policy},{row[2]:.9f},{row[3]:.9f},{row[4]:.9f},{uses}')
    print('SUMMARY policy,mean,average_min,final,uses,wins_vs_echo')
    for p in ('echo','local','half','confidence'):
        a=[r for r in rows if r[1]==p]; e=[r for r in rows if r[1]=='echo']; print(p,*[round(sum(r[j] for r in a)/len(a),6) for j in (2,3,4)],sum(r[5] for r in a),sum(r[2]>s[2] for r,s in zip(a,e)))
    print('PASS: 8640 exact norm/inverse checks; 48 amplitude rewinds')
if __name__=='__main__':run()
