from random import Random
from statistics import median
Q=(8,32,128); H=(5000,15000,30000)

def run(seq,mode):
 c=[0]*3; p=age=s=quiet=0; reacq=False; fresh=[]; trace=[]
 for d in seq:
  if d is None:
   reacq=True;fresh=[];trace.append((s,None));continue
  c=[(1 if v>=0 else -1)*(abs(v)*(q-1)//q)+d for v,q in zip(c,Q)]
  if s:
   quiet=quiet+1 if all(s*v<t//2 for v,t in zip(c,H)) else 0
   if quiet>=8:s=quiet=0
  if not s:
   if not p:
    j=next((j for j,v in enumerate(c) if abs(v)>=H[j]),None)
    if j is not None:p=1 if c[j]>0 else -1;age=0
   if p:
    if age>=3 and sum(p*v>=t for v,t in zip(c,H))>=2:s=p;p=age=quiet=0
    elif age>=64 or p*c[0]<0:p=age=0
    else:age+=1
  if reacq:
   fresh=(fresh+[d])[-8:]
   if mode=='immediate':reacq=False
   elif len(fresh)==8:
    # Eight observations, at least six matching sign above 0.02 pp; neutral requires eight small observations.
    if (s and sum(s*v>=200 for v in fresh)>=6) or (s==0 and all(abs(v)<200 for v in fresh)):reacq=False
  assert s in (-1,0,1) and 0<=age<=64 and 0<=quiet<8
  trace.append((s,None if reacq else s))
 return trace

def main():
 count=0
 print('mode,pattern,runs,qualified_correct,median_correct_latency,wrong_slots,unknown_slots')
 for mode in ('immediate','fresh'):
  for kind,targetmul in [('same',1),('reverse',-1),('quiet',0)]:
   delays=[];wrong=unknown=0
   for seed in range(199,231):
    r=Random(seed);s=1 if seed%2==0 else -1;target=s*targetmul
    seq=[s*(900+r.randint(-200,200)) for _ in range(96)]+[None]*256+[target*(900+r.randint(-200,200)) if target else r.randint(-100,100) for _ in range(256)]
    tr=run(seq,mode);count+=len(seq);assert tr[95][0]==s and all(a==s and b is None for a,b in tr[96:352])
    post=[b for a,b in tr[352:]];hits=[i+1 for i,b in enumerate(post) if b==target]
    if hits:delays.append(hits[0])
    wrong+=sum(b is not None and b!=target for b in post);unknown+=post.count(None)
   print(mode,kind,32,len(delays),median(delays) if delays else 'NA',wrong,unknown,sep=',')
 print('PASS',count,'slots')
if __name__=='__main__':main()
