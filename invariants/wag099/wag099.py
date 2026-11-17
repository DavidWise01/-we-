"""WAG-099: local pinned gossip, fresh nonce, revocation-aware signatures."""
import sqlite3,json,hashlib
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def digest(v):return hashlib.sha256(canonical(v)).hexdigest()
@dataclass(frozen=True)
class Head:
 size:int
 root:str
 epoch:int
@dataclass(frozen=True)
class Witness:
 name:str
 ancestor:str
 domain:str
 public:object
class Gate:
 def __init__(self,path,witnesses,pinned,nonce):
  self.pinned=pinned;self.nonce=nonce;self.ws={w.name:w for w in witnesses}
  if len(self.ws)!=3 or len({w.ancestor for w in witnesses})!=3 or len({w.domain for w in witnesses})!=3:raise ValueError('independent declared labels')
  self.db=sqlite3.connect(path)
  self.db.execute('CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY,kind TEXT,body TEXT,prior TEXT,hash TEXT)')
  self.db.execute('CREATE TABLE IF NOT EXISTS revoked(name TEXT PRIMARY KEY,epoch INTEGER)')
  self.db.execute('CREATE TABLE IF NOT EXISTS observations(name TEXT PRIMARY KEY,epoch INTEGER,size INTEGER,root TEXT,nonce TEXT,signature BLOB)')
  self.db.commit()
  if not self.db.execute('SELECT 1 FROM events LIMIT 1').fetchone():self.event('genesis',{'root':pinned.root,'epoch':pinned.epoch,'size':pinned.size})
 def event(self,kind,body):
  last=self.db.execute('SELECT seq,hash FROM events ORDER BY seq DESC LIMIT 1').fetchone();seq=last[0]+1 if last else 0;prior=last[1] if last else '0'*64
  rec={'seq':seq,'kind':kind,'body':body,'prior':prior}
  self.db.execute('INSERT INTO events VALUES (?,?,?,?,?)',(seq,kind,canonical(body).decode(),prior,digest(rec)));self.db.commit()
 def statement(self,name,head,nonce=None):return canonical({'domain':'WAG099/gossip','name':name,'head':vars(head),'nonce':nonce or self.nonce})
 def revoked(self,name,epoch):
  x=self.db.execute('SELECT epoch FROM revoked WHERE name=?',(name,)).fetchone()
  return bool(x and epoch>=x[0])
 def revoke(self,name,epoch):
  if name not in self.ws or epoch<0 or self.db.execute('SELECT 1 FROM revoked WHERE name=?',(name,)).fetchone():raise ValueError('revocation')
  self.db.execute('INSERT INTO revoked VALUES (?,?)',(name,epoch));self.event('revoke',{'name':name,'epoch':epoch})
 def observe(self,name,head,sig,nonce=None):
  nonce=nonce or self.nonce
  if name not in self.ws:return 'REJECT_UNKNOWN'
  try:self.ws[name].public.verify(sig,self.statement(name,head,nonce))
  except (InvalidSignature,TypeError,ValueError):return 'REJECT_SIGNATURE'
  if nonce!=self.nonce or head.epoch!=self.pinned.epoch or head.size!=self.pinned.size:return 'HOLD_STALE'
  if self.revoked(name,head.epoch):return 'HOLD_REVOKED'
  if head.root!=self.pinned.root:
   self.event('signed_conflict',{'name':name,'head':vars(head)})
   return 'QUARANTINE_CONFLICT'
  if self.db.execute('SELECT 1 FROM observations WHERE name=?',(name,)).fetchone():return 'REJECT_REPLAY'
  self.db.execute('INSERT INTO observations VALUES (?,?,?,?,?,?)',(name,head.epoch,head.size,head.root,nonce,sig))
  self.event('observe',{'name':name,'root':head.root});return 'RECORDED'
 def certify(self):
  if self.db.execute("SELECT 1 FROM events WHERE kind='signed_conflict' LIMIT 1").fetchone():return 'QUARANTINE_CONFLICT'
  rows=self.db.execute('SELECT name,epoch,size,root,nonce FROM observations').fetchall()
  if len(rows)!=3:return 'HOLD_QUORUM'
  if any(self.revoked(name,self.pinned.epoch) for name,*_ in rows):return 'HOLD_REVOKED'
  if any((e,s,r,n)!=(self.pinned.epoch,self.pinned.size,self.pinned.root,self.nonce) for _,e,s,r,n in rows):return 'HOLD_STALE'
  return 'LOCAL_CURRENT_AGREEMENT'
 def historical_signature(self,name,head,nonce,sig):
  try:self.ws[name].public.verify(sig,self.statement(name,head,nonce));return True
  except (KeyError,InvalidSignature,TypeError,ValueError):return False
 def verify(self):
  prior='0'*64
  for i,(seq,kind,body,p,h) in enumerate(self.db.execute('SELECT seq,kind,body,prior,hash FROM events ORDER BY seq')):
   if seq!=i or p!=prior or digest({'seq':seq,'kind':kind,'body':json.loads(body),'prior':p})!=h:return False
   prior=h
  return True
 def close(self):self.db.close()
def demo():
 keys={n:Ed25519PrivateKey.generate() for n in ('W1','W2','W3')}
 ws=[Witness(n,n+'-root',n+'-domain',k.public_key()) for n,k in keys.items()]
 head=Head(3,'a'*64,99);g=Gate(':memory:',ws,head,'nonce-99')
 for name,key in keys.items():assert g.observe(name,head,key.sign(g.statement(name,head)))=='RECORDED'
 before=g.certify();sig=keys['W1'].sign(g.statement('W1',head))
 g.revoke('W1',99);after=g.certify()
 result={'before':before,'after':after,'historically_valid':g.historical_signature('W1',head,'nonce-99',sig),'audit_valid':g.verify()}
 g.close();return result
if __name__=='__main__':print(json.dumps(demo(),indent=2))
