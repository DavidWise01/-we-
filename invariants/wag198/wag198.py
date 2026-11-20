from random import Random
from statistics import median
Q=(8,32,128); H=(5000,15000,30000)
def run(seq,mode):
 c=[0]*3;p=age=s=quiet=missing=0;trace=[];events=[]
 for n,d in enumerate(seq):
  missing=missing+1 if d is None else 0
  if d is None and mode!='zero':
   # Freeze evidence, but distinguish stale output from known neutral.
   trace.append((s,None if mode=='qualified' else s));continue
  d=0 if d is None else d
  c=[(1 if v>=0 else -1)*(abs(v)*(q-1)//q)+d for v,q in zip(c,Q)]
  if s:
   quiet=quiet+1 if all(s*v<t//2 for v,t in zip(c,H)) else 0
   if quiet>=8:events.append((n,'release',s));s=quiet=0
  if not s:
   if not p:
    j=next((j for j,v in enumerate(c) if abs(v)>=H[j]),None)
    if j is not None:p=1 if c[j]>0 else -1;age=0
   if p:
    if age>=3 and sum(p*v>=t for v,t in zip(c,H))>=2:
     s=p;events.append((n,'commit',s));p=age=quiet=0
    elif age>=64 or p*c[0]<0:p=age=0
    else:age+=1
  assert s in (-1,0,1) and 0<=age<=64 and 0<=quiet<8
  trace.append((s,s))
 return trace,events

def main():
 count=0
 print('mode,pattern,retained_at_gap_end,unknown_samples,release_runs,median_release_after_resume')
 for mode in ('zero','freeze','qualified'):
  for kind in ('missing_same','missing_reverse','measured_zero'):
   retained=unknown=released=0;delays=[]
   for seed in range(198,230):
    r=Random(seed);s=1 if seed%2==0 else -1
    def sig(n,sign):return [sign*(900+r.randint(-200,200)) for _ in range(n)]
    seq=sig(96,s)+([0] if kind=='measured_zero' else [None])*256+sig(256,-s if kind=='missing_reverse' else s)
    tr,ev=run(seq,mode);count+=len(seq);assert tr[95][0]==s
    retained+=tr[351][0]==s;unknown+=sum(b is None for a,b in tr)
    rel=[n for n,k,v in ev if n>=96 and k=='release'];released+=bool(rel)
    if rel and rel[0]>=352:delays.append(rel[0]-351)
    if mode=='qualified' and kind!='measured_zero':assert all(a==s and b is None for a,b in tr[96:352])
   print(mode,kind,retained,unknown,released,median(delays) if delays else 'NA',sep=',')
 print('PASS',count,'processed slots (including missing)')
if __name__=='__main__':main()
