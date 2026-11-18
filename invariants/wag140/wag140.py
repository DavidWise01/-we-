from itertools import combinations

def cuts(custodians, domains):
    """Minimal sets of domains covering every evidence custodian.
    Each listed dependency can independently erase its custodian's evidence.
    """
    target=frozenset(custodians)
    if not target or len(target)!=len(custodians): raise ValueError('custodians')
    if any(not set(v)<=target for v in domains.values()): raise ValueError('unknown custodian')
    if set().union(*map(set,domains.values()))!=target: raise ValueError('incomplete model')
    found=[]
    for n in range(1,len(domains)+1):
        for names in combinations(sorted(domains),n):
            s=frozenset(names)
            if any(f<=s for f in found): continue
            if set().union(*(domains[k] for k in names))==target: found.append(s)
    return tuple(tuple(sorted(f)) for f in found)

def resistance(custodians,domains):
    return min(map(len,cuts(custodians,domains)))

def availability_cut(custodians,domains):
    """All-custodian agreement halts when any one required custodian disappears."""
    cuts(custodians,domains)
    return min(1 for v in domains.values() if v)
