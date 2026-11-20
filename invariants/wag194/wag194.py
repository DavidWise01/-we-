from random import Random
from statistics import median
Q=(8,32,128); H=(5000,15000,30000)
MODES=('any','coherent','strict')
def simulate(seq,mode):
 a=10000;c=[0]*3;events=[]
 for n,d in enumerate(seq):
  h=max(1000,min(50000,2*a)); hit=[]
  if abs(d)>=h: hit=['immediate']
  else:
   c=[(1 if v>=0 else -1)*(abs(v)*(q-1)//q)+d for v,q in zip(c,Q)]
   for j,v in enumerate(c):
    if abs(v)<H[j]:continue
    support=sum(k!=j and v*w>0 and 4*abs(w)>=H[k] for k,w in enumerate(c))
    if mode=='any' or support >= (1 if mode=='coherent' else 2):hit.append(j)
  if hit:events.append((n,tuple(hit)));c=[0]*3
  q=2 if abs(d)>a else 32;a=((q-1)*a+abs(d))//q
  assert a>=0 and 1000<=h<=50000 and all(abs(v)<=q*max(abs(x) for x in seq[:1]+[d]) or abs(v)<=q*80000 for v,q in zip(c,Q))
 return events

def fixtures():
 for seed in range(194,226):
  r=Random(seed)
  yield 'white',[80000]+[r.randint(-1000,1000) for _ in range(4096)]
  v=0;tail=[]
  for _ in range(4096):
   v=(7*v+r.randint(-1000,1000))//8;tail.append(v)
  yield 'correlated',[80000]+tail
  for kind,L,mu,j in [('pulse',5,1500,200),('trend',48,900,350),('drift',512,500,500)]:
   for sign in (1,-1):yield kind,[80000]+[sign*(mu+r.randint(-j,j)) for _ in range(L)]
def run():
 print('mode,white_events,correlated_events,pulse_found,pulse_median,trend_found,trend_median,drift_found,drift_median')
 count=0
 for mode in MODES:
  noise=dict(white=0,correlated=0); found={k:[] for k in ('pulse','trend','drift')}
  for kind,seq in fixtures():
   ev=simulate(seq,mode);count+=len(seq);post=[n for n,h in ev if n>0]
   if kind in noise:noise[kind]+=len(post)
   elif post:found[kind].append(post[0])
  print(mode,*noise.values(),*[x for k in found for x in (len(found[k]),median(found[k]) if found[k] else 'NA')],sep=',')
 print('PASS',count,'estimator updates')
if __name__=='__main__':run()
