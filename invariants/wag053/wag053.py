"""WAG-053: auditable precommitted recovery; not proof of unbiased randomness."""
from dataclasses import dataclass
from hashlib import sha256
import json
from math import comb

def digest(v):
    return sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

@dataclass(frozen=True)
class Policy:
    policy_id:str='WAG053:v1'
    max_recoveries:int=1
    fallback_source:str='independent-beacon-declared'
    cutoff_tick:int=10

class RecoveryAuditor:
    def __init__(self,policy=Policy()):
        if (not isinstance(policy,Policy) or not policy.policy_id or
            policy.max_recoveries!=1 or not policy.fallback_source or
            type(policy.cutoff_tick)!=int or policy.cutoff_tick<1):
            raise ValueError('invalid policy')
        self.policy=policy
        self.policy_hash=digest(vars(policy))
        self.records=[]
        self.attempts={}
        self.children={}
        self.sealed=False
        self._append('policy',{'policy':vars(policy),'hash':self.policy_hash})
    def _append(self,kind,payload):
        entry={'seq':len(self.records),'prev':self.records[-1]['hash'] if self.records else '0'*64,'kind':kind,'payload':payload}
        entry['hash']=digest(entry)
        self.records.append(entry)
    def verify(self):
        return all(r['seq']==i and r['prev']==(self.records[i-1]['hash'] if i else '0'*64) and
                   r['hash']==digest({k:v for k,v in r.items() if k!='hash'})
                   for i,r in enumerate(self.records))
    def seal(self,tick):
        if self.sealed or type(tick)!=int or tick!=self.policy.cutoff_tick:
            raise ValueError('wrong cutoff or sealed')
        self.sealed=True
        self._append('seal',{'tick':tick,'policy_hash':self.policy_hash})
    def attempt(self,attempt_id,stage,outcome,tick,*,parent=None,source=None,abort_reason=None):
        if (not self.sealed or not attempt_id or attempt_id in self.attempts or
            type(tick)!=int or tick<=self.policy.cutoff_tick or
            stage not in ('initial','recovery') or outcome not in ('complete','abort')):
            raise ValueError('invalid/replayed attempt')
        if stage=='initial':
            if parent is not None or source is not None:
                raise ValueError('initial not recovery')
        else:
            if (parent not in self.attempts or self.attempts[parent]['stage']!='initial'
                or self.attempts[parent]['outcome']!='abort' or parent in self.children
                or source!=self.policy.fallback_source):
                raise ValueError('unauthorized recovery')
        if (outcome=='abort')!=bool(abort_reason):
            raise ValueError('abort reason mismatch')
        rec={'id':attempt_id,'stage':stage,'outcome':outcome,'tick':tick,
             'parent':parent,'source':source,'abort_reason':abort_reason}
        self.attempts[attempt_id]=rec
        if parent is not None:self.children[parent]=attempt_id
        self._append('attempt',rec.copy())
        return rec.copy()
    def report(self):
        primary=[a for a in self.attempts.values() if a['stage']=='initial']
        recovery=[a for a in self.attempts.values() if a['stage']=='recovery']
        result={'initial':len(primary),'recovery':len(recovery),
                'completed_initial':sum(x['outcome']=='complete' for x in primary),
                'aborted_initial':sum(x['outcome']=='abort' for x in primary),
                'completed_recovery':sum(x['outcome']=='complete' for x in recovery),
                'aborted_recovery':sum(x['outcome']=='abort' for x in recovery),
                'unrecovered_initial_aborts':sum(x['outcome']=='abort' and x['id'] not in self.children for x in primary),
                'status':'AUDITABLE_NOT_UNBIASED_CERTIFIED'}
        self._append('report',result.copy())
        return result

def fisher_two_sided(a,b,c,d):
    if any(type(x)!=int or x<0 for x in (a,b,c,d)) or a+b==0 or c+d==0:
        raise ValueError('invalid table')
    n=a+b+c+d;k=a+c;row=a+b;denom=comb(n,row)
    pmf=lambda x:comb(k,x)*comb(n-k,row-x)/denom
    ref=pmf(a)
    return min(1.0,sum(pmf(x) for x in range(max(0,row-(n-k)),min(row,k)+1) if pmf(x)<=ref+1e-15))

def demonstration():
    a=RecoveryAuditor();a.seal(10)
    for i in range(30):
        a.attempt(f'C0-{i:02d}','initial','complete' if i<20 else 'abort',11+i,
                  abort_reason='withheld' if i>=20 else None)
    for i in range(10):
        a.attempt(f'C1-{i:02d}','recovery','complete' if i<9 else 'abort',50+i,
                  parent=f'C0-{i+20:02d}',source=a.policy.fallback_source,
                  abort_reason='fallback unavailable' if i==9 else None)
    return a,a.report()

if __name__=='__main__':
    a,r=demonstration()
    print(json.dumps({'result':r,'records':len(a.records),'verified':a.verify(),
                      'illustrative_fisher_p':fisher_two_sided(16,4,7,2)},indent=2))
