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
def choose(b,n,mode):
 out=[(-1)**n]*5; base=masses(bright(gap(b,out))); a=base; flips=blocked=0
 if mode!='echo':
  for i in (range(5) if n%2==0 else reversed(range(5))):
   alt=out.copy(); alt[i]*=-1; c=masses(bright(gap(b,alt)))
   if c[i]>a[i]:
    if mode=='balanced' and min(c)<min(a):blocked+=1;continue
    out=alt;a=c;flips+=1
 if mode=='balanced':assert min(a)>=min(base)
 return tuple(out),flips,blocked

def run():
 rng=Random(184); rows=[]
 for k in range(12):
  r=k%5; a=[rng.randint(-2,2) for _ in range(10)]; a[r]+=6;a[r+5]+=8;seed=tuple(a)
  for mode in ('echo','individual','balanced'):
   x=seed; den=sum(v*v for v in x); vals=[masses(x)[r]/den]; floors=[min(masses(x))/den];hist=[];flips=blocked=0
   for n in range(184):
    ss,f,b=choose(bright(x),n,mode); flips+=f;blocked+=b;y=gap(bright(x),ss);den*=D*D
    assert sum(v*v for v in y)==den
    assert bright(gap(y,ss,True),True)==tuple(v*D*D for v in x)
    x=y;hist.append(ss);vals.append(masses(x)[r]/den);floors.append(min(masses(x))/den)
   for ss in reversed(hist):
    y=bright(gap(x,ss,True),True);assert all(v%(D*D)==0 for v in y);x=tuple(v//(D*D) for v in y)
   assert x==seed
   rows.append((k,mode,sum(vals)/len(vals),min(vals),sum(floors)/len(floors),min(floors),flips,blocked))
 print('fixture,policy,mean_origin,min_origin,mean_floor,min_floor,flips,blocked')
 for row in rows:print('%d,%s,%.9f,%.9f,%.9f,%.9f,%d,%d'%row)
 for m in ('echo','individual','balanced'):
  a=[r for r in rows if r[1]==m];print(m,*[round(sum(r[j] for r in a)/len(a),6) for j in range(2,6)],sum(r[6] for r in a),sum(r[7] for r in a))
 print('PASS 6624 exact updates, 36 amplitude rewinds, 2208 balanced floor checks')
if __name__=='__main__':run()
