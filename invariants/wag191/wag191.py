# WAG-191 .dlw: integer disturbance-estimator experiment
from random import Random
P=10000 # units per percentage point

def simulate(seq,mode):
 a=P; acc=0; events=[]; trace=[]
 for n,d in enumerate(seq):
  h=max(1000,min(50000,2*a)) if mode!='fixed' else 20000
  if abs(d)>=h:
   event=1 if d>0 else -1; acc=0
  else:
   acc=max(-30000,min(30000,acc+d)) if mode=='dual' else 0
   event=(1 if acc>=30000 else -1 if acc<=-30000 else 0)
   if event:acc=0
  if event:events.append((n,event))
  q=2 if abs(d)>a else 32
  a=((q-1)*a+abs(d))//q
  assert 0<=a and -30000<=acc<=30000 and 1000<=h<=50000
  trace.append((n,d,h,acc,event))
 return events,trace

def fixtures():
 for seed in range(191,203):
  rng=Random(seed); quiet=[rng.randint(-1000,1000) for _ in range(64)]
  # Separate signed drift from bounded zero-mean alternating disturbance.
  for kind in ('drift','alternating','quiet'):
   tail=([3500+rng.randint(-500,500) for _ in range(64)] if kind=='drift' else [3500*(-1)**i for i in range(64)] if kind=='alternating' else quiet)
   yield seed,kind,[80000]+tail

def run():
 print('mode,drift_detected,median_latency,alternating_false_events,quiet_false_events')
 import statistics
 for mode in ('fixed','asymmetric','dual'):
  delays=[];false={'alternating':0,'quiet':0}
  for seed,kind,seq in fixtures():
   events,trace=simulate(seq,mode);post=[n for n,s in events if n>0]
   if kind=='drift' and post:delays.append(post[0])
   elif kind!='drift':false[kind]+=len(post)
  print(mode,len(delays),statistics.median(delays) if delays else 'NA',false['alternating'],false['quiet'],sep=',')
 print('PASS: 7020 integer estimator updates and bounds checks')
if __name__=='__main__':run()
