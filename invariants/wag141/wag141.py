from itertools import combinations

def resistance(witnesses, domains, quorum):
    """Each domain can erase, disable or equivocate its listed witnesses."""
    w=set(witnesses); n=len(w)
    if not n or len(witnesses)!=n or type(quorum)!=int or not 1<=quorum<=n: raise ValueError('membership or quorum')
    if not domains or any(not set(v)<=w for v in domains.values()) or set().union(*map(set,domains.values()))!=w: raise ValueError('domain coverage')
    thresholds=(n,n-quorum+1,max(0,2*quorum-n))
    result=[]
    for t in thresholds:
        for k in range(len(domains)+1):
            hits=[c for c in combinations(sorted(domains),k) if len(set().union(*(set(domains[d]) for d in c)))>=t]
            if hits:
                result.append((k,hits)); break
    return tuple(result)
