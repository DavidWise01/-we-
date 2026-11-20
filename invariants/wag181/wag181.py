from random import Random
D=625*401
E=((0,1),(2,3),(1,2),(3,4))
def bright(x,rev=False):
 y=list(x); s=-1 if rev else 1
 for i,j in (E[::-1] if rev else E):
  a,b=y[i],y[j]; y=[5*v for v in y]; y[i],y[j]=3*a-s*4*b,s*4*a+3*b
 return tuple(y)
def gap(x,ss,rev=False):
 y=list(x)
 for i,s in enumerate(ss):
  if rev:s=-s
  a,b=y[i],y[i+5]; y[i],y[i+5]=399*a-s*40*b,s*40*a+399*b
 return tuple(y)
def run():
 rng=Random(181); rows=[]
 for k in range(12):
  r=k%5; a=[rng.randint(-2,2) for _ in range(10)]; a[r]+=6; a[r+5]+=8; seed=tuple(a)
  for mode in ('echo','local','confidence','calibrated'):
   x=seed; den=sum(v*v for v in x); vals=[(x[r]**2+x[r+5]**2)/den]; old=older=None; prev=(-1,)*5; scores=[0]*5; history=[]; uses=0
   for n in range(181):
    b=bright(x); ss=[]
    for i in range(5):
     j=i+5; use=False
     if older is not None:
      u=[b[t]-D*old[t] for t in (i,j)]; v=[D*old[t]-D*D*older[t] for t in (i,j)]
      nu=sum(t*t for t in u); nv=sum(t*t for t in v); dot=sum(t*w for t,w in zip(u,v))
      if mode=='confidence':use=dot>0 and 4*dot*dot>=nu*nv and nu<=4*nv and nv<=4*nu
      if mode=='calibrated':
       # Compare previous half-derivative prediction with previous persistence prediction.
       err=sum((2*t-w)**2 for t,w in zip(u,v)); base=4*nu
       scores[i]=max(-4,min(4,scores[i]+(1 if err<base else -1 if err>base else 0)))
       use=scores[i]>=2 and dot>0
     uses+=use
     p,q=(3*b[i]-D*old[i],3*b[j]-D*old[j]) if use else (b[i],b[j])
     ss.append((-1)**n if mode=='echo' else 1 if p*q>0 else -1 if p*q<0 else -prev[i])
    y=gap(b,ss); den*=D*D
    assert sum(v*v for v in y)==den
    assert bright(gap(y,ss,True),True)==tuple(v*D*D for v in x)
    x=y; older,old=old,b; prev=tuple(ss); history.append(prev); vals.append((x[r]**2+x[r+5]**2)/den)
   for ss in reversed(history):
    y=bright(gap(x,ss,True),True); assert all(v%(D*D)==0 for v in y); x=tuple(v//(D*D) for v in y)
   assert x==seed
   rows.append((k,mode,sum(vals)/len(vals),min(vals),vals[-1],uses))
 print('fixture,policy,mean,min,final,uses')
 for row in rows:print('%d,%s,%.9f,%.9f,%.9f,%d'%row)
 for mode in ('echo','local','confidence','calibrated'):
  a=[r for r in rows if r[1]==mode]; print(mode,*[round(sum(r[j] for r in a)/len(a),6) for j in (2,3,4)],sum(r[5] for r in a))
 print('PASS: 8688 updates and 48 full amplitude rewinds')
if __name__=='__main__':run()
