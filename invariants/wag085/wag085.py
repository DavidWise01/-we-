"""WAG-085 compact reference: challenge-bound full-file readback; local simulation only.
The full 35-test validated version is distributed as a conversation artifact.
"""
from pathlib import Path
from hashlib import sha256
from dataclasses import dataclass,replace
import json, sqlite3, os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

def enc(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def H(b):return sha256(b).hexdigest()
@dataclass(frozen=True)
class Challenge:
 epoch:int
 root:str
 nonce:str
 def id(self):return H(enc(['WAG085_CHALLENGE',self.epoch,self.root,self.nonce]))
@dataclass(frozen=True)
class Proof:
 host:str
 challenge_id:str
 content_hash:str
 signature:bytes
 def message(self):return enc(['WAG085_PROOF',self.host,self.challenge_id,self.content_hash])
class Host:
 def __init__(self,name,folder,key):
  self.name=name;self.folder=Path(folder);self.folder.mkdir(parents=True,exist_ok=True);self.key=key
 def persist(self,data):
  f=self.folder/'checkpoint';temp=self.folder/'checkpoint.tmp'
  with temp.open('wb') as out:out.write(data);out.flush();os.fsync(out.fileno())
  os.replace(temp,f)
 def answer(self,challenge):
  data=(self.folder/'checkpoint').read_bytes()
  r=Proof(self.name,challenge.id(),H(data),b'')
  return replace(r,signature=self.key.sign(r.message()))
class Gate:
 def __init__(self,db_path,public_keys,declared_domains,expected_content):
  self.keys=dict(public_keys);self.domains=dict(declared_domains);self.target=H(expected_content)
  if len(self.keys)!=3 or set(self.keys)!=set(self.domains) or len(set(self.domains.values()))!=3:raise ValueError('distinct hosts/domains')
  if any(not x for x in self.domains.values()):raise ValueError('empty domain')
  self.db=str(db_path)
  c=sqlite3.connect(self.db)
  try:
   c.execute('CREATE TABLE IF NOT EXISTS challenge(id TEXT PRIMARY KEY,epoch INTEGER,nonce TEXT UNIQUE,state TEXT)')
   c.execute('CREATE TABLE IF NOT EXISTS receipts(sig TEXT PRIMARY KEY,challenge TEXT,host TEXT)')
   c.commit()
  finally:c.close()
 def register(self,ch):
  if ch.epoch<0 or ch.root!=self.target or not ch.nonce:raise ValueError('bad challenge')
  c=sqlite3.connect(self.db)
  try:
   c.execute('BEGIN IMMEDIATE')
   high=c.execute('SELECT MAX(epoch) FROM challenge').fetchone()[0]
   if high is not None and ch.epoch<high:raise ValueError('rollback')
   c.execute('INSERT INTO challenge VALUES(?,?,?,?)',(ch.id(),ch.epoch,ch.nonce,'OPEN'))
   c.commit()
  except Exception:c.rollback();raise
  finally:c.close()
 def check(self,ch,proofs):
  c=sqlite3.connect(self.db)
  try:
   c.execute('BEGIN IMMEDIATE')
   state=c.execute('SELECT state FROM challenge WHERE id=?',(ch.id(),)).fetchone()
   if state!=('OPEN',):raise ValueError('stale challenge')
   if len(proofs)!=3 or {p.host for p in proofs}!=set(self.keys):raise ValueError('quorum')
   for p in proofs:
    if p.challenge_id!=ch.id() or p.content_hash!=self.target:raise ValueError('bad hash or nonce')
    if c.execute('SELECT 1 FROM receipts WHERE sig=?',(p.signature.hex(),)).fetchone():raise ValueError('replay')
    try:self.keys[p.host].verify(p.signature,p.message())
    except (ValueError,InvalidSignature):raise ValueError('invalid signature')
   for p in proofs:c.execute('INSERT INTO receipts VALUES(?,?,?)',(p.signature.hex(),ch.id(),p.host))
   c.execute("UPDATE challenge SET state='ACCEPTED' WHERE id=?",(ch.id(),))
   c.commit();return 'LOCAL_FRESH_STORAGE_ELIGIBLE'
  except Exception:c.rollback();raise
  finally:c.close()
