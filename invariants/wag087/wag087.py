"""WAG-087: exact detection bounds and observed sample coverage."""
from dataclasses import dataclass
from hashlib import sha256
from math import comb, gcd
from fractions import Fraction
import json

def digest(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def detection_fraction(n, missing, k):
    if not all(type(i) is int for i in (n,missing,k)) or n<1 or not 0<=missing<=n or not 0<=k<=n:
        raise ValueError('invalid sampling parameters')
    total=comb(n,k)
    fail=comb(n-missing,k) if k<=n-missing else 0
    p=total-fail
    d=gcd(p,total)
    return p//d,total//d

def detection_probability(n,missing,k):
    a,b=detection_fraction(n,missing,k)
    return a/b

def sample_indices(n,k,seed):
    """Deterministic SHA256 challenge fixture, not a source of secure entropy."""
    if type(n) is not int or type(k) is not int or n<1 or not 0<=k<=n:raise ValueError('dimensions')
    if not isinstance(seed,bytes) or len(seed)<16:raise ValueError('seed')
    ranked=sorted(range(n),key=lambda i:(sha256(b'WAG087-rank-v1\x00'+seed+i.to_bytes(8,'big')).digest(),i))
    return tuple(sorted(ranked[:k]))

@dataclass(frozen=True)
class AuditRecord:
    round_id:str
    challenge:str
    host:str
    ancestor:str
    population:int
    positions:tuple
    result:str='PASS'

class CoverageLedger:
    def __init__(self,population,host_ancestors):
        if type(population) is not int or population<1:raise ValueError('population')
        if not host_ancestors or any(not k or not v for k,v in host_ancestors.items()):raise ValueError('hosts')
        self.population=population
        self.ancestors=dict(host_ancestors)
        self.rounds=[]
        self.log=[]
        self.seen_challenges=set()
        self._append('genesis',{'population':population,'hosts':sorted(host_ancestors.items())})

    def _append(self,kind,payload):
        event={'seq':len(self.log),'previous':self.log[-1]['hash'] if self.log else '0'*64,'kind':kind,'payload':payload}
        event['hash']=digest(event)
        self.log.append(event)

    def audit(self,rec):
        if not isinstance(rec,AuditRecord) or not rec.round_id or not rec.challenge:raise ValueError('record')
        if rec.host not in self.ancestors or rec.ancestor!=self.ancestors[rec.host]:raise ValueError('ancestry')
        if rec.population!=self.population or rec.result not in ('PASS','FAIL'):raise ValueError('result or population')
        if not isinstance(rec.positions,tuple) or not rec.positions or len(rec.positions)!=len(set(rec.positions)) or any(type(i) is not int or not 0<=i<self.population for i in rec.positions):raise ValueError('positions')
        if (rec.host,rec.challenge) in self.seen_challenges:raise ValueError('challenge replay')
        prior=[r for r in self.rounds if r.round_id==rec.round_id]
        if prior and (rec.challenge!=prior[0].challenge or rec.positions!=prior[0].positions):raise ValueError('mismatched round')
        if any(r.host==rec.host for r in prior):raise ValueError('duplicate host round')
        self.rounds.append(rec)
        self.seen_challenges.add((rec.host,rec.challenge))
        self._append('audit',{'round':rec.round_id,'challenge':rec.challenge,'host':rec.host,'ancestor':rec.ancestor,'positions':list(rec.positions),'result':rec.result})

    def inspected(self,host):
        if host not in self.ancestors:raise ValueError('host')
        return set().union(*(set(r.positions) for r in self.rounds if r.host==host and r.result=='PASS'))

    def coverage(self,host):
        return len(self.inspected(host)),self.population

    def cross_host_union(self):
        return set().union(*(self.inspected(h) for h in self.ancestors))

    def distinct_ancestor_count(self):
        return len({r.ancestor for r in self.rounds if r.result=='PASS'})

    def independent_replica_evidence(self):
        return {r.ancestor for r in self.rounds if r.result=='PASS'}

    def cumulative_detection_bound(self,host,missing):
        """Conditional theoretical planning bound; NOT posterior confidence."""
        if host not in self.ancestors or type(missing) is not int or not 0<=missing<=self.population:raise ValueError('parameters')
        no_hit=Fraction(1,1)
        for r in self.rounds:
            if r.host==host and r.result=='PASS':
                a,b=detection_fraction(self.population,missing,len(r.positions))
                no_hit*=1-Fraction(a,b)
        p=1-no_hit
        return p.numerator,p.denominator

    def verify_log(self):
        return all(e['seq']==i and e['previous']==(self.log[i-1]['hash'] if i else '0'*64)
            and e['hash']==digest({k:v for k,v in e.items() if k!='hash'}) for i,e in enumerate(self.log))

def demonstration():
    ledger=CoverageLedger(17,{'W1':'A','W2':'B','W3':'C'})
    for rd,seed in [('r1',b'round-one-entropy-0001'),('r2',b'round-two-entropy-0002')]:
        positions=sample_indices(17,3,seed)
        for host,root in [('W1','A'),('W2','B'),('W3','C')]:
            ledger.audit(AuditRecord(rd,'nonce-'+rd,host,root,17,positions))
    return ledger,{'rounds':2,'host_samples':{h:ledger.coverage(h)[0] for h in ledger.ancestors},
        'global_unique_positions':len(ledger.cross_host_union()),
        'declared_ancestor_roots':ledger.distinct_ancestor_count(),
        'single_round_detection_3missing':detection_fraction(17,3,3),
        'two_round_detection_3missing':ledger.cumulative_detection_bound('W1',3),
        'audit_records':len(ledger.log),'audit_valid':ledger.verify_log()}

if __name__=='__main__':
    print(json.dumps(demonstration()[1],indent=2))
