"""WAG-045 — minimal predictive context difference, not a causal model."""
from dataclasses import dataclass
from itertools import combinations
from hashlib import sha256
import json

@dataclass(frozen=True)
class Trial:
    packet: str
    root: str
    phase: str
    context: tuple
    success: int

class BoundaryAuditor:
    def __init__(self, fields, min_per_group=4, min_gap=.4, max_features=2, max_candidates=64):
        if not fields or len(set(fields))!=len(fields) or min_per_group<2 or not 0<min_gap<=1 or max_features<1 or max_candidates<1:
            raise ValueError('policy')
        self.fields=tuple(fields)
        self.min_per_group=min_per_group
        self.min_gap=min_gap
        self.max_features=max_features
        self.max_candidates=max_candidates
        self.trials=[]
        self.packets=set()
        self.roots=set()
        self.frozen=None
        self.ledger=[]
        self._append('genesis',{'fields':self.fields})

    @staticmethod
    def _hash(x):
        return sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

    def _append(self,kind,data):
        record={'seq':len(self.ledger),'prev':self.ledger[-1]['hash'] if self.ledger else '0'*64,'kind':kind,'data':data}
        record['hash']=self._hash(record)
        self.ledger.append(record)

    def verify(self):
        return all(r['seq']==i and r['prev']==(self.ledger[i-1]['hash'] if i else '0'*64)
                   and r['hash']==self._hash({k:v for k,v in r.items() if k!='hash'})
                   for i,r in enumerate(self.ledger))

    def add(self,trial):
        if (not isinstance(trial,Trial) or not trial.packet or not trial.root
            or trial.packet in self.packets or trial.root in self.roots
            or trial.phase not in ('discovery','holdout')
            or trial.success not in (0,1) or type(trial.success) is not int
            or len(trial.context)!=len(self.fields)
            or any(not isinstance(v,str) or not v for v in trial.context)
            or (trial.phase=='discovery' and self.frozen is not None)):
            raise ValueError('invalid/replayed/leaked trial')
        if trial.phase=='holdout' and self.frozen is None:
            raise ValueError('holdout before freeze')
        self.trials.append(trial)
        self.packets.add(trial.packet)
        self.roots.add(trial.root)
        self._append('trial',vars(trial))

    def _score(self,records,indices):
        groups={}
        for trial in records:
            groups.setdefault(tuple(trial.context[i] for i in indices),[]).append(trial.success)
        if len(groups)!=2 or min(map(len,groups.values()))<self.min_per_group:
            return None
        rates={key:sum(values)/len(values) for key,values in groups.items()}
        return max(rates.values())-min(rates.values()),rates

    def discover(self):
        if self.frozen is not None:
            raise ValueError('already frozen')
        records=[t for t in self.trials if t.phase=='discovery']
        tried=0
        winner=None
        for size in range(1,min(len(self.fields),self.max_features)+1):
            for indices in combinations(range(len(self.fields)),size):
                tried+=1
                if tried>self.max_candidates:
                    break
                result=self._score(records,indices)
                if result and result[0]>=self.min_gap:
                    winner=(indices,result[0])
                    break
            if winner or tried>=self.max_candidates:
                break
        if winner is None:
            self._append('unresolved',{'candidates':tried})
            return None
        indices,gap=winner
        self.frozen={'indices':indices,'fields':tuple(self.fields[i] for i in indices),
                     'discovery_gap':gap,'discovery_packets':tuple(t.packet for t in records),
                     'candidates':tried}
        self.frozen['digest']=self._hash(self.frozen)
        self._append('freeze',self.frozen.copy())
        return self.frozen.copy()

    def validate(self):
        if self.frozen is None:
            raise ValueError('no frozen hypothesis')
        records=[t for t in self.trials if t.phase=='holdout']
        result=self._score(records,self.frozen['indices'])
        decision='BOUNDARY_SUPPORTED' if result and result[0]>=self.min_gap else 'UNRESOLVED'
        self._append('decision',{'decision':decision,'holdout_gap':result[0] if result else None,
                                 'freeze_hash':self.frozen['digest']})
        return decision

def demonstration():
    auditor=BoundaryAuditor(('sensor','calibration','temperature','software'))
    n=0
    for phase in ('discovery','holdout'):
        for calibration,successes in (('v1.0',[1]*12),('v1.1',[1]*6+[0]*6)):
            for success in successes:
                n+=1
                auditor.add(Trial('packet-'+str(n),'root-'+str(n),phase,
                                  ('S100',calibration,'22C','r7.4'),success))
        if phase=='discovery':
            auditor.discover()
    return auditor,auditor.validate()

if __name__=='__main__':
    auditor,decision=demonstration()
    print(json.dumps({'decision':decision,'feature':auditor.frozen['fields'],
                      'records':len(auditor.ledger),'ledger_valid':auditor.verify()},indent=2))
