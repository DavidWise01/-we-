from math import sqrt
D=625*401
E=((0,1),(2,3),(1,2),(3,4))
def step(x,sign,reverse=False):
    y=list(x)
    def bright(s,edges):
        for i,j in edges:
            a,b=y[i],y[j]; y[:]=[5*v for v in y]
            y[i],y[j]=3*a-s*4*b,s*4*a+3*b
    def gap(s):
        for i in range(5):
            a,b=y[i],y[i+5]; y[i],y[i+5]=399*a-s*40*b,s*40*a+399*b
    if reverse: gap(-sign); bright(-1,E[::-1])
    else: bright(1,E); gap(sign)
    return tuple(y)
def local(x,r):return x[r]**2+x[r+5]**2
def choose(x,r,previous):
    # One-step lookahead is useless: channel rotation preserves rank norm.
    # Choose sign by two-step retention, assuming the second sign is reversed.
    candidates={s:local(step(step(x,s),-s),r) for s in (-1,1)}
    return -previous if candidates[1]==candidates[-1] else max(candidates,key=candidates.get)
def run():
    print('fixture,policy,mean,min,final,flips')
    for r in range(5):
      for kind in ('dark','mixed'):
        seed=tuple((3 if kind=='mixed' and i==r else 4 if kind=='mixed' and i==r+5 else 1 if kind=='dark' and i==r+5 else 0) for i in range(10))
        for policy in ('echo','feedback'):
          x=seed; den=sum(v*v for v in x); vals=[1.]; signs=[]; previous=-1
          for k in range(176):
            s=(-1)**k if policy=='echo' else choose(x,r,previous)
            y=step(x,s); den*=D*D
            assert sum(v*v for v in y)==den
            assert step(y,s,True)==tuple(v*D*D for v in x)
            x=y; signs.append(s); previous=s; vals.append(local(x,r)/den)
          for s in reversed(signs):
            y=step(x,s,True); assert all(v%(D*D)==0 for v in y); x=tuple(v//(D*D) for v in y)
          assert x==seed
          print(f'{kind}{r+1},{policy},{sum(vals)/len(vals):.6f},{min(vals):.6f},{vals[-1]:.6f},{sum(a!=b for a,b in zip(signs,signs[1:]))}')
    print('PASS: 3520 exact norm/inverse checks, 20 full rewinds')
if __name__=='__main__':run()
