"""WAG-072: challenge-bound Ed25519 observations and equivocation proofs.
Synthetic witness keys and ancestry; not a Byzantine consensus protocol.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(x):return sha256(canonical(x)).hexdigest()
@dataclass(frozen=True)
class Statement:
    signer:str
    epoch:int
    round_id:str
    challenge:str
    snapshot:str
    signature:str
    def payload(self):
        return {'domain':'WAG-072/snapshot/v1','signer':self.signer,'epoch':self.epoch,'round_id':self.round_id,'challenge':self.challenge,'snapshot':self.snapshot}
    def as_dict(self):return {**self.payload(),'signature':self.signature}
@dataclass(frozen=True)
class Certificate:
    signer:str
    left:Statement
    right:Statement
    def as_dict(self):return {'signer':self.signer,'left':self.left.as_dict(),'right':self.right.as_dict()}
def sign(key,signer,epoch,round_id,challenge,snapshot):
    p={'domain':'WAG-072/snapshot/v1','signer':signer,'epoch':epoch,'round_id':round_id,'challenge':challenge,'snapshot':snapshot}
    return Statement(signer,epoch,round_id,challenge,snapshot,key.sign(canonical(p)).hex())
class EquivocationGate:
    def __init__(self,keys,roots,epoch,round_id,challenge):
        if len(keys)!=3 or set(keys)!=set(roots) or len(set(roots.values()))!=3 or not all(roots.values()):raise ValueError('distinct ancestry roots')
        if epoch<0 or not round_id or len(challenge)<16:raise ValueError('invalid round/challenge')
        self.keys=dict(keys);self.roots=dict(roots);self.epoch=epoch;self.round_id=round_id;self.challenge=challenge
        self.statements={};self.equivocations={};self.quarantined=set();self.ledger=[]
        self._append('genesis',{'epoch':epoch,'round':round_id,'challenge':challenge,'roots':roots})
    def _append(self,event,data):
        r={'seq':len(self.ledger),'prev':self.ledger[-1]['hash'] if self.ledger else '0'*64,'event':event,'data':data}
        r['hash']=digest(r);self.ledger.append(r)
    def verify_ledger(self):
        return all(r['seq']==i and r['prev']==(self.ledger[i-1]['hash'] if i else '0'*64)
                   and r['hash']==digest({k:v for k,v in r.items() if k!='hash'}) for i,r in enumerate(self.ledger))
    def verify_signature(self,s):
        if s.signer not in self.keys:return False
        try:
            self.keys[s.signer].verify(bytes.fromhex(s.signature),canonical(s.payload()))
            return True
        except (InvalidSignature,ValueError,TypeError):return False
    def in_scope(self,s):return s.epoch==self.epoch and s.round_id==self.round_id and s.challenge==self.challenge
    def submit(self,s):
        if not self.verify_signature(s):return 'REJECT_BAD_SIGNATURE'
        if not self.in_scope(s):return 'REJECT_WRONG_CHALLENGE_OR_ROUND'
        old=self.statements.get(s.signer)
        if old is None:
            self.statements[s.signer]=s;self._append('signed_observation',s.as_dict())
            return 'QUARANTINED' if s.signer in self.quarantined else 'RECORDED'
        if old.snapshot==s.snapshot:return 'REPLAY_NO_CHANGE'
        if s.signer not in self.equivocations:
            cert=Certificate(s.signer,old,s)
            self.equivocations[s.signer]=cert;self.quarantined.add(s.signer)
            self._append('equivocation',cert.as_dict())
        return 'QUARANTINE_EQUIVOCATION'
    def verify_certificate(self,c):
        a,b=c.left,c.right
        return a.signer==b.signer==c.signer and self.in_scope(a) and self.in_scope(b) and a.snapshot!=b.snapshot and self.verify_signature(a) and self.verify_signature(b)
    def decision(self):
        if self.quarantined:return 'HOLD_EQUIVOCATION'
        if set(self.statements)!=set(self.keys):return 'HOLD_MISSING_WITNESS'
        if len({s.snapshot for s in self.statements.values()})!=1:return 'HOLD_SNAPSHOT_DISAGREEMENT'
        return 'LOCAL_SIGNED_AGREEMENT'
def demo(equivocate=True):
    keys={n:Ed25519PrivateKey.generate() for n in ('W1','W2','W3')}
    g=EquivocationGate({n:k.public_key() for n,k in keys.items()},{'W1':'root-A','W2':'root-B','W3':'root-C'},2,'recovery-round-7','0123456789abcdef0123456789abcdef')
    for n in keys:g.submit(sign(keys[n],n,2,'recovery-round-7',g.challenge,'snapshot-A'))
    before=g.decision()
    result=g.submit(sign(keys['W1'],'W1',2,'recovery-round-7',g.challenge,'snapshot-B')) if equivocate else 'NO_FORK'
    return g,{'before':before,'fork_submit':result,'after':g.decision(),'certificates':len(g.equivocations),'ledger_entries':len(g.ledger),'ledger_verified':g.verify_ledger()}
if __name__=='__main__':print(json.dumps(demo()[1],indent=2))
