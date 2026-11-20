from random import Random
from statistics import median
Q=(8,32,128)
H={8:5000,32:15000,128:30000}
MODES=('fast','medium','slow','nested')

def simulate(seq,mode):
    qs=Q if mode=='nested' else (Q[MODES.index(mode)],)
    c={q:0 for q in qs}; events=[]; a=10000
    for n,d in enumerate(seq):
        hit=[]; h=max(1000,min(50000,2*a))
        if abs(d)>=h: hit=['immediate']
        else:
            for q in qs:
                v=c[q]; c[q]=(1 if v>=0 else -1)*(abs(v)*(q-1)//q)+d
                if abs(c[q])>=H[q]:hit.append(q)
        if hit:
            events.append((n,tuple(hit)))
            c=dict.fromkeys(qs,0)
        k=2 if abs(d)>a else 32; a=((k-1)*a+abs(d))//k
        assert all(abs(c[q])<H[q] for q in qs) and 1000<=h<=50000 and a>=0
    return events

def run():
    rows=[]; count=0
    for mode in MODES:
        noise=0; found={k:[] for k in ('pulse','trend','drift')}
        for seed in range(193,225):
            rng=Random(seed)
            for kind,L,mu,jitter in [('noise',4096,0,1000),('pulse',5,1500,200),('trend',48,900,350),('drift',512,500,500)]:
                seq=[80000]+[mu+rng.randint(-jitter,jitter) for _ in range(L)]
                ev=simulate(seq,mode); count+=len(seq)
                post=[n for n,h in ev if n>0]
                if kind=='noise':noise+=len(post)
                elif post:found[kind].append(post[0])
        row=[mode,noise]
        for k in ('pulse','trend','drift'):row.extend([len(found[k]),median(found[k]) if found[k] else 'NA'])
        rows.append(row)
    print('policy,noise_events,pulse_detected,pulse_median,trend_detected,trend_median,drift_detected,drift_median')
    for r in rows:print(*r,sep=',')
    print('PASS',count,'integer estimator updates')
if __name__=='__main__':run()
