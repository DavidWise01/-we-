"""WAG-078 compact signed full-prefix continuity reference, not Merkle proof."""
from dataclasses import dataclass
from hashlib import sha256
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

def encode(x):return json.dumps(x,separators=(',',':'),sort_keys=True).encode()
def digest(x):return sha256(encode(x)).hexdigest()

@dataclass(frozen=True)
class Head:
    registry:str
    size:int
    root:str
    epoch:int
    signature:bytes
    def payload(self):return encode(['WAG078-registry-head',self.registry,self.size,self.root,self.epoch])

@dataclass(frozen=True)
class Vote:
    witness:str
    ancestor:str
    old_root:str
    new_root:str
    new_size:int
    epoch:int
    signature:bytes
    def payload(self):return encode(['WAG078-observer-vote',self.witness,self.ancestor,self.old_root,self.new_root,self.new_size,self.epoch])

class PrefixGate:
    def __init__(self):
        self.registry='registry-A'
        self.registry_sk=Ed25519PrivateKey.generate()
        self.registry_pk=self.registry_sk.public_key()
        self.witness_sk={k:Ed25519PrivateKey.generate() for k in ('W1','W2','W3')}
        self.witness_pk={k:v.public_key() for k,v in self.witness_sk.items()}
        self.ancestors={'W1':'A','W2':'B','W3':'C'}
        self.frozen=None
        self.frozen_events=None
        self.audit=[]
        self._event('genesis',self.registry)
    def _event(self,kind,data):
        event={'n':len(self.audit),'prev':self.audit[-1]['hash'] if self.audit else '0'*64,'kind':kind,'data':data}
        event['hash']=digest(event)
        self.audit.append(event)
    def audit_valid(self):
        return all(e['n']==i and e['prev']==(self.audit[i-1]['hash'] if i else '0'*64) and e['hash']==digest({k:v for k,v in e.items() if k!='hash'}) for i,e in enumerate(self.audit))
    def head(self,events,epoch):
        if not isinstance(epoch,int) or epoch<0 or not all(isinstance(s,str) and s for s in events):raise ValueError('invalid input')
        h=Head(self.registry,len(events),digest(['events',list(events)]),epoch,b'')
        return Head(h.registry,h.size,h.root,h.epoch,self.registry_sk.sign(h.payload()))
    def valid_head(self,h):
        try:
            if h.registry!=self.registry:return False
            self.registry_pk.verify(h.signature,h.payload())
            return True
        except (InvalidSignature,ValueError,TypeError):return False
    def freeze(self,events,epoch):
        if self.frozen is not None:raise ValueError('already frozen')
        self.frozen_events=tuple(events)
        self.frozen=self.head(events,epoch)
        self._event('freeze',{'root':self.frozen.root,'size':self.frozen.size})
    def decision(self,h,events):
        if self.frozen is None:return 'HOLD_NO_CHECKPOINT'
        if not self.valid_head(h):return 'HOLD_INVALID_SIGNATURE'
        if h.epoch<=self.frozen.epoch:return 'HOLD_STALE_EPOCH'
        if h.size!=len(events) or h.root!=digest(['events',list(events)]):return 'HOLD_SNAPSHOT_MISMATCH'
        if h.size<self.frozen.size:return 'HOLD_ROLLBACK'
        if tuple(events[:self.frozen.size])!=self.frozen_events:return 'QUARANTINE_REWRITTEN_PREFIX'
        if h.size==self.frozen.size:return 'HOLD_NO_EXTENSION'
        return 'PREFIX_VALID'
    def vote(self,w,h):
        if w not in self.witness_sk:raise ValueError('unknown witness')
        v=Vote(w,self.ancestors[w],self.frozen.root,h.root,h.size,h.epoch,b'')
        return Vote(v.witness,v.ancestor,v.old_root,v.new_root,v.new_size,v.epoch,self.witness_sk[w].sign(v.payload()))
    def confirm(self,h,events,votes):
        d=self.decision(h,events)
        if d!='PREFIX_VALID':
            self._event('reject',{'decision':d,'root':h.root})
            return d
        if len(votes)!=3 or {v.witness for v in votes}!=set(self.witness_pk):return 'HOLD_OBSERVER_QUORUM'
        for v in votes:
            if (v.ancestor!=self.ancestors[v.witness] or v.old_root!=self.frozen.root or v.new_root!=h.root or v.new_size!=h.size or v.epoch!=h.epoch):return 'HOLD_OBSERVER_CONTEXT'
            try:self.witness_pk[v.witness].verify(v.signature,v.payload())
            except (InvalidSignature,ValueError,TypeError):return 'HOLD_OBSERVER_SIGNATURE'
        self._event('accept',{'root':h.root,'old_root':self.frozen.root,'size':h.size})
        return 'LOCAL_PREFIX_CERTIFIED'

def demo():
    gate=PrefixGate()
    gate.freeze(('A','B','C'),7)
    honest=('A','B','C','D')
    h=gate.head(honest,8)
    approved=gate.confirm(h,honest,[gate.vote(w,h) for w in ('W1','W2','W3')])
    tampered=('A','X','C','D')
    bad=gate.head(tampered,9)
    rejected=gate.confirm(bad,tampered,[gate.vote(w,bad) for w in ('W1','W2','W3')])
    return {'honest':approved,'rewrite':rejected,'audit_records':len(gate.audit),'valid':gate.audit_valid()}
if __name__=='__main__':print(demo())
