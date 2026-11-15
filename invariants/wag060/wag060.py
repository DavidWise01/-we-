"""WAG-060: partition recovery bound to immutable pre-partition tree head.
Demonstration: authenticated fixture keys and disclosed histories, not independently
witnessed compact transparency consistency proofs.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()

def merkle_root(leaves):
    if not leaves:return sha256(b'EMPTY-WAG060').hexdigest()
    nodes=[sha256(b'\x00'+x.encode()).digest() for x in leaves]
    while len(nodes)>1:
        nodes=[sha256(b'\x01'+nodes[i]+nodes[i+1]).digest() if i+1<len(nodes) else nodes[i]
               for i in range(0,len(nodes),2)]
    return nodes[0].hex()

def head_message(log_id,leaves,epoch):
    return canonical({'domain':'WAG060:head:v1','log_id':log_id,'size':len(leaves),
                      'root':merkle_root(leaves),'epoch':epoch})

@dataclass(frozen=True)
class Head:
    log_id:str
    leaves:tuple
    epoch:int
    signature:str
    @property
    def root(self):return merkle_root(self.leaves)

class RecoveryGate:
    def __init__(self,log_id,operator_public_hex,max_age=5):
        if not log_id or not operator_public_hex or type(max_age)!=int or max_age<0:raise ValueError('policy')
        self.log_id,self.key,self.max_age=log_id,operator_public_hex,max_age
        self.history=[];self.frozen=None;self.status='INITIAL';self.forks=[]
        self._append('policy',{'log_id':log_id,'max_age':max_age})
    def _append(self,kind,payload):
        r={'seq':len(self.history),'prev':self.history[-1]['hash'] if self.history else '0'*64,
           'kind':kind,'payload':payload}
        r['hash']=sha256(canonical(r)).hexdigest();self.history.append(r)
    def verify_history(self):
        return all(r['seq']==i and r['prev']==(self.history[i-1]['hash'] if i else '0'*64)
                   and r['hash']==sha256(canonical({k:v for k,v in r.items() if k!='hash'})).hexdigest()
                   for i,r in enumerate(self.history))
    def _verify_head(self,h):
        if not isinstance(h,Head) or h.log_id!=self.log_id or type(h.epoch)!=int or h.epoch<0 or not h.leaves or not all(isinstance(x,str) and x for x in h.leaves):
            raise ValueError('invalid head')
        try:
            pk=Ed25519PublicKey.from_public_bytes(bytes.fromhex(self.key))
            pk.verify(bytes.fromhex(h.signature),head_message(h.log_id,h.leaves,h.epoch))
        except (ValueError,InvalidSignature):
            raise ValueError('invalid signature')
    def freeze(self,h):
        if self.frozen is not None:raise ValueError('already frozen')
        self._verify_head(h);self.frozen=h;self.status='CURRENT'
        self._append('freeze',{'root':h.root,'size':len(h.leaves),'epoch':h.epoch,'signature':h.signature})
    def partition(self,reason):
        if self.frozen is None or self.status!='CURRENT' or not reason:raise ValueError('partition')
        self.status='HOLD_PARTITION'
        self._append('partition',{'reason':reason,'frozen_root':self.frozen.root})
    def known_fork(self,conflicting_root):
        if self.frozen is None or not conflicting_root:raise ValueError('fork')
        self.forks.append(conflicting_root);self.status='QUARANTINE_FORK'
        self._append('fork',{'conflict':conflicting_root})
    def reconnect(self,h,now):
        if self.status not in ('HOLD_PARTITION','HOLD_AWAITING_PROOF') or self.frozen is None:raise ValueError('not awaiting reconnection')
        self._verify_head(h)
        if type(now)!=int or now<h.epoch:raise ValueError('invalid time')
        old=self.frozen
        if h.epoch<old.epoch or len(h.leaves)<len(old.leaves):decision='HOLD_ROLLBACK'
        elif h.leaves[:len(old.leaves)]!=old.leaves:decision='QUARANTINE_FORK'
        elif self.forks:decision='QUARANTINE_FORK'
        elif now-h.epoch>self.max_age:decision='HOLD_STALE'
        else:decision='RESTORED'
        self._append('reconnect',{'new_root':h.root,'new_size':len(h.leaves),'epoch':h.epoch,
                                  'frozen_root':old.root,'decision':decision})
        if decision=='RESTORED':
            self.frozen=h;self.status='CURRENT'
            self._append('restore',{'old_root':old.root,'root':h.root,'size':len(h.leaves)})
        elif decision=='QUARANTINE_FORK':self.status='QUARANTINE_FORK'
        else:self.status='HOLD_AWAITING_PROOF'
        return decision
def demonstration():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    key=Ed25519PrivateKey.generate()
    pub=key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()
    def signed(leaves,epoch):
        return Head('log-A',tuple(leaves),epoch,key.sign(head_message('log-A',tuple(leaves),epoch)).hex())
    gate=RecoveryGate('log-A',pub)
    gate.freeze(signed(('a','b','c'),10));gate.partition('network partition')
    return gate,gate.reconnect(signed(('a','b','c','d'),13),14)
if __name__=='__main__':
    g,r=demonstration()
    print(json.dumps({'decision':r,'records':len(g.history),'current_root':g.frozen.root,'verified':g.verify_history()},indent=2))
