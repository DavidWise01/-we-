from itertools import combinations

def joint(n,q,domains,axes='eaf'):
    if not 1<=q<=n or not axes or set(axes)-set('eaf'):raise ValueError('scope')
    thresholds=dict(zip('eaf',(n,n-q+1,max(0,2*q-n))))
    u=set(range(n))
    for d in domains.values():
        if set(d)-set('eaf') or any(not set(v)<=u for v in d.values()):raise ValueError('domain')
    for k in range(len(domains)+1):
        hits=[]
        for names in combinations(sorted(domains),k):
            if all(len(set().union(*(set(domains[d].get(a,())) for d in names)))>=thresholds[a] for a in axes):hits.append(names)
        if hits:return k,hits
    return None,[]

def model(shared=False):
    d={f'host{i}':{'e':{i},'a':{i},'f':{i}} for i in range(13)}
    if shared:d.update(provider={'a':set(range(9))},admin={'f':set(range(5))},backup={'e':set(range(8))},recovery={'e':set(range(8,13)),'f':set(range(5,10))})
    return d

if __name__=='__main__':
    for shared in (False,True):
        for a in ('e','a','f','af','ea','ef','eaf'):
            k,h=joint(13,9,model(shared),a);print(shared,a,k,len(h),h[0] if h else None)
