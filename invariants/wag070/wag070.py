"""WAG-070: local epoch-bound evidence freshness gate (not cryptographic authentication)."""
from dataclasses import dataclass
from hashlib import sha256
import json
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def H(x):return sha256(canon(x).encode()).hexdigest()
@dataclass(frozen=True)
class Witness:
    name:str
    ancestor:str
    operator:str
    failure_domain:str
class EpochGate:
    def __init__(self,witnesses,dependencies):
        self.witnesses=tuple(witnesses)
        if len(self.witnesses)!=3:raise ValueError('three witnesses required')
        for field in ('name','ancestor','operator','failure_domain'):
            values=[getattr(w,field) for w in self.witnesses]
            if len(set(values))!=3 or not all(isinstance(v,str) and v for v in values):raise ValueError('declared provenance')
        self.names=frozenset(w.name for w in self.witnesses)
        self.deps={str(k):frozenset(v) for k,v in dependencies.items()}
        if not self.deps or not self.names.issubset(self.deps) or any(not k or not v or not all(isinstance(p,str) and p for p in v) for k,v in self.deps.items()):raise ValueError('dependencies')
        self.domains=frozenset().union(*self.deps.values())
        self.state={d:True for d in self.domains};self.epoch=0;self.verified=None;self.receipts={};self.used_receipts=set();self.history=[]
        self.append('genesis',{'epoch':0,'snapshot':self.snapshot()})
    def append(self,kind,payload):
        record={'seq':len(self.history),'prev':self.history[-1]['hash'] if self.history else '0'*64,'kind':kind,'payload':payload}
        record['hash']=H(record);self.history.append(record)
    def audit_valid(self):
        return all(r['seq']==i and r['prev']==(self.history[i-1]['hash'] if i else '0'*64) and r['hash']==H({k:v for k,v in r.items() if k!='hash'}) for i,r in enumerate(self.history))
    def snapshot(self):return H({'epoch':self.epoch,'domains':sorted(self.state.items()),'witness_dependencies':sorted((w,sorted(v)) for w,v in self.deps.items())})
    def available(self):return {w for w in self.names if all(self.state[d] for d in self.deps[w])}
    def transition(self,domain,healthy):
        if domain not in self.domains or not isinstance(healthy,bool) or self.state[domain]==healthy:raise ValueError('invalid transition')
        self.state[domain]=healthy;self.epoch+=1;self.verified=None;self.receipts={}
        self.append('domain_state_changed',{'domain':domain,'healthy':healthy,'epoch':self.epoch,'snapshot':self.snapshot()})
    def verify_infrastructure(self):
        if self.available()!=self.names:raise ValueError('not all witnesses available')
        self.verified=(self.epoch,self.snapshot());self.append('verified_snapshot',{'epoch':self.epoch,'snapshot':self.verified[1]})
        return self.verified
    def attest(self,name,receipt_id,epoch,snapshot):
        if name not in self.names or not isinstance(receipt_id,str) or not receipt_id:raise ValueError('invalid receipt')
        if self.verified is None or (epoch,snapshot)!=self.verified or epoch!=self.epoch or snapshot!=self.snapshot():raise ValueError('stale evidence')
        if name not in self.available() or name in self.receipts or receipt_id in self.used_receipts:raise ValueError('replay or unavailable witness')
        self.receipts[name]=receipt_id;self.used_receipts.add(receipt_id)
        self.append('witness_attestation',{'witness':name,'receipt_id':receipt_id,'epoch':epoch,'snapshot':snapshot})
    def certify(self,epoch,snapshot):
        if self.verified is None or (epoch,snapshot)!=self.verified or epoch!=self.epoch or snapshot!=self.snapshot():raise ValueError('stale certificate')
        if self.available()!=self.names or set(self.receipts)!=self.names:raise ValueError('incomplete quorum')
        self.append('local_certificate',{'epoch':epoch,'snapshot':snapshot,'receipts':sorted(self.receipts.items())})
        return 'LOCAL_EPOCH_BOUND_CERTIFICATE'
def demo():
    ws=[Witness('W1','A','op-a','fd-a'),Witness('W2','B','op-b','fd-b'),Witness('W3','C','op-c','fd-c')]
    g=EpochGate(ws,{'W1':{'power-y','network-x','router-a'},'W2':{'power-y','network-x','router-b'},'W3':{'power-z','network-z','router-c'}})
    old_epoch,old_hash=g.verify_infrastructure()
    for w in ('W1','W2','W3'):g.attest(w,'old-'+w,old_epoch,old_hash)
    g.certify(old_epoch,old_hash);g.transition('power-y',False);g.transition('power-y',True)
    old_rejected=False
    try:g.attest('W1','old-W1',old_epoch,old_hash)
    except ValueError:old_rejected=True
    epoch,head=g.verify_infrastructure()
    for w in ('W1','W2','W3'):g.attest(w,'new-'+w,epoch,head)
    result=g.certify(epoch,head)
    return g,{'old_epoch':old_epoch,'new_epoch':epoch,'old_snapshot':old_hash,'new_snapshot':head,'old_rejected':old_rejected,'certificate':result,'events':len(g.history),'audit_ok':g.audit_valid()}
if __name__=='__main__':print(json.dumps(demo()[1],indent=2))
