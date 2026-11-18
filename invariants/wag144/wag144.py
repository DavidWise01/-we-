from itertools import combinations

def partitions(n, cap):
    if not n:
        yield (); return
    for k in range(min(n, cap), 0, -1):
        for tail in partitions(n-k,k): yield (k,)+tail

def cut(sizes, threshold):
    if threshold<=0:return 0
    total=0
    for i,s in enumerate(sorted(sizes,reverse=True),1):
        total+=s
        if total>=threshold:return i
    raise ValueError('coverage')

def designs(n,budget,cap=4):
    # Each host group either shares signing custody or isolates every key.
    for sizes in partitions(n,cap):
        for isolated in range(1<<len(sizes)):
            # A singleton needs no additional isolation in this model.
            if any(s==1 and isolated>>i&1 for i,s in enumerate(sizes)):continue
            # Symmetry reduction among equal-sized groups.
            if any(sizes[i]==sizes[i+1] and (isolated>>i&1)<(isolated>>(i+1)&1) for i in range(len(sizes)-1)):continue
            extra=sum(s for i,s in enumerate(sizes) if isolated>>i&1)
            cost=n+2*len(sizes)+extra
            if cost>budget:continue
            signing=tuple(t for i,s in enumerate(sizes) for t in ([1]*s if isolated>>i&1 else [s]))
            for q in range(1,n+1):
                r=(len(sizes),cut(sizes,n-q+1),cut(signing,max(0,2*q-n)))
                yield (sizes,isolated,q,cost,r)

def score(x):
    s,i,q,c,r=x
    return (min(r),min(r[1:]),sum(r),-c,q)

def optimize(n,budget):return max(designs(n,budget),key=score,default=None)

if __name__=='__main__':
    for b in (21,25,29,33,37,39):print(b,optimize(13,b))
    print('configurations',sum(1 for _ in designs(13,39)))
