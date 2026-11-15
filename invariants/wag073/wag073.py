"""WAG-073: revocation-safe witness rotation, local Ed25519 demonstration."""
from dataclasses import dataclass
from hashlib import sha256
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
def encode(x):return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def hashof(x):return sha256(encode(x)).hexdigest()
@dataclass(frozen=True)
class Witness:
    name:str
    ancestor:str
    operator:str
    domain:str
    pub:bytes
    @property
    def key_id(self):return sha256(self.pub).hexdigest()
def fresh(name,ancestor,operator,domain):
    sk=Ed25519PrivateKey.generate()
    pk=sk.public_key().public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
    return Witness(name,ancestor,operator,domain,pk),sk
def payload(name,epoch,challenge,snapshot):
    return dict(purpose="WAG-073-recovery-v1",name=name,epoch=epoch,challenge=challenge,snapshot=snapshot)
def signed(sk,x):return sk.sign(encode(x)).hex()
def valid(w,x,s):
    try:
        Ed25519PublicKey.from_public_bytes(w.pub).verify(bytes.fromhex(s),encode(x));return True
    except (ValueError,TypeError,InvalidSignature):return False
class Gate:
    def __init__(self,old,epoch,challenge,snapshot):
        if len(old)!=3 or epoch<0 or not challenge or not snapshot:raise ValueError("invalid genesis")
        self.check_unique(old)
        self.active={w.name:w for w in old}
        self.retired={};self.quarantine=set();self.cert=None;self.review=None
        self.epoch=epoch;self.challenge=challenge;self.snapshot=snapshot;self.events=[]
        self.record("genesis",dict(members=sorted(self.active),epoch=epoch))
    @staticmethod
    def check_unique(ws):
        for prop in ("name","ancestor","operator","domain","key_id"):
            values=[getattr(w,prop) for w in ws]
            if any(not x for x in values) or len(set(values))!=len(values):raise ValueError("duplicate witness or ancestor")
    def record(self,event,data):
        r=dict(seq=len(self.events),prior=self.events[-1]["hash"] if self.events else "0"*64,event=event,data=data)
        r["hash"]=hashof(r);self.events.append(r)
    def verify(self):
        return all(r["seq"]==i and r["prior"]==(self.events[i-1]["hash"] if i else "0"*64) and r["hash"]==hashof({k:v for k,v in r.items() if k!="hash"}) for i,r in enumerate(self.events))
    def equivocation(self,name,a,sa,b,sb):
        if self.cert is not None or name not in self.active:raise ValueError("ineligible signer")
        w=self.active[name]
        if not valid(w,a,sa) or not valid(w,b,sb):raise ValueError("invalid signature")
        for x in (a,b):
            if x.get("purpose")!="WAG-073-recovery-v1" or (x.get("name"),x.get("epoch"),x.get("challenge"))!=(name,self.epoch,self.challenge):raise ValueError("wrong recovery round")
        if not a.get("snapshot") or not b.get("snapshot") or a["snapshot"]==b["snapshot"]:raise ValueError("not conflicting")
        self.cert=dict(name=name,key_id=w.key_id,a=a,sa=sa,b=b,sb=sb)
        self.quarantine.add(name);self.record("equivocation",self.cert)
        return hashof(self.cert)
    def authorize_review(self,reviewer,sk):
        if not self.cert or self.review or reviewer.name not in self.active or reviewer.name in self.quarantine:raise ValueError("review prohibited")
        review=dict(purpose="WAG-073-review-v1",cert=hashof(self.cert),reviewer=reviewer.name,epoch=self.epoch)
        sig=signed(sk,review)
        if not valid(reviewer,review,sig):raise ValueError("bad reviewer signature")
        self.review=(review,sig);self.record("review",dict(body=review,sig=sig))
    def rotate(self,old,new):
        if not self.cert or not self.review or old!=self.cert["name"] or old not in self.quarantine or old not in self.active:raise ValueError("not authorized")
        if new.name in self.active or new.name in self.retired:raise ValueError("duplicate name")
        allw=[*self.active.values(),*self.retired.values()]
        if any(new.ancestor==w.ancestor or new.operator==w.operator or new.domain==w.domain or new.key_id==w.key_id for w in allw):raise ValueError("reused lineage")
        self.check_unique([w for n,w in self.active.items() if n!=old]+[new])
        self.retired[old]=self.active.pop(old);self.active[new.name]=new;self.epoch+=1
        self.challenge=hashof(dict(epoch=self.epoch,prior_challenge=self.challenge,cert=hashof(self.cert),replacement_key=new.key_id))
        self.record("rotation",dict(retired=old,new=new.name,epoch=self.epoch,challenge=self.challenge))
    def certify(self,receipts):
        if not self.retired or len(self.active)!=3 or set(receipts)!=set(self.active) or self.quarantine&set(self.active):raise ValueError("invalid quorum")
        for name,(data,sig) in receipts.items():
            if data!=payload(name,self.epoch,self.challenge,self.snapshot) or not valid(self.active[name],data,sig):raise ValueError("stale or invalid attestation")
        if any(r["event"]=="certify" for r in self.events):raise ValueError("duplicate certification")
        self.record("certify",dict(members=sorted(self.active),epoch=self.epoch,receipts=sorted(hashof([d,s]) for d,s in receipts.values())))
        return "LOCAL_SIGNED_QUORUM_RECONSTITUTED"
    def status(self):
        if self.cert and not self.retired:return "HOLD_EQUIVOCATION"
        if self.retired and not any(e["event"]=="certify" for e in self.events):return "HOLD_FRESH_REATTESTATION"
        return "LOCAL_SIGNED_QUORUM_RECONSTITUTED" if self.retired else "INITIAL_QUORUM_PENDING"
def demo():
    w1,k1=fresh("W1","A","opA","fdA");w2,k2=fresh("W2","B","opB","fdB");w3,k3=fresh("W3","C","opC","fdC");w4,k4=fresh("W4","D","opD","fdD")
    g=Gate([w1,w2,w3],2,"round-7","snapshot-A")
    a=payload("W1",2,"round-7","snapshot-A");b=payload("W1",2,"round-7","snapshot-B")
    g.equivocation("W1",a,signed(k1,a),b,signed(k1,b))
    held=g.status();g.authorize_review(w2,k2);g.rotate("W1",w4);pending=g.status()
    rec={w.name:(payload(w.name,g.epoch,g.challenge,g.snapshot),signed(k,payload(w.name,g.epoch,g.challenge,g.snapshot))) for w,k in ((w2,k2),(w3,k3),(w4,k4))}
    decision=g.certify(rec)
    return dict(before=held,pending=pending,after=decision,members=sorted(g.active),retired=sorted(g.retired),events=len(g.events),verified=g.verify())
if __name__=="__main__":print(demo())
