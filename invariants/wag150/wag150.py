from fractions import Fraction as F

# Five paired channels, each with its own exchange coefficient.
K=tuple(F(i,20) for i in (1,2,3,4,5))
TARGET=(F(2),)*5+(F(6),)+(F(2),)*5

def step(x,angles):
    if len(x)!=11 or sum(x)!=26 or min(x)<0 or x[5]!=6: raise ValueError('state')
    y=list(x)
    # Conservative pair exchange; the central singlet is isolated.
    for r,k in enumerate(K,1):
        a,b=5-r,5+r
        flux=k*(x[a]-x[b])
        y[a]-=flux;y[b]+=flux
    return tuple(y),(angles[0]-1)%360,(angles[1]+1)%360

def error(x):return sum((a-b)**2 for a,b in zip(x,TARGET))

def run(n=200):
    x=tuple(map(F,[0,1,0,3,1,6,3,1,4,3,4]));angles=(0,0)
    assert sum(x)==26
    rows=[]
    for i in range(n+1):
        rows.append((i,float(error(x)),float(max(abs(a-b) for a,b in zip(x,TARGET)))))
        y,l,r=step(x,angles)
        assert sum(y)==26 and min(y)>=0 and y[5]==6 and error(y)<=error(x)
        x=y;angles=(l,r);assert (l+r)%360==0
    return rows

if __name__=='__main__':
    for row in run():
        if row[0] in (0,1,10,50,100,200):print(*row)
