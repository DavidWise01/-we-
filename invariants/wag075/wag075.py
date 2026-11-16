"""WAG-075 GitHub reference: transitive controller ancestry, review and quorum gate.
This is a shortened reference; full locally tested artifact is a conversation download.
Declared controllers and receipts are not independently authenticated.
"""
from dataclasses import dataclass
from hashlib import sha256
import json

def hash_event(x):
    return sha256(json.dumps(x,sort_keys=True,default=list).encode()).hexdigest()

@dataclass(frozen=True)
class Witness:
    name: str
    key: str
    root: str
    controller: str
    operator: str
    domain: str

class ControlSuccession:
    def __init__(self,witnesses,parents):
        self.parents={k:tuple(v) for k,v in parents.items()}
        self._check_dag()
        self.witnesses={w.name:w for w in witnesses}
        if len(witnesses)!=3 or len(self.witnesses)!=3:raise ValueError('three witnesses')
        self._diversity(tuple(self.witnesses.values()))
        self.compromised=self.witnesses['W1']
        self.bad=self.ancestors(self.compromised.controller)
        self.retired={'W1'}
        self.keys={w.key for w in witnesses}
        self.roots={w.root for w in witnesses}
        self.generation=0;self.proposal=None;self.reviews=set()
        self.receipts={};self.used=set();self.ledger=[]
        self._record('genesis',{'members':sorted(self.witnesses)})
    def _check_dag(self):
        visited=set();active=set()
        def visit(n):
            if n in active:raise ValueError('cycle')
            if n in visited:return
            active.add(n)
            for p in self.parents.get(n,()):visit(p)
            active.remove(n);visited.add(n)
        for n in self.parents:visit(n)
    def ancestors(self,n):
        out={n}
        for p in self.parents.get(n,()):out.update(self.ancestors(p))
        return frozenset(out)
    def _diversity(self,ws):
        for field in ('name','key','root','operator','domain'):
            values=[getattr(w,field) for w in ws]
            if any(not x for x in values) or len(set(values))!=3:
                raise ValueError('collision '+field)
        for i in range(len(ws)):
            for j in range(i+1,len(ws)):
                if self.ancestors(ws[i].controller)&self.ancestors(ws[j].controller):
                    raise ValueError('shared control ancestry')
    def _record(self,kind,data):
        x={'index':len(self.ledger),'prior':self.ledger[-1]['hash'] if self.ledger else '0'*64,
           'kind':kind,'data':data}
        x['hash']=hash_event(x);self.ledger.append(x)
    def verify(self):
        return all(x['index']==i and x['prior']==(self.ledger[i-1]['hash'] if i else '0'*64)
                   and x['hash']==hash_event({k:v for k,v in x.items() if k!='hash'})
                   for i,x in enumerate(self.ledger))
    def propose(self,new):
        if self.proposal:raise ValueError('pending')
        if new.name in self.witnesses or new.name in self.retired or new.key in self.keys or new.root in self.roots:
            raise ValueError('identity reentry')
        if self.bad&self.ancestors(new.controller):
            self._record('reject',{'candidate':new.name,'controller':new.controller})
            raise ValueError('compromised controller lineage')
        survivors=[w for w in self.witnesses.values() if w.name!='W1']
        self._diversity(survivors+[new])
        self.proposal=new;self.reviews=set()
        self._record('propose',{'candidate':new.name,'controller':new.controller})
    def review(self,name):
        if not self.proposal or name not in self.witnesses or name=='W1' or name in self.reviews:
            raise ValueError('invalid reviewer')
        self.reviews.add(name);self._record('review',name)
    def rotate(self):
        if not self.proposal or self.reviews!={'W2','W3'}:raise ValueError('two reviewers required')
        new=self.proposal
        del self.witnesses['W1'];self.witnesses[new.name]=new
        self.keys.add(new.key);self.roots.add(new.root)
        self.proposal=None;self.generation+=1;self.receipts.clear()
        self._record('rotate',{'new':new.name,'generation':self.generation})
    def attest(self,name,receipt,generation):
        if generation!=self.generation or generation==0 or name not in self.witnesses or name in self.receipts or not receipt or receipt in self.used:
            raise ValueError('invalid/replayed attestation')
        self.used.add(receipt);self.receipts[name]=receipt
        self._record('attest',{'name':name,'receipt':receipt,'generation':generation})
    def decide(self):
        return ('LOCAL_DECLARED_SUCCESSION_ACCEPTED' if self.generation>0 and
            set(self.receipts)==set(self.witnesses) else 'HOLD_MISSING_FRESH_QUORUM')

def demo():
    w=(Witness('W1','k1','A','org-x','op1','fd1'),
       Witness('W2','k2','B','org-y','op2','fd2'),
       Witness('W3','k3','C','org-z','op3','fd3'))
    g=ControlSuccession(w,{'shell-w4':['org-x']})
    try:g.propose(Witness('W4','k4','D','shell-w4','op4','fd4'))
    except ValueError:pass
    g.propose(Witness('W4','k4','D','org-w','op4','fd4'))
    g.review('W2');g.review('W3');g.rotate()
    for n in ('W2','W3','W4'):g.attest(n,'fresh-'+n,1)
    return g
if __name__=='__main__':
    g=demo()
    print(g.decide(),len(g.ledger),g.verify())
