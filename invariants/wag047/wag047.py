"""WAG-047 assignment integrity; reference only, not proof of randomization."""
from dataclasses import dataclass
from hashlib import sha256
from math import comb
import json

def digest(data):
    return sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()

@dataclass(frozen=True)
class Subject:
    sid: str
    covariate: int

@dataclass(frozen=True)
class Observation:
    sid: str
    assigned: str
    exposed: str
    outcome: int
    tick: int
    packet: str
    root: str

class AssignmentAudit:
    def __init__(self,alpha=.02,max_covariate_gap=.20,min_per_arm=10):
        if not (0<alpha<1 and 0<=max_covariate_gap<=1 and min_per_arm>=2):
            raise ValueError('invalid policy')
        self.policy=dict(alpha=alpha,max_covariate_gap=max_covariate_gap,min_per_arm=min_per_arm)
        self.subjects={};self.assignments={};self.commit=None
        self.records={};self.packets=set();self.roots=set();self.ledger=[]
        self._append('policy',self.policy)

    def _append(self,kind,payload):
        r={'seq':len(self.ledger),'previous':self.ledger[-1]['hash'] if self.ledger else '0'*64,
           'kind':kind,'payload':payload}
        r['hash']=digest(r);self.ledger.append(r)

    def verify(self):
        return all(r['seq']==i and r['previous']==(self.ledger[i-1]['hash'] if i else '0'*64)
                   and r['hash']==digest({k:v for k,v in r.items() if k!='hash'})
                   for i,r in enumerate(self.ledger))

    def register_subject(self,subject):
        if (self.commit is not None or not isinstance(subject,Subject) or not subject.sid
            or subject.sid in self.subjects or type(subject.covariate)!=int
            or subject.covariate not in (0,1)):
            raise ValueError('invalid subject')
        self.subjects[subject.sid]=subject
        self._append('subject',vars(subject))

    def freeze_assignment(self,allocation,mechanism='externally_generated_random_permutation'):
        if self.commit is not None or not self.subjects or set(allocation)!=set(self.subjects):
            raise ValueError('invalid allocation')
        if not mechanism or any(x not in ('control','intervention') for x in allocation.values()):
            raise ValueError('invalid allocation')
        n0=sum(v=='control' for v in allocation.values());n1=len(allocation)-n0
        if min(n0,n1)<self.policy['min_per_arm']:
            raise ValueError('insufficient allocation')
        self.assignments=dict(allocation)
        ordered=sorted(allocation.items())
        self.commit=digest({'assignment':ordered,'mechanism':mechanism,'subjects':sorted(self.subjects)})
        self._append('freeze',{'commit':self.commit,'allocation':ordered,'mechanism':mechanism})
        return self.commit

    def observe(self,obs):
        if (self.commit is None or not isinstance(obs,Observation) or obs.sid not in self.subjects
            or obs.sid in self.records or obs.assigned!=self.assignments.get(obs.sid)
            or obs.exposed not in ('control','intervention') or type(obs.outcome)!=int
            or obs.outcome not in (0,1) or type(obs.tick)!=int or obs.tick<=0
            or not obs.packet or not obs.root or obs.packet in self.packets or obs.root in self.roots):
            raise ValueError('invalid/replayed observation')
        self.records[obs.sid]=obs;self.packets.add(obs.packet);self.roots.add(obs.root)
        self._append('observation',vars(obs))

    def evaluate(self):
        if self.commit is None:raise ValueError('no frozen assignment')
        control=[s for s in self.subjects if self.assignments[s]=='control']
        treated=[s for s in self.subjects if self.assignments[s]=='intervention']
        baseline_gap=abs(sum(self.subjects[x].covariate for x in control)/len(control)
                         -sum(self.subjects[x].covariate for x in treated)/len(treated))
        missing=set(self.subjects)-set(self.records)
        crossover=[x for x,o in self.records.items() if o.assigned!=o.exposed]
        if missing:result={'status':'HOLD_MISSING_OUTCOMES','missing':len(missing)}
        elif crossover:result={'status':'HOLD_EXPOSURE_CROSSOVER','crossovers':len(crossover)}
        elif baseline_gap>self.policy['max_covariate_gap']:
            result={'status':'HOLD_BASELINE_IMBALANCE','gap':baseline_gap}
        else:
            c=sum(self.records[x].outcome for x in control)
            t=sum(self.records[x].outcome for x in treated)
            total=c+t;nc=len(control);nt=len(treated)
            numerator=sum(comb(total,k)*comb(nc+nt-total,nc-k)
                for k in range(c,min(total,nc)+1) if 0<=nc-k<=nc+nt-total)
            p=numerator/comb(nc+nt,nc)
            diff=c/nc-t/nt
            result={'status':'ASSOCIATION_SUPPORTED_ASSIGNMENT_CHECKS_PASS' if p<=self.policy['alpha'] and diff>0
                    else 'UNRESOLVED','p_value':p,'risk_difference':diff,'control':(c,nc),
                    'intervention':(t,nt),'baseline_gap':baseline_gap}
        self._append('evaluation',result)
        return result

def demonstration():
    g=AssignmentAudit()
    for i in range(48):g.register_subject(Subject(f'S{i:02d}',i%2))
    allocation={f'S{i:02d}':('control' if i<24 else 'intervention') for i in range(48)}
    g.freeze_assignment(allocation)
    for i in range(48):
        arm=allocation[f'S{i:02d}']
        outcome=int(i%24<(20 if arm=='control' else 12))
        g.observe(Observation(f'S{i:02d}',arm,arm,outcome,i+1,f'p{i}',f'r{i}'))
    return g,g.evaluate()

if __name__=='__main__':
    gate,result=demonstration()
    print(json.dumps({'result':result,'records':len(gate.ledger),'ledger_valid':gate.verify()},indent=2))
