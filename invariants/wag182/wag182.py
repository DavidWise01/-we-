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
# Each rank estimates its own next rank mass with other signs held at echo.
def choose(b,k,mode):
 base=((-1)**k,)*5
 if mode=='echo':return base
 if mode=='local':return tuple(1 if b[i]*b[i+5]>0 else -1 if b[i]*b[i+5]<0 else base[i] for i in range(5))
 out=[]
 for i in range(5):
  alt=list(base); alt[i]*=-1
  a=local(bright(gap(b,base)),i); c=local(bright(gap(b,alt)),i)
  out.append(alt[i] if c>a else base[i])
 return tuple(out)
def run():
 rng=Random(182); rows=[]
 for k in range(12):
  r=k%5; a=[rng.randint(-2,2) for _ in range(10)]; a[r]+=6; a[r+5]+=8; seed=tuple(a)
  for mode in ('echo','local','consequence'):
   x=seed; den=sum(v*v for v in x); vals=[local(x,r)/den]; hist=[]
   for n in range(182):
    b=bright(x); ss=choose(b,n,mode); y=gap(b,ss); den*=D*D
    assert sum(v*v for v in y)==den
    assert bright(gap(y,ss,True),True)==tuple(v*D*D for v in x)
    x=y; hist.append(ss); vals.append(local(x,r)/den)
   for ss in reversed(hist):
    y=bright(gap(x,ss,True),True); assert all(v%(D*D)==0 for v in y); x=tuple(v//(D*D) for v in y)
   assert x==seed
   rows.append((k,mode,sum(vals)/len(vals),min(vals),vals[-1]))
 print('fixture,policy,mean,min,final')
 for row in rows: print('%d,%s,%.9f,%.9f,%.9f'%row)
 for m in ('echo','local','consequence'):
  a=[r for r in rows if r[1]==m];e=[r for r in rows if r[1]=='echo'];print(m,*[round(sum(r[j] for r in a)/len(a),6) for j in (2,3,4)],'wins',sum(r[2]>s[2] for r,s in zip(a,e)))
 print('PASS: 6552 exact updates and 36 amplitude rewinds')
if __name__=='__main__':run()
