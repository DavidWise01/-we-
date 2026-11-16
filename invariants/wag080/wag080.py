"""WAG-080 compact reference: one-way signed checkpoint advancement.
Synthetic witness keys and ancestry; caller must independently verify Merkle proof.
"""
from dataclasses import dataclass
from hashlib import sha256
from copy import deepcopy
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

def packed(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def H(x): return sha256(packed(x)).hexdigest()
def ishash(x): return isinstance(x,str) and len(x)==64 and all(c in '0123456789abcdef' for c in x)
class Hold(ValueError): pass
@dataclass(frozen=True)
class Witness:
    name: str
    ancestry: str
    controller: str
    domain: str
    public_key: object
@dataclass(frozen=True)
class Vote:
    signer: str
    receipt_id: str
    signature: bytes
class Gate:
    def __init__(self,witnesses,root,challenge):
        ws=list(witnesses)
        if len(ws)!=3 or len({w.name for w in ws})!=3: raise Hold('WITNESS_COUNT')
        if any(len({getattr(w,k) for w in ws})!=3 for k in ('ancestry','controller','domain')): raise Hold('SHARED_ROOT')
        if not ishash(root) or not ishash(challenge): raise Hold('INVALID_GENESIS')
        self.ws={w.name:w for w in ws}
        self.root,self.challenge,self.epoch=root,challenge,0
        self.used_ids=set();self.used_challenges=set();self.certs=[];self.events=[]
        self.record('genesis',dict(root=root,challenge=challenge,epoch=0))
    def record(self,kind,data):
        e=dict(seq=len(self.events),prev=self.events[-1]['digest'] if self.events else '0'*64,kind=kind,data=deepcopy(data))
        e['digest']=H(e);self.events.append(e)
    def audit_ok(self):
        return all(e['seq']==i and e['prev']==(self.events[i-1]['digest'] if i else '0'*64) and e['digest']==H({k:v for k,v in e.items() if k!='digest'}) for i,e in enumerate(self.events))
    @staticmethod
    def message(old,new,epoch,challenge,proof):
        return packed(dict(domain='WAG-080-advance-v1',old_root=old,new_root=new,epoch=epoch,challenge=challenge,proof_digest=proof))
    def advance(self,old,new,epoch,challenge,proof,votes,proof_verified):
        if old!=self.root:raise Hold('OLD_ROOT_MISMATCH')
        if epoch!=self.epoch:raise Hold('STALE_EPOCH')
        if challenge!=self.challenge or challenge in self.used_challenges:raise Hold('STALE_CHALLENGE')
        if not ishash(new) or new==old or not ishash(proof):raise Hold('INVALID_TRANSITION')
        if proof_verified is not True:raise Hold('INVALID_PROOF')
        votes=list(votes)
        if len(votes)!=3 or {v.signer for v in votes}!=set(self.ws):raise Hold('MISSING_WITNESS')
        ids=[v.receipt_id for v in votes]
        if any(not x or not isinstance(x,str) for x in ids) or len(set(ids))!=3:raise Hold('DUPLICATE_RECEIPT')
        if any(x in self.used_ids for x in ids):raise Hold('REPLAYED_RECEIPT')
        message=self.message(old,new,epoch,challenge,proof)
        for v in votes:
            try:self.ws[v.signer].public_key.verify(v.signature,message)
            except Exception:raise Hold('INVALID_SIGNATURE') from None
        cert=dict(old=old,new=new,epoch=epoch,challenge=challenge,proof=proof,ids=sorted(ids))
        self.certs.append(cert);self.used_ids.update(ids);self.used_challenges.add(challenge)
        self.root=new;self.epoch+=1
        self.challenge=H(dict(domain='WAG-080-next-challenge-v1',challenge=challenge,certificate=H(cert)))
        self.record('advance',dict(cert=cert,epoch=self.epoch,challenge=self.challenge))
        return 'ADVANCED_LOCAL'
def fixtures():
    keys={name:Ed25519PrivateKey.generate() for name in ('W1','W2','W3')}
    ws=[Witness(n,'ancestor-'+n,'operator-'+n,'domain-'+n,k.public_key()) for n,k in keys.items()]
    gate=Gate(ws,H('checkpoint-079'),H('nonce-080'))
    return gate,keys
def votes_for(gate,keys,old,new,epoch,challenge,proof,suffix='a'):
    msg=Gate.message(old,new,epoch,challenge,proof)
    return [Vote(n,n+'-'+suffix,keys[n].sign(msg)) for n in ('W1','W2','W3')]
if __name__=='__main__':
    g,keys=fixtures();old=g.root;challenge=g.challenge;new=H('checkpoint-080');proof=H('proof-080')
    v=votes_for(g,keys,old,new,0,challenge,proof)
    print(g.advance(old,new,0,challenge,proof,v,True))
    try:g.advance(old,new,0,challenge,proof,v,True)
    except Hold as e:print('REPLAY_REJECTED:',e)
    print('EPOCH',g.epoch,'AUDIT_OK',g.audit_ok())
