from random import Random
from statistics import median
Q=(8,32,128); H=(5000,15000,30000)

def run(seq,hold):
    c=[0]*3; p=age=s=quiet=0; events=[]; trace=[]
    for n,d in enumerate(seq):
        c=[(1 if v>=0 else -1)*(abs(v)*(q-1)//q)+d for v,q in zip(c,Q)]
        if s:
            quiet=quiet+1 if all(s*v<t//2 for v,t in zip(c,H)) else 0
            if quiet>=hold:
                events.append((n,'release',s)); s=quiet=0
        if not s:
            if not p:
                j=next((j for j,v in enumerate(c) if abs(v)>=H[j]),None)
                if j is not None:p=1 if c[j]>0 else -1;age=0
            if p:
                if age>=3 and sum(p*v>=t for v,t in zip(c,H))>=2:
                    s=p;events.append((n,'commit',s));p=age=quiet=0
                elif age>=64 or p*c[0]<0:p=age=0
                else:age+=1
        assert s in (-1,0,1) and 0<=age<=64 and 0<=quiet<hold
        trace.append(s)
    return events,trace

def main():
    count=0
    print('hold,pattern,runs,initial,unbroken,releases,recommits,median_release_delay')
    for hold in (1,8,32):
        for kind in ('gap32','gap128','gap256','quiet','reverse'):
            initial=unbroken=releases=recommits=0;delays=[]
            for seed in range(197,229):
                r=Random(seed);s=1 if seed%2==0 else -1
                def signal(n,sign):return [sign*(900+r.randint(-200,200)) for _ in range(n)]
                seq=signal(96,s)
                if kind.startswith('gap'):
                    gap=int(kind[3:])
                    for _ in range(4):seq += [0]*gap+signal(96,s)
                else:seq += [0]*512 if kind=='quiet' else signal(512,-s)
                ev,tr=run(seq,hold);count+=len(seq);initial+=tr[95]==s;unbroken+=all(v==s for v in tr[96:])
                rel=[n-95 for n,k,v in ev if n>=96 and k=='release'];com=[n for n,k,v in ev if n>=96 and k=='commit'];releases+=len(rel);recommits+=len(com)
                if rel:delays.append(rel[0])
            print(hold,kind,32,initial,unbroken,releases,recommits,median(delays) if delays else 'NA',sep=',')
    print('PASS',count,'integer state updates')
if __name__=='__main__':main()
