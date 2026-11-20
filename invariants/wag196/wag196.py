from random import Random
from statistics import median
Q=(8,32,128); H=(5000,15000,30000)
def run(seq,mode):
 c=[0]*3; p=age=state=quiet=0; events=[]; trace=[]
 for n,d in enumerate(seq):
  c=[(1 if v>=0 else -1)*(abs(v)*(q-1)//q)+d for v,q in zip(c,Q)]
  if state and mode!='latched':
   # Release after eight consecutive observations below half of all thresholds in committed direction.
   quiet=quiet+1 if all(state*v<t//2 for v,t in zip(c,H)) else 0
   if quiet>=8:events.append((n,'release',state));state=quiet=0
  if not state:
   if not p:
    j=next((j for j,v in enumerate(c) if abs(v)>=H[j]),None)
    if j is not None:p=1 if c[j]>0 else -1;age=0
   if p:
    if age>=3 and sum(p*v>=t for v,t in zip(c,H))>=2:
     state=p;events.append((n,'commit',state));p=age=quiet=0
    elif age>=64 or p*c[0]<0:p=age=0
    else:age+=1
  assert state in (-1,0,1) and 0<=age<=64 and 0<=quiet<=8
  trace.append(state)
 return events,trace

def main():
 count=0
 print('mode,pattern,runs,initial_commit,released,reversed,median_release_after_change,median_reverse_after_change')
 for mode in ('latched','recoverable'):
  for kind in ('quiet','reverse','sustain'):
   releases=[]; reversals=[]; initial=0
   for seed in range(196,228):
    r=Random(seed); s=1 if seed%2==0 else -1
    seq=[s*(900+r.randint(-200,200)) for _ in range(96)]
    seq += [r.randint(-200,200) if kind=='quiet' else (-s if kind=='reverse' else s)*(900+r.randint(-200,200)) for _ in range(256)]
    ev,tr=run(seq,mode);count+=len(seq)
    initial+=tr[95]==s
    rel=[n-96+1 for n,k,v in ev if n>=96 and k=='release']; rev=[n-96+1 for n,k,v in ev if n>=96 and k=='commit' and v==-s]
    if rel:releases.append(rel[0])
    if rev:reversals.append(rev[0])
   print(mode,kind,32,initial,len(releases),len(reversals),median(releases) if releases else 'NA',median(reversals) if reversals else 'NA',sep=',')
 print('PASS',count,'integer state updates')
if __name__=='__main__':main()
