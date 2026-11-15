"""WAG-071 signed recovery snapshot gate. Ed25519 test keys; no external attestation."""
from dataclasses import dataclass
from hashlib import sha256
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def hashof(v):return sha256(canon(v)).hexdigest()
def ishash(s):return isinstance(s,str) and len(s)==64 and all(x in '0123456789abcdef' for x in s)
def payload(name,epoch,snapshot,nonce):return canon({'protocol':'WAG-071/SNAPSHOT/v1','name':name,'epoch':epoch,'snapshot_hash':snapshot,'nonce':nonce})
@dataclass(frozen=True)
class Witness:
 name:str
 ancestor:str
 domain:str
 public_key:bytes
@dataclass(frozen=True)
class Report:
 name:str
 epoch:int
 snapshot_hash:str
 nonce:str
 signature:bytes
def sign(key,name,epoch,snapshot,nonce):return Report(name,epoch,snapshot,nonce,key.sign(payload(name,epoch,snapshot,nonce)))
class Gate:
 def __init__(self,witnesses,epoch,snapshot,verified=True):
  self.ws=tuple(witnesses)
  if len(self.ws)!=3:raise ValueError('three witnesses')
  for field in ('name','ancestor','domain','public_key'):
   v=[getattr(w,field) for w in self.ws]
   if len(set(v))!=3 or not all(v):raise ValueError('unique identities and ancestry')
  if not isinstance(epoch,int) or epoch<0 or not ishash(snapshot):raise ValueError('checkpoint')
  self.epoch,self.snapshot,self.verified=epoch,snapshot,verified
  self.byname={w.name:w for w in self.ws};self.reports=[];self.nonces=set();self.audit=[]
  self.record('genesis',{'epoch':epoch,'hash':snapshot})
 def record(self,kind,data):
  v={'index':len(self.audit),'prior':self.audit[-1]['digest'] if self.audit else '0'*64,'kind':kind,'data':data}
  v['digest']=hashof(v);self.audit.append(v)
 def audit_ok(self):
  return all(v['index']==i and v['prior']==(self.audit[i-1]['digest'] if i else '0'*64) and v['digest']==hashof({k:x for k,x in v.items() if k!='digest'}) for i,v in enumerate(self.audit))
 def submit(self,r):
  if not isinstance(r,Report) or r.name not in self.byname:raise ValueError('identity')
  if r.epoch!=self.epoch:raise ValueError('epoch')
  if not ishash(r.snapshot_hash) or not isinstance(r.nonce,str) or not r.nonce:raise ValueError('snapshot/nonce')
  if r.nonce in self.nonces or any(v.name==r.name for v in self.reports):raise ValueError('replay')
  try:Ed25519PublicKey.from_public_bytes(self.byname[r.name].public_key).verify(r.signature,payload(r.name,r.epoch,r.snapshot_hash,r.nonce))
  except (ValueError,TypeError) as e:raise ValueError('signature') from e
  except Exception as e:raise ValueError('signature') from e
  self.reports.append(r);self.nonces.add(r.nonce)
  self.record('signed',{'name':r.name,'epoch':r.epoch,'snapshot':r.snapshot_hash,'nonce':r.nonce,'signature':r.signature.hex()})
  return self.status()
 def status(self):
  if not self.verified:return 'HOLD_UNVERIFIED_INFRASTRUCTURE'
  if any(r.snapshot_hash!=self.snapshot for r in self.reports):return 'QUARANTINE_SNAPSHOT_CONFLICT'
  if len(self.reports)<3:return 'HOLD_INCOMPLETE_QUORUM'
  return 'LOCAL_SIGNED_QUORUM_ACCEPTED'
def demo(conflict=True):
 from cryptography.hazmat.primitives import serialization
 keys=[Ed25519PrivateKey.from_private_bytes(bytes([i])*32) for i in (3,4,5)]
 ws=[Witness('W'+str(i+1),chr(65+i),'domain-'+str(i+1),keys[i].public_key().public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)) for i in range(3)]
 s=hashof({'epoch':2,'power':'verified'});g=Gate(ws,2,s)
 for i in range(3):
  observed=hashof('conflict') if i==2 and conflict else s
  g.submit(sign(keys[i],ws[i].name,2,observed,'fresh-'+str(i)))
 return g
if __name__=='__main__':
 g=demo()
 print(json.dumps({'decision':g.status(),'reports':len(g.reports),'records':len(g.audit),'audit_ok':g.audit_ok()},indent=2))
