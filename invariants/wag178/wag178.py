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
def choose(b,old,prev,policy,k):
    if policy=='echo':return ((-1)**k,)*5
    # old is previous pre-gap sample; multiply by D to align denominators.
    q=b if policy=='local' or old is None else tuple(2*v-D*w for v,w in zip(b,old))
    return tuple(1 if q[i]*q[i+5]>0 else -1 if q[i]*q[i+5]<0 else -prev[i] for i in range(5))
def run():
    print('fixture,policy,mean,min,final')
    for r in range(5):
      for kind in ('dark','mixed'):
        seed=tuple(3 if kind=='mixed' and i==r else 4 if kind=='mixed' and i==r+5 else 1 if kind=='dark' and i==r+5 else 0 for i in range(10))
        for policy in ('echo','local','derivative'):
          x=seed; den=sum(v*v for v in x); vals=[1.]; history=[]; prev=(-1,)*5; old=None
          for k in range(178):
            b=bright(x); signs=choose(b,old,prev,policy,k); y=gap(b,signs); den*=D*D
            assert sum(v*v for v in y)==den
            assert bright(gap(y,signs,True),True)==tuple(v*D*D for v in x)
            x=y; old=b; history.append(signs); prev=signs; vals.append((x[r]**2+x[r+5]**2)/den)
          for signs in reversed(history):
            y=bright(gap(x,signs,True),True); assert all(v%(D*D)==0 for v in y); x=tuple(v//(D*D) for v in y)
          assert x==seed
          print(f'{kind}{r+1},{policy},{sum(vals)/len(vals):.6f},{min(vals):.6f},{vals[-1]:.6f}')
    print('PASS: 5340 exact norm/inverse checks; 30 full rewinds')
if __name__=='__main__':run()
