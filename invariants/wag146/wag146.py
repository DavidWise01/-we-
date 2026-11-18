from itertools import combinations, product

# Effects are half-open intervals [start, start+duration).
# e: erased evidence; a: offline witnesses; f: compromised signing keys.
# Recovery restores modeled evidence from an assumed external source.
def evaluate(events, n, q, horizon):
    if not (1 <= q <= n and horizon > 0): raise ValueError('scope')
    rows=[]
    for t in range(horizon):
        e,a,f=set(),set(),set()
        for start,duration,axis,ids in events:
            if start<0 or duration<1 or axis not in 'eaf' or not set(ids)<=set(range(n)): raise ValueError('event')
            if start<=t<start+duration: {'e':e,'a':a,'f':f}[axis].update(ids)
        # Two conflicting q-signature certificates among online witnesses
        # require >=q online and >=max(0,2q-online) online equivocators.
        online=n-len(a); equiv=len(f-a)
        rows.append((t,len(e)==n,online<q,online>=q and equiv>=max(0,2*q-online)))
    return rows

def search(domains,n,q,horizon,objectives,ordered=False):
    if not objectives or set(objectives)-{1,2,3}: raise ValueError('objective')
    for k in range(len(domains)+1):
        for names in combinations(sorted(domains),k):
            for starts in product(range(horizon),repeat=k):
                events=[(s,d,a,i) for name,s in zip(names,starts) for d,a,i in domains[name]]
                rows=evaluate(events,n,q,horizon)
                hit=all(any(r[j] for r in rows) for j in objectives) if ordered else any(all(r[j] for j in objectives) for r in rows)
                if hit:return k,names,starts
    return None

def model():
    return {'backup':[(2,'e',range(8))], 'recovery':[(2,'e',range(8,13)),(2,'f',range(5,10))], 'provider':[(2,'a',range(9))], 'admin':[(2,'f',range(5))]}

if __name__=='__main__':
    for axes in [(1,),(2,),(3,),(1,2),(1,3),(2,3),(1,2,3)]:
        print(axes,'simultaneous',search(model(),13,9,4,axes),'across_time',search(model(),13,9,4,axes,True))
