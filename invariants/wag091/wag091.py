"""WAG-091 — bounded selective-abort recovery reference (synthetic, no trusted beacon)."""
from dataclasses import dataclass
from hashlib import sha256
import json
def blob(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def digest(v):return sha256(blob(v)).hexdigest()
@dataclass(frozen=True)
class Policy:
    family:str; root:str; n:int; k:int; retries:int
    def __post_init__(self):
        if not self.family or not self.root or not 0<self.k<=self.n or not 0<=self.retries<=16:raise ValueError('policy')
class Gate:
    def __init__(self, policy, witnesses=('W1','W2','W3')):
        if len(witnesses)!=3 or len(set(witnesses))!=3:raise ValueError('witnesses')
        self.p=policy;self.ws=tuple(witnesses);self.epoch=0;self.state='OPEN'
        self.commits={};self.reveals={};self.used_beacons=set();self.beacon=None;self.log=[]
        self.record('GENESIS',{'policy':vars(policy),'witnesses':self.ws})
    def record(self,kind,data):
        e={'n':len(self.log),'prior':self.log[-1]['hash'] if self.log else '0'*64,'epoch':self.epoch,'kind':kind,'data':data}
        e['hash']=digest(e);self.log.append(e)
    def audit(self):
        return all(e['n']==i and e['prior']==(self.log[i-1]['hash'] if i else '0'*64)
                   and e['hash']==digest({k:v for k,v in e.items() if k!='hash'})
                   for i,e in enumerate(self.log))
    def binding(self,w,s):
        return digest({'policy':digest(vars(self.p)),'epoch':self.epoch,'witness':w,'secret':s})
    def commit(self,w,h):
        if self.state!='OPEN' or w not in self.ws or w in self.commits or not isinstance(h,str) or len(h)!=64:raise ValueError('commit')
        self.commits[w]=h;self.record('COMMIT',{'w':w,'h':h})
    def freeze(self):
        if self.state!='OPEN' or set(self.commits)!=set(self.ws):raise ValueError('incomplete')
        self.state='FROZEN';self.record('FREEZE',{'commitments':self.commits.copy()})
    def reveal(self,w,s):
        if self.state!='FROZEN' or w not in self.commits or w in self.reveals or self.binding(w,s)!=self.commits[w]:raise ValueError('reveal')
        self.reveals[w]=s;self.record('REVEAL',{'w':w,'hash':digest(s)})
    def abort(self,why):
        if self.state!='FROZEN' or not why:raise ValueError('abort')
        self.record('ABORT',{'why':why,'missing':sorted(set(self.ws)-set(self.reveals))})
        self.state='ABORTED'
    def retry(self,beacon_id,beacon):
        if self.state!='ABORTED':raise ValueError('not aborted')
        if self.epoch>=self.p.retries:
            self.state='TERMINAL_HOLD';self.record('EXHAUSTED',{})
            raise ValueError('budget exhausted')
        if not beacon_id or not beacon or beacon_id in self.used_beacons:raise ValueError('beacon')
        self.record('RETRY',{'beacon_id':beacon_id,'beacon_hash':digest(beacon)})
        self.used_beacons.add(beacon_id);self.epoch+=1;self.beacon=(beacon_id,beacon)
        self.state='OPEN';self.commits={};self.reveals={}
    def finish(self):
        if self.state!='FROZEN' or set(self.reveals)!=set(self.ws):raise ValueError('missing')
        seed=sha256(blob({'policy':vars(self.p),'epoch':self.epoch,'beacon':self.beacon,
                          'secrets':[self.reveals[w] for w in sorted(self.ws)]})).digest()
        out=[];i=0;N=self.p.n;limit=(1<<256)//N*N
        while len(out)<self.p.k:
            x=int.from_bytes(sha256(seed+i.to_bytes(8,'big')).digest(),'big');i+=1
            if x<limit and x%N not in out:out.append(x%N)
        self.state='FINAL';self.record('FINAL',{'indices':out})
        return tuple(out)
def demo():
    g=Gate(Policy('family91','rootA',17,3,1))
    for w,s in zip(g.ws,('a','b','c')):g.commit(w,g.binding(w,s))
    g.freeze();g.reveal('W1','a');g.reveal('W2','b');g.abort('W3 withheld')
    g.retry('beacon1','demo beacon (not independently verified)')
    for w,s in zip(g.ws,('d','e','f')):g.commit(w,g.binding(w,s))
    g.freeze()
    for w,s in zip(g.ws,('d','e','f')):g.reveal(w,s)
    return g,g.finish()
if __name__=='__main__':
    g,indices=demo();print({'indices':indices,'audit':g.audit(),'events':len(g.log)})
