from random import Random
from statistics import median
Q=(8,32,128); H=(5000,15000,30000)
def simulate(seq):
    a=10000;c=[0]*3;pending=0;age=0; alerts=[]; commits=[]; expired=0
    for n,d in enumerate(seq):
        h=max(1000,min(50000,2*a))
        if abs(d)>=h:
            alerts.append(n); commits.append(n); c=[0]*3;pending=age=0
        else:
            c=[(1 if v>=0 else -1)*(abs(v)*(q-1)//q)+d for v,q in zip(c,Q)]
            if not pending and any(abs(v)>=t for v,t in zip(c,H)):
                j=next(j for j in range(3) if abs(c[j])>=H[j]);pending=1 if c[j]>0 else -1;age=0;alerts.append(n)
            if pending:
                if age>=3 and sum(pending*v>=t for v,t in zip(c,H))>=2:
                    commits.append(n);pending=age=0;c=[0]*3
                elif age>=64 or pending*c[0] < 0:
                    expired+=1;pending=age=0;c=[0]*3
                else:age+=1
        q=2 if abs(d)>a else 32;a=((q-1)*a+abs(d))//q
        assert a>=0 and 1000<=h<=50000 and 0<=age<=64
    return alerts,commits,expired

def run():
    count=0;stats={}
    for seed in range(195,227):
        r=Random(seed)
        for kind,L,mu,j in [('white',4096,0,1000),('pulse',5,1500,200),('trend',48,900,350),('drift',512,500,500)]:
            for sign in ((1,) if kind=='white' else (1,-1)):
                seq=[80000]+[sign*(mu+r.randint(-j,j)) for _ in range(L)]+([0]*80 if kind=='pulse' else [])
                a,c,e=simulate(seq);count+=len(seq);a=[x for x in a if x];c=[x for x in c if x]
                z=stats.setdefault(kind,[0,0,0,0,[],[],0]);z[0]+=1;z[1]+=bool(a);z[2]+=bool(c);z[3]+=len(c);z[6]+=len(a)
                if a:z[4].append(a[0])
                if c:z[5].append(c[0])
    print('kind,runs,alerted,committed,commit_events,median_alert,median_commit,alert_events')
    for k,z in stats.items():print(k,*z[:4],median(z[4]) if z[4] else 'NA',median(z[5]) if z[5] else 'NA',z[6],sep=',')
    print('PASS',count,'estimator updates')
if __name__=='__main__':run()
