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

def run():
 rng=Random(185); rows=[]
 for k in range(12):
  r=k%5;a=[rng.randint(-2,2) for _ in range(10)];a[r]+=6;a[r+5]+=8;seed=tuple(a)
  for t in (None,0,5,10,25,1000):
   x=seed;den=sum(v*v for v in x);vals=[];floors=[];hist=[];blocked=0
   for n in range(185):
    b=bright(x);ss,z=choose(b,n,t);blocked+=z;y=gap(b,ss);den*=D*D
    assert sum(v*v for v in y)==den
    assert bright(gap(y,ss,True),True)==tuple(v*D*D for v in x)
    x=y;hist.append(ss);m=masses(x);vals.append(m[r]/den);floors.append(min(m)/den)
   for ss in reversed(hist):
    y=bright(gap(x,ss,True),True);assert all(v%(D*D)==0 for v in y);x=tuple(v//(D*D) for v in y)
   assert x==seed
   rows.append((t,sum(vals)/len(vals),sum(floors)/len(floors),min(floors),blocked))
 for t in (None,0,5,10,25,1000):
  a=[r for r in rows if r[0]==t];print(t,*[round(100*sum(r[j] for r in a)/len(a),4) for j in (1,2,3)],sum(r[4] for r in a))
 print('PASS 13320 exact updates, 72 amplitude rewinds, 11100 candidate floor checks')
if __name__=='__main__':run()
