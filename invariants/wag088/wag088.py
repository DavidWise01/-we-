"""WAG-088. Predeclared optional-stopping-safe missing-chunk audit.
Synthetic reports; this is NOT a cryptographic storage proof.
H0: at least m of N fixed chunks missing; each round selects a fresh uniform
k-subset. No-missing probability through t independent rounds <= q**t.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from hmac import new as hmac_new
from math import comb
import json
import secrets

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def digest(value):
    return sha256(canonical(value)).hexdigest()
def miss_probability(n:int,missing:int,k:int)->Fraction:
    if not (isinstance(n,int) and not isinstance(n,bool) and isinstance(missing,int)
            and not isinstance(missing,bool) and isinstance(k,int) and not isinstance(k,bool)
            and n>0 and 1<=missing<=n and 1<=k<=n):
        raise ValueError('invalid sampling parameters')
    return Fraction(comb(n-missing,k),comb(n,k))
def look_budget(audit_alpha:Fraction,t:int)->Fraction:
    if not isinstance(t,int) or isinstance(t,bool) or t<1:
        raise ValueError('invalid round')
    return audit_alpha/(t*(t+1))

class FamilyBudget:
    def __init__(self,total=Fraction(1,20)):
        self.total=Fraction(total)
        if not 0<self.total<1: raise ValueError('total budget must be in (0,1)')
        self.allocations={}
    def reserve(self,experiment:str,allocation)->Fraction:
        a=Fraction(allocation)
        if not experiment or experiment in self.allocations or not 0<a<=self.total:
            raise ValueError('invalid or repeated budget reservation')
        if sum(self.allocations.values(),Fraction(0))+a>self.total:
            raise ValueError('family error budget exceeded')
        self.allocations[experiment]=a
        return a

@dataclass(frozen=True)
class Snapshot:
    experiment:str
    round:int
    positions:tuple[int,...]
    challenge:str
    missing_detected:bool
    p_bound:Fraction
    alpha_spent:Fraction
    unique_coverage:int
    decision:str

def _digest_stream(secret:bytes,message:bytes,counter:int)->int:
    return int.from_bytes(hmac_new(secret,message+b':'+str(counter).encode(),'sha256').digest(),'big')

def challenge_positions(secret:bytes,experiment:str,round_no:int,n:int,k:int):
    """HMAC rejection-sampled Fisher-Yates draw; seed must stay secret until release."""
    if not isinstance(secret,bytes) or len(secret)<16 or not experiment or round_no<1 or not 1<=k<=n:
        raise ValueError('invalid challenge')
    arr=list(range(n))
    counter=0
    context=canonical([experiment,round_no,n,k])
    for i in range(k):
        count=n-i
        limit=(1<<256)//count*count
        while True:
            x=_digest_stream(secret,context,counter)
            counter+=1
            if x<limit:break
        j=i+x%count
        arr[i],arr[j]=arr[j],arr[i]
    return tuple(sorted(arr[:k]))

class Auditor:
    def __init__(self,experiment:str,n:int,minimum_missing:int,sample_size:int,
                 family:FamilyBudget,audit_alpha,secret:bytes|None=None):
        self.q=miss_probability(n,minimum_missing,sample_size)
        self.experiment=experiment
        self.n,self.m,self.k=n,minimum_missing,sample_size
        self.secret=secret if secret is not None else secrets.token_bytes(32)
        if not isinstance(self.secret,bytes) or len(self.secret)<16:
            raise ValueError('weak challenge secret')
        self.alpha=family.reserve(experiment,audit_alpha)
        self.round=0
        self.positions_seen=set()
        self.status='COLLECTING'
        self.events=[]
        self.snapshots=[]
        self._append('genesis',{'experiment':experiment,'n':n,
                    'minimum_missing':minimum_missing,'k':sample_size,
                    'alpha':str(self.alpha),'seed_commitment':sha256(self.secret).hexdigest()})
    def _append(self,kind,data):
        e={'seq':len(self.events),
           'prior':self.events[-1]['hash'] if self.events else '0'*64,
           'kind':kind,'data':data}
        e['hash']=digest(e)
        self.events.append(e)
    def ledger_valid(self):
        return all(e['seq']==i and e['prior']==(self.events[i-1]['hash'] if i else '0'*64)
                   and e['hash']==digest({k:v for k,v in e.items() if k!='hash'})
                   for i,e in enumerate(self.events))
    def challenge(self):
        if self.status!='COLLECTING':raise ValueError('audit closed')
        t=self.round+1
        idx=challenge_positions(self.secret,self.experiment,t,self.n,self.k)
        nonce=hmac_new(self.secret,canonical(['WAG088',self.experiment,t,idx]),'sha256').hexdigest()
        return t,idx,nonce
    def submit(self,round_no:int,positions,nonce:str,missing_detected:bool):
        if self.status!='COLLECTING':raise ValueError('audit closed')
        t,expected,expected_nonce=self.challenge()
        if (round_no!=t or type(positions) not in (tuple,list) or tuple(positions)!=expected
                or nonce!=expected_nonce or type(missing_detected) is not bool):
            raise ValueError('stale, manipulated, or malformed sample')
        self.round=t
        self.positions_seen.update(expected)
        p=self.q**t
        alpha_t=look_budget(self.alpha,t)
        if missing_detected:self.status='HOLD_DETECTED_MISSING'
        elif p<=alpha_t:self.status='ELIGIBLE_BOUND'
        else:self.status='COLLECTING'
        snap=Snapshot(self.experiment,t,expected,nonce,missing_detected,p,alpha_t,
                      len(self.positions_seen),self.status)
        self.snapshots.append(snap)
        self._append('sample',{'round':t,'positions':list(expected),'nonce':nonce,
                     'missing_detected':missing_detected,'p':str(p),
                     'alpha_t':str(alpha_t),'unique_coverage':len(self.positions_seen),
                     'decision':self.status})
        return snap
    def certify(self):
        if self.status!='ELIGIBLE_BOUND':raise ValueError('not eligible')
        self.status='CERTIFIED_STATISTICAL_BOUND'
        self._append('certify',{'round':self.round,'p':str(self.q**self.round),
                    'threshold':str(look_budget(self.alpha,self.round))})
        return self.status
    def stop(self):
        if self.status!='COLLECTING':raise ValueError('cannot stop in terminal/eligible state')
        self.status='HOLD_EARLY_STOP'
        self._append('early_stop',{'round':self.round})
        return self.status

def demo():
    family=FamilyBudget(Fraction(1,20))
    audit=Auditor('archive-17',17,3,3,family,Fraction(1,20),
                  b'WAG088_TEST_SEED_DO_NOT_USE_LIVE!')
    history=[]
    while audit.status=='COLLECTING':
        t,idx,nonce=audit.challenge()
        history.append(audit.submit(t,idx,nonce,False))
    result=audit.certify()
    return audit,{'rounds':audit.round,'q':str(audit.q),
                  'last_p':str(history[-1].p_bound),
                  'last_threshold':str(history[-1].alpha_spent),
                  'coverage':len(audit.positions_seen),'decision':result,
                  'ledger_events':len(audit.events),'ledger_valid':audit.ledger_valid()}
if __name__=='__main__':
    print(json.dumps(demo()[1],indent=2))
