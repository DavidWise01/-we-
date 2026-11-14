"""WAG-046 — frozen controlled intervention (synthetic reference)."""
from dataclasses import dataclass
from hashlib import sha256
from math import comb
import json

@dataclass(frozen=True)
class Trial:
    packet: str
    root: str
    arm: str
    success: int
    context: str
    epoch: int

class InterventionGate:
    def __init__(self, factor='calibration', control='v1.0', treatment='v1.1',
                 alpha=.02, minimum=8, expected_direction='decrease'):
        if not factor or not control or not treatment or control == treatment or not 0 < alpha < 1 or minimum < 4 or expected_direction not in ('decrease','increase'):
            raise ValueError('invalid preregistration')
        self.plan=dict(factor=factor,control=control,treatment=treatment,
                       alpha=alpha,minimum=minimum,direction=expected_direction)
        self.frozen=False
        self.packets=set();self.roots=set();self.trials=[];self.ledger=[]
        self._append('plan',self.plan)
    def _hash(self,d):
        return sha256(json.dumps(d,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    def _append(self,kind,data):
        e={'seq':len(self.ledger),'prev':self.ledger[-1]['hash'] if self.ledger else '0'*64,'kind':kind,'data':data}
        e['hash']=self._hash(e)
        self.ledger.append(e)
    def verify(self):
        return all(r['seq']==i and r['prev']==(self.ledger[i-1]['hash'] if i else '0'*64) and r['hash']==self._hash({k:v for k,v in r.items() if k!='hash'}) for i,r in enumerate(self.ledger))
    def freeze(self):
        if self.frozen: raise ValueError('already frozen')
        self.frozen=True
        self._append('freeze',{'plan_hash':self._hash(self.plan)})
    def add(self,t):
        if not self.frozen or not isinstance(t,Trial) or not t.packet or not t.root or t.packet in self.packets or t.root in self.roots or t.arm not in ('control','treatment') or type(t.success) is not int or t.success not in (0,1) or t.context!='fixed' or not isinstance(t.epoch,int) or t.epoch<0:
            raise ValueError('invalid observation')
        self.packets.add(t.packet);self.roots.add(t.root);self.trials.append(t)
        self._append('trial',vars(t))
    def evaluate(self):
        a=[t.success for t in self.trials if t.arm=='control']
        b=[t.success for t in self.trials if t.arm=='treatment']
        if min(len(a),len(b))<self.plan['minimum']:
            outcome={'decision':'HOLD_INSUFFICIENT','p':None}
        else:
            n1,n2=len(a),len(b);s1,s2=sum(a),sum(b);K=s1+s2;N=n1+n2
            denominator=comb(N,n1)
            left=max(0,n1-(N-K));right=min(n1,K)
            if self.plan['direction']=='decrease':
                numerator=sum(comb(K,k)*comb(N-K,n1-k) for k in range(max(s1,left),right+1))
            else:
                numerator=sum(comb(K,k)*comb(N-K,n1-k) for k in range(left,min(s1,right)+1))
            p=numerator/denominator
            effect=s1/n1-s2/n2
            if self.plan['direction']=='increase':effect=-effect
            outcome={'decision':'INTERVENTION_SUPPORTED' if p<=self.plan['alpha'] and effect>0 else 'UNRESOLVED',
                     'p':p,'difference':effect,'control':(s1,n1),'treatment':(s2,n2)}
        self._append('evaluation',outcome)
        return outcome

def demonstration():
    g=InterventionGate();g.freeze()
    for arm,successes in [('control',[1]*12),('treatment',[1]*6+[0]*6)]:
        for index,s in enumerate(successes):
            g.add(Trial(f'{arm}-{index}',f'{arm}-root-{index}',arm,s,'fixed',1))
    return g,g.evaluate()

if __name__=='__main__':
    gate,result=demonstration()
    print(json.dumps({'result':result,'records':len(gate.ledger),'valid':gate.verify()},indent=2))
