from itertools import combinations

def cut(sizes,t):
    if t<=0:return 0
    for k in range(1,len(sizes)+1):
        if sum(sorted(sizes,reverse=True)[:k])>=t:return k
    raise ValueError('coverage')

def placements(n,budget,capacity=4,domain_cost=2,witness_cost=1):
    if min(n,capacity,domain_cost,witness_cost)<1 or budget<0:raise ValueError('parameters')
    def partitions(left,maximum):
        if not left:yield ();return
        for i in range(min(left,maximum),0,-1):
            for tail in partitions(left-i,i):yield (i,)+tail
    for sizes in partitions(n,capacity):
        cost=n*witness_cost+len(sizes)*domain_cost
        if cost>budget:continue
        for q in range(1,n+1):
            # shared infrastructure affects erasure and availability; signing keys independently controlled
            r=(len(sizes),cut(sizes,n-q+1),max(0,2*q-n))
            yield dict(sizes=sizes,q=q,cost=cost,r=r)

def optimize(n,budget,**kwargs):
    rows=list(placements(n,budget,**kwargs))
    return max(rows,key=lambda x:(min(x['r']),min(x['r'][1:]),sum(x['r']),-x['cost'],x['q'])) if rows else None
