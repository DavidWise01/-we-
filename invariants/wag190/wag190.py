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

def update(a,d,p):
 q=8 if p!='asymmetric' else (2 if d>a else 32)
 return ((q-1)*a+d)//q
def threshold(a,p):return 20000 if p=='fixed' else max(1000,min(50000,2*a))
def response(x,prev,state,p,a):
 m=masses(x); total=sum(m); spread=max(m)-min(m)
 old,den=prev or (spread,total); delta=spread*den-old*total; scale=total*den
 h=threshold(a,p); low=h//2
 state=1 if 1000000*delta>=h*scale else -1 if 1000000*delta<=-h*scale else 0 if abs(1000000*delta)<=low*scale else state if state*delta>0 else 0
 t=max(0,min(25,25*((total-spread)*den-(delta if state else 0))//scale))
 return t,(spread,total),state,update(a,1000000*abs(delta)//scale,p),h

def run():
 for batch in (189,190):
  rng=Random(batch);rows=[]
  for k in range(12):
   r=k%5;v=[rng.randint(-2,2) for _ in range(10)];v[r]+=6;v[r+5]+=8;seed=tuple(v)
   for p in ('fixed','symmetric','asymmetric'):
    x=seed;den=sum(v*v for v in x);prev=None;state=last=rev=trans=blocked=0;a=10000;vals=[];floors=[];hs=[];hist=[]
    for n in range(190):
     t,prev,new,a,h=response(x,prev,state,p,a);trans+=new!=state;state=new
     if state:rev+=last!=0 and last!=state;last=state
     hs.append(h);b=bright(x);ss,z=choose(b,n,t);blocked+=z;y=gap(b,ss);den*=D*D
     assert sum(v*v for v in y)==den and bright(gap(y,ss,True),True)==tuple(v*D*D for v in x)
     x=y;hist.append(ss);m=masses(x);vals.append(m[r]/den);floors.append(min(m)/den)
    for ss in reversed(hist):
     y=bright(gap(x,ss,True),True);assert all(v%(D*D)==0 for v in y);x=tuple(v//(D*D) for v in y)
    assert x==seed
    rows.append((p,sum(vals)/190,sum(floors)/190,rev,trans,blocked,sum(hs)/190/10000))
  print('batch',batch,'policy origin_pct floor_pct reversals transitions blocked mean_engage_pp',flush=True)
  for p in ('fixed','symmetric','asymmetric'):
   a=[r for r in rows if r[0]==p];print(p,*[round(100*sum(r[j] for r in a)/12,4) for j in (1,2)],*[sum(r[j] for r in a) for j in (3,4,5)],round(sum(r[6] for r in a)/12,4),flush=True)
 print('PASS 13680 exact updates, candidate floor checks and 72 amplitude rewinds',flush=True)
 print('SHOCK: initial scale 1 pp; one 8 pp observation then zero observations; post-update engagement pp')
 for p in ('fixed','symmetric','asymmetric'):
  a=update(10000,80000,p);v=[threshold(a,p)/10000]
  for i in range(1,65):
   a=update(a,0,p)
   if i in (1,8,32,64):v.append(threshold(a,p)/10000)
  print(p,*v)
if __name__=='__main__':run()
