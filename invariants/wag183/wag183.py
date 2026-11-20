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
def local(x,i):return x[i]**2+x[i+5]**2
def choose(b,k,mode):
 base=((-1)**k,)*5; out=list(base); predicted=[]
 if mode=='echo':return base,0,0
 for i in (range(5) if k%2==0 else reversed(range(5))):
  cur=tuple(out) if mode=='staggered' else base
  alt=list(cur); alt[i]*=-1
  a=local(bright(gap(b,cur)),i); c=local(bright(gap(b,alt)),i)
  if c>a:out[i]=alt[i]; predicted.append((i,a))
 actual=bright(gap(b,out))
 return tuple(out),len(predicted),sum(local(actual,i)<a for i,a in predicted)
def run():
 rng=Random(183); rows=[]
 for k in range(12):
  r=k%5; a=[rng.randint(-2,2) for _ in range(10)]; a[r]+=6; a[r+5]+=8; seed=tuple(a)
  for mode in ('echo','parallel','staggered'):
   x=seed; den=sum(v*v for v in x); vals=[local(x,r)/den]; hist=[]; flips=bad=0
   for n in range(183):
    b=bright(x); ss,f,h=choose(b,n,mode); flips+=f; bad+=h; y=gap(b,ss); den*=D*D
    assert sum(v*v for v in y)==den
    assert bright(gap(y,ss,True),True)==tuple(v*D*D for v in x)
    x=y; hist.append(ss); vals.append(local(x,r)/den)
   for ss in reversed(hist):
    y=bright(gap(x,ss,True),True); assert all(v%(D*D)==0 for v in y); x=tuple(v//(D*D) for v in y)
   assert x==seed
   rows.append((k,mode,sum(vals)/len(vals),min(vals),vals[-1],flips,bad))
 print('fixture,policy,mean,min,final,accepted,harmful')
 for row in rows:print('%d,%s,%.9f,%.9f,%.9f,%d,%d'%row)
 for m in ('echo','parallel','staggered'):
  a=[r for r in rows if r[1]==m]; e=[r for r in rows if r[1]=='echo']; print(m,*[round(sum(r[j] for r in a)/len(a),6) for j in (2,3,4)],sum(r[5] for r in a),sum(r[6] for r in a),'wins',sum(r[2]>s[2] for r,s in zip(a,e)))
 print('PASS: 6588 exact updates and 36 amplitude rewinds')
if __name__=='__main__':run()
