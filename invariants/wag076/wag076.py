"""WAG-076 compact signed ancestry reference. Registry identities are declared."""
import json,hashlib
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from cryptography.exceptions import InvalidSignature
def encode(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def sha(v):return hashlib.sha256(encode(v)).hexdigest()
def make_key():
 k=Ed25519PrivateKey.generate()
 return k,k.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
@dataclass(frozen=True)
class Registry:
 name:str
 ancestor:str
 operator:str
 domain:str
 key_id:str
 public:bytes
@dataclass(frozen=True)
class Claim:
 registry:str
 subject:str
 parent:str
 epoch:int
 challenge:str
 signature:bytes
 def payload(self):return dict(version="WAG-076-v1",registry=self.registry,subject=self.subject,parent=self.parent,epoch=self.epoch,challenge=self.challenge)
def sign(key,registry,subject,parent,epoch,challenge):
 x=Claim(registry,subject,parent,epoch,challenge,b'')
 return Claim(registry,subject,parent,epoch,challenge,key.sign(encode(x.payload())))
class Gate:
 def __init__(self,registries,excluded,epoch,challenge,subject="W4"):
  self.registries={r.name:r for r in registries}
  if len(registries)<2 or len(self.registries)!=len(registries):raise ValueError("registries")
  for attr in ("ancestor","operator","domain","key_id"):
   vals=[getattr(r,attr) for r in registries]
   if any(not x for x in vals) or len(set(vals))!=len(vals):raise ValueError("shared declared control")
  if not subject or not challenge or epoch<0:raise ValueError("scope")
  self.subject=subject;self.epoch=epoch;self.challenge=challenge;self.excluded=set(excluded)
  self.claims=[];self.records=[]
  self.append("genesis",dict(subject=subject,epoch=epoch,challenge=challenge))
 def append(self,kind,data):
  entry=dict(seq=len(self.records),previous=self.records[-1]["hash"] if self.records else "0"*64,kind=kind,data=data)
  entry["hash"]=sha(entry);self.records.append(entry)
 def verify_history(self):
  return all(r["seq"]==i and r["previous"]==(self.records[i-1]["hash"] if i else "0"*64) and r["hash"]==sha({k:v for k,v in r.items() if k!="hash"}) for i,r in enumerate(self.records))
 def submit(self,c):
  if not isinstance(c,Claim) or c.registry not in self.registries:raise ValueError("signer")
  if (c.subject,c.epoch,c.challenge)!=(self.subject,self.epoch,self.challenge) or not c.parent:raise ValueError("scope")
  try:Ed25519PublicKey.from_public_bytes(self.registries[c.registry].public).verify(c.signature,encode(c.payload()))
  except (InvalidSignature,ValueError):raise ValueError("signature") from None
  self.claims.append(c);self.append("claim",dict(payload=c.payload(),signature=c.signature.hex()))
  return self.status()
 def status(self):
  seen={}
  for c in self.claims:seen.setdefault(c.registry,set()).add(c.parent)
  if any(len(v)>1 for v in seen.values()):return "QUARANTINE_EQUIVOCATION"
  roots={c.parent for c in self.claims}
  if len(roots)>1:return "HOLD_REGISTRY_CONFLICT"
  if len(seen)<2:return "HOLD_INSUFFICIENT_REGISTRIES"
  if next(iter(roots)) in self.excluded:return "HOLD_COMPROMISED_ANCESTRY"
  return "ELIGIBLE_DECLARED_ANCESTRY"
 def freeze(self):
  x=self.status();self.append("freeze",dict(decision=x,claim_count=len(self.claims)));return x
def demo():
 a,pa=make_key();b,pb=make_key()
 rs=[Registry("A","RA","OA","DA","KA",pa),Registry("B","RB","OB","DB","KB",pb)]
 g=Gate(rs,{"ORG-X"},2,"nonce");g.submit(sign(a,"A","W4","ORG-W",2,"nonce"));g.submit(sign(b,"B","W4","ORG-W",2,"nonce"))
 h=Gate(rs,{"ORG-X"},2,"nonce");h.submit(sign(a,"A","W4","ORG-W",2,"nonce"));h.submit(sign(b,"B","W4","ORG-X",2,"nonce"))
 return dict(matching=g.freeze(),conflicting=h.freeze(),audit_valid=g.verify_history() and h.verify_history(),records=[len(g.records),len(h.records)])
if __name__=="__main__":print(demo())
