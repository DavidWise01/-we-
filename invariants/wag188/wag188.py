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
def masses(x):return tuple(x[i]**2+x[i+5]**2 for i in range(5))
def choose(b,n,t):
 out=[(-1)**n]*5; a=masses(bright(gap(b,out))); floor=min(a); total=sum(a); blocked=0
 if t is not None:
  for i in (range(5) if n%2==0 else reversed(range(5))):
   alt=out.copy();alt[i]*=-1;c=masses(bright(gap(b,alt)))
   if c[i]>a[i]:
    if 1000*(min(c)-floor)<-t*total:blocked+=1;continue
    out=alt;a=c
  assert 1000*(min(a)-floor)>=-t*total
 return tuple(out),blocked

def response(x,prev,state,policy):
 m=masses(x); total=sum(m); spread=max(m)-min(m)
 a,b=prev or (spread,total); delta=spread*b-a*total; scale=total*b
 if policy=='hysteresis':
  # Engage beyond 2 percentage points; release inside 1 point.
  state=1 if 100*delta>=2*scale else -1 if 100*delta<=-2*scale else 0 if abs(100*delta)<=scale else state if state*delta>0 else 0
 elif policy=='deadband':state=0 if abs(100*delta)<2*scale else (1 if delta>0 else -1)
 else:state=(delta>0)-(delta<0)
 correction=delta if state else 0
 t=0 if policy=='rigid' else max(0,min(25,25*((total-spread)*b-correction)//scale))
 return t,(spread,total),state

def run():
 for batch in (187,188):
  rng=Random(batch);rows=[]
  for k in range(12):
   r=k%5;a=[rng.randint(-2,2) for _ in range(10)];a[r]+=6;a[r+5]+=8;seed=tuple(a)
   for p in ('rigid','directional','deadband','hysteresis'):
    x=seed;den=sum(v*v for v in x);prev=None;state=last=0;switches=changes=0;vals=[];floors=[];hist=[];ts=[];blocked=0
    for n in range(188):
     t,prev,new=response(x,prev,state,p);changes+=new!=state;state=new
     if state: switches+=last!=0 and last!=state;last=state
     ts.append(t);b=bright(x);ss,z=choose(b,n,t);blocked+=z;y=gap(b,ss);den*=D*D
     assert sum(v*v for v in y)==den and bright(gap(y,ss,True),True)==tuple(v*D*D for v in x)
     x=y;hist.append(ss);m=masses(x);vals.append(m[r]/den);floors.append(min(m)/den)
    for ss in reversed(hist):
     y=bright(gap(x,ss,True),True);assert all(v%(D*D)==0 for v in y);x=tuple(v//(D*D) for v in y)
    assert x==seed
    rows.append((p,sum(vals)/188,sum(floors)/188,switches,changes,blocked))
  print('batch',batch,'policy origin_pct floor_pct reversals transitions blocked',flush=True)
  for p in ('rigid','directional','deadband','hysteresis'):
   a=[r for r in rows if r[0]==p];print(p,*[round(100*sum(r[j] for r in a)/12,4) for j in (1,2)],*[sum(r[j] for r in a) for j in (3,4,5)],flush=True)
 print('PASS 18048 exact updates and candidate floor checks, 96 amplitude rewinds',flush=True)
if __name__=='__main__':run()
