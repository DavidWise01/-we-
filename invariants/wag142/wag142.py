from itertools import combinations

def cut(n, domains, threshold):
    if type(n)!=int or n<1 or not 0<=threshold<=n: raise ValueError('threshold')
    universe=set(range(n))
    if not domains or any(not set(v)<=universe for v in domains.values()) or set().union(*map(set,domains.values()))!=universe: raise ValueError('coverage')
    masks=[sum(1<<i for i in set(v)) for v in domains.values()]
    for k in range(len(masks)+1):
        for group in combinations(masks,k):
            u=0
            for m in group:u|=m
            if u.bit_count()>=threshold:return k

def vector(n,q,maps):
    if not 1<=q<=n:raise ValueError('quorum')
    return tuple(cut(n,maps[a],t) for a,t in zip('eaf',(n,n-q+1,max(0,2*q-n))))

def frontier(n,maps):
    rows=[(q,vector(n,q,maps)) for q in range(1,n+1)]
    return [(q,r) for q,r in rows if not any(s!=r and all(b>=a for a,b in zip(r,s)) for _,s in rows)]

def independent(n):return {str(i):{i} for i in range(n)}
def example(n):return {'e':independent(n),'a':{'host':set(range(n))},'f':independent(n)}
if __name__=='__main__':
    for n in (3,5,8,13):
        m={a:independent(n) for a in 'eaf'}
        print(n,frontier(n,m))
        print('shared availability:',frontier(n,example(n)))
