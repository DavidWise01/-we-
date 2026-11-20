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

def tolerance(x,policy):
 if policy == 'adaptive':
  m=masses(x); total=sum(m)
  return 25*(total-max(m)+min(m))//total
 return policy

def run():
 rng=Random(186); rows=[]
 for k in range(12):
  r=k%5;a=[rng.randint(-2,2) for _ in range(10)];a[r]+=6;a[r+5]+=8;seed=tuple(a)
  for p in (None,0,5,10,25,1000,'adaptive'):
   x=seed;den=sum(v*v for v in x);vals=[];floors=[];hist=[];blocked=0;ts=[]
   for n in range(186):
    t=tolerance(x,p);ts.append(t or 0);b=bright(x);ss,z=choose(b,n,t);blocked+=z;y=gap(b,ss);den*=D*D
    assert sum(v*v for v in y)==den
    assert bright(gap(y,ss,True),True)==tuple(v*D*D for v in x)
    x=y;hist.append(ss);m=masses(x);vals.append(m[r]/den);floors.append(min(m)/den)
   for ss in reversed(hist):
    y=bright(gap(x,ss,True),True);assert all(v%(D*D)==0 for v in y);x=tuple(v//(D*D) for v in y)
   assert x==seed
   rows.append((p,sum(vals)/len(vals),sum(floors)/len(floors),min(floors),blocked,sum(ts)/len(ts)))
 print('policy origin_pct floor_pct avg_min_floor_pct blocked mean_tolerance_pct')
 for p in (None,0,5,10,25,1000,'adaptive'):
  a=[r for r in rows if r[0]==p];print(p,*[round(100*sum(r[j] for r in a)/len(a),4) for j in (1,2,3)],sum(r[4] for r in a),round(sum(r[5] for r in a)/len(a)/10,4))
 print('PASS 15624 exact updates, 84 amplitude rewinds, 13392 candidate floor checks')
if __name__=='__main__':run()
