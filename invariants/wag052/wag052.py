"""WAG-052: abort-censoring diagnostic with observable counterfactual outcome proxies.

All data are synthetic. Censored outcomes unobserved in real-world cases cannot
be treated as observed; analysis reports bounds instead.
"""
from dataclasses import dataclass
from hashlib import sha256
from math import comb
import json


def digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


@dataclass(frozen=True)
class Attempt:
    attempt_id: str
    root: str
    completed: bool
    outcome: int | None
    tick: int
    reason: str = ''


def fisher_two_sided(a, b, c, d):
    """Exact Fisher p via probability-ordering; rows are completed/aborted."""
    if any(type(v) is not int or v < 0 for v in (a,b,c,d)):
        raise ValueError('invalid counts')
    n1 = a+b
    n2 = c+d
    k = a+c
    n = n1+n2
    if not n1 or not n2:
        raise ValueError('empty arm')
    pobs = comb(k,a)*comb(n-k,n1-a)/comb(n,n1)
    p = sum(comb(k,x)*comb(n-k,n1-x)/comb(n,n1)
            for x in range(max(0,n1-(n-k)), min(n1,k)+1)
            if comb(k,x)*comb(n-k,n1-x)/comb(n,n1) <= pobs*(1+1e-12))
    return min(1.0,p)


class CensoringAuditor:
    def __init__(self, alpha=0.05, min_per_group=5):
        if not isinstance(alpha,(float,int)) or not 0<alpha<1 or type(min_per_group) is not int or min_per_group<2:
            raise ValueError('invalid policy')
        self.alpha=alpha
        self.minimum=min_per_group
        self.attempts=[]
        self.ids=set()
        self.roots=set()
        self.last_tick=0
        self.closed=False
        self.events=[]
        self._append('plan',{'alpha':alpha,'minimum':min_per_group})

    def _append(self,kind,payload):
        r={'seq':len(self.events),'prev':self.events[-1]['hash'] if self.events else '0'*64,
           'kind':kind,'payload':payload}
        r['hash']=digest(r)
        self.events.append(r)

    def verify(self):
        return all(r['seq']==i and r['prev']==(self.events[i-1]['hash'] if i else '0'*64)
                   and r['hash']==digest({k:v for k,v in r.items() if k!='hash'})
                   for i,r in enumerate(self.events))

    def add(self,a:Attempt):
        if (self.closed or not isinstance(a,Attempt) or not a.attempt_id or not a.root
            or a.attempt_id in self.ids or a.root in self.roots
            or type(a.completed) is not bool or type(a.tick) is not int or a.tick<=self.last_tick
            or (a.outcome is not None and (type(a.outcome) is not int or a.outcome not in (0,1)))
            or (a.completed and a.outcome is None)
            or (not a.completed and not a.reason)):
            raise ValueError('invalid or replayed attempt')
        self.attempts.append(a)
        self.ids.add(a.attempt_id)
        self.roots.add(a.root)
        self.last_tick=a.tick
        self._append('attempt',vars(a))

    def evaluate(self):
        if self.closed:
            raise ValueError('already evaluated')
        self.closed=True
        complete=[a for a in self.attempts if a.completed]
        aborted=[a for a in self.attempts if not a.completed]
        nc, na=len(complete),len(aborted)
        known_aborted=[a for a in aborted if a.outcome is not None]
        sc=sum(a.outcome for a in complete)
        sa=sum(a.outcome for a in known_aborted)
        unknown=na-len(known_aborted)
        n=nc+na
        if n==0 or nc==0:
            result={'status':'UNRESOLVED_INSUFFICIENT','total':n}
        else:
            bounds=[(sc+sa)/n,(sc+sa+unknown)/n]
            result={'status':'UNRESOLVED_MISSING_OUTCOMES','attempts':n,'completed':nc,'aborted':na,
                    'completion_rate':nc/n,'completed_rate':sc/nc,'overall_rate_bounds':bounds,
                    'unknown_abort_outcomes':unknown}
            if unknown==0 and min(nc,na)>=self.minimum:
                p=fisher_two_sided(sc,nc-sc,sa,na-sa)
                result.update({'status':'SELECTION_ASSOCIATION_FLAG' if p<=self.alpha else 'UNRESOLVED_NO_FLAG',
                               'overall_rate':(sc+sa)/n,'aborted_rate':sa/na,'p_value':p})
        self._append('decision',result)
        return result


def demonstration():
    audit=CensoringAuditor()
    outcomes=[1]*16+[0]*4
    abort_outcomes=[1]+[0]*9
    for i,(completed,result) in enumerate([(True,x) for x in outcomes]+[(False,x) for x in abort_outcomes],1):
        audit.add(Attempt(f'a{i}',f'r{i}',completed,result,i,'' if completed else 'withheld'))
    return audit,audit.evaluate()

if __name__=='__main__':
    audit,result=demonstration()
    print(json.dumps({'result':result,'events':len(audit.events),'verified':audit.verify()},indent=2))