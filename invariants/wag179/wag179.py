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
POLICIES=('echo',-2,-1,0,1,2) # lambda = policy/2

def run():
    print('fixture,policy,mean,min,final')
    for r in range(5):
      for kind in ('dark','mixed'):
        seed=tuple(3 if kind=='mixed' and i==r else 4 if kind=='mixed' and i==r+5 else 1 if kind=='dark' and i==r+5 else 0 for i in range(10))
        for policy in POLICIES:
          x=seed; den=sum(v*v for v in x); vals=[1.]; history=[]; prev=(-1,)*5; old=None
          for k in range(179):
            b=bright(x)
            if policy=='echo': signs=((-1)**k,)*5
            else:
                q=b if old is None else tuple((2+policy)*v-policy*D*w for v,w in zip(b,old))
                signs=tuple(1 if q[i]*q[i+5]>0 else -1 if q[i]*q[i+5]<0 else -prev[i] for i in range(5))
            y=gap(b,signs); den*=D*D
            assert sum(v*v for v in y)==den
            assert bright(gap(y,signs,True),True)==tuple(v*D*D for v in x)
            x=y; old=b; history.append(signs); prev=signs; vals.append((x[r]**2+x[r+5]**2)/den)
          for signs in reversed(history):
            y=bright(gap(x,signs,True),True); assert all(v%(D*D)==0 for v in y); x=tuple(v//(D*D) for v in y)
          assert x==seed
          print(f'{kind}{r+1},{policy if policy=="echo" else policy/2},{sum(vals)/len(vals):.9f},{min(vals):.9f},{vals[-1]:.9f}')
    print('PASS: 10740 exact norm/inverse checks; 60 full amplitude rewinds')
if __name__=='__main__':run()
