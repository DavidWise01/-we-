D=625*401
E=((0,1),(2,3),(1,2),(3,4))
def bright(x,reverse=False):
    y=list(x); s=-1 if reverse else 1
    for i,j in (E[::-1] if reverse else E):
        a,b=y[i],y[j]; y=[5*v for v in y]; y[i],y[j]=3*a-s*4*b,s*4*a+3*b
    return tuple(y)
def gap(x,signs,reverse=False):
    y=list(x)
    for i,s in enumerate(signs):
        if reverse:s=-s
        a,b=y[i],y[i+5]; y[i],y[i+5]=399*a-s*40*b,s*40*a+399*b
    return tuple(y)
def select(x,prev):
    # Maximize local dark-channel norm after the current bright layer.
    return tuple(1 if x[i]*x[i+5]>0 else -1 if x[i]*x[i+5]<0 else -prev[i] for i in range(5))
def run():
    print('fixture,policy,mean,min,final')
    for r in range(5):
      for kind in ('dark','mixed'):
        seed=tuple(3 if kind=='mixed' and i==r else 4 if kind=='mixed' and i==r+5 else 1 if kind=='dark' and i==r+5 else 0 for i in range(10))
        for policy in ('echo','local'):
          x=seed; den=sum(v*v for v in x); vals=[1.]; history=[]; prev=(-1,)*5
          for k in range(177):
            b=bright(x); signs=select(b,prev) if policy=='local' else ((-1)**k,)*5
            y=gap(b,signs); den*=D*D
            assert sum(v*v for v in y)==den
            assert bright(gap(y,signs,True),True)==tuple(v*D*D for v in x)
            x=y; history.append(signs); prev=signs; vals.append((x[r]**2+x[r+5]**2)/den)
          for signs in reversed(history):
            y=bright(gap(x,signs,True),True); assert all(v%(D*D)==0 for v in y); x=tuple(v//(D*D) for v in y)
          assert x==seed
          print(f'{kind}{r+1},{policy},{sum(vals)/len(vals):.6f},{min(vals):.6f},{vals[-1]:.6f}')
    print('PASS: 3540 exact norm/inverse checks; 20 full rewinds')
if __name__=='__main__':run()
