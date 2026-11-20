from random import Random
from statistics import median
P=10000
H=30000
MODES=(1,8,32,128,0) # denominator of leak; 0=no leak

def simulate(seq,q):
    a=P;c=0;events=[]
    for n,d in enumerate(seq):
        h=max(1000,min(50000,2*a))
        if abs(d)>=h:
            events.append((n,'immediate',1 if d>0 else -1));c=0
        else:
            if q:c=(1 if c>=0 else -1)*(abs(c)*(q-1)//q)
            c+=d
            if abs(c)>=H:events.append((n,'cumulative',1 if c>0 else -1));c=0
        k=2 if abs(d)>a else 32
        a=((k-1)*a+abs(d))//k
        assert a>=0 and abs(c)<H and 1000<=h<=50000
    return events

def run():
    print('leak_den,noise_events,noise_cumulative,weak_detected,weak_median,strong_detected,strong_median')
    for q in MODES:
        noise=nc=0;weak=[];strong=[]
        for seed in range(192,224):
            rng=Random(seed)
            seq=[80000]+[rng.randint(-1000,1000) for _ in range(4096)]
            ev=simulate(seq,q);noise+=len(ev)-1;nc+=sum(n>0 and k=='cumulative' for n,k,s in ev)
            for mu,out in ((500,weak),(3500,strong)):
                seq=[80000]+[mu+rng.randint(-500,500) for _ in range(512)]
                ev=simulate(seq,q)
                post=[n for n,k,s in ev if n>0 and s==1]
                if post:out.append(post[0])
        print(q,noise,nc,len(weak),median(weak) if weak else 'NA',len(strong),median(strong) if strong else 'NA',sep=',')
    print('PASS',len(MODES)*32*(4097+2*513),'integer updates')
if __name__=='__main__':run()
