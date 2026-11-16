"""WAG-097 repository reference: Ed25519 signed gossip and same-size fork quarantine.
Full 44-test local implementation is separately linked in conversation.
Source roots, failure domains and signing keys are simulated declarations.
"""
import hashlib,json,sqlite3
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
def leaf(x):return hashlib.sha256(b'\0'+x).digest()
def branch(a,b):return hashlib.sha256(b'\1'+a+b).digest()
def root(items):
 if not items:return sha(b'')
 def calc(xs):
  if len(xs)==1:return leaf(xs[0])
  k=1<<((len(xs)-1).bit_length()-1)
  return branch(calc(xs[:k]),calc(xs[k:]))
 return calc(items).hex()
class Pair:
 def __init__(self):self.key=Ed25519PrivateKey.generate();self.public=self.key.public_key()
 def sign(self,obj):return self.key.sign(canon(obj)).hex()
def head(log_key,log_id,epoch,items):
 body={'log_id':log_id,'epoch':epoch,'size':len(items),'root':root(items)}
 return {'head':body,'signature':log_key.sign(body)}
def gossip(witness_key,name,signed_head):
 body={'observer':name,'head':signed_head['head']}
 return {'gossip':body,'signature':witness_key.sign(body)}
class Gate:
 def __init__(self,path,log_public,witness_public,log_id='registry-a',epoch=97):
  if len(witness_public)!=3:raise ValueError('three witnesses')
  self.path=path;self.log_key=log_public;self.keys=witness_public;self.id=log_id;self.epoch=epoch
  with self.db() as c:
   c.execute('CREATE TABLE IF NOT EXISTS evidence(seq INTEGER PRIMARY KEY,kind TEXT,payload TEXT,prev TEXT,hash TEXT)')
   c.execute('CREATE TABLE IF NOT EXISTS heads(observer TEXT,size INTEGER,root TEXT,PRIMARY KEY(observer,size,root))')
   c.execute('CREATE TABLE IF NOT EXISTS state(k TEXT PRIMARY KEY,v TEXT)')
   c.execute("INSERT OR IGNORE INTO state VALUES('decision','HOLD_NO_QUORUM')")
 def db(self):return sqlite3.connect(self.path)
 def decision(self):
  c=self.db()
  try:return c.execute("SELECT v FROM state WHERE k='decision'").fetchone()[0]
  finally:c.close()
 def record(self,c,kind,payload):
  prev=c.execute('SELECT hash FROM evidence ORDER BY seq DESC LIMIT 1').fetchone()
  prev=prev[0] if prev else '0'*64
  d=sha(canon({'kind':kind,'payload':payload,'prev':prev}))
  c.execute('INSERT INTO evidence(kind,payload,prev,hash) VALUES(?,?,?,?)',(kind,canon(payload).decode(),prev,d))
 def observe(self,name,items,signed_head,signed_gossip,old_items=None,old_head=None):
  if name not in self.keys:raise ValueError('unknown observer')
  expected={'log_id':self.id,'epoch':self.epoch,'size':len(items),'root':root(items)}
  if signed_head['head']!=expected or signed_gossip['gossip']!={'observer':name,'head':expected}:raise ValueError('head or gossip mismatch')
  try:
   self.log_key.verify(bytes.fromhex(signed_head['signature']),canon(expected))
   self.keys[name].verify(bytes.fromhex(signed_gossip['signature']),canon(signed_gossip['gossip']))
  except (InvalidSignature,ValueError) as e:raise ValueError('signature invalid') from e
  if (old_items is None)!=(old_head is None):raise ValueError('incomplete extension proof')
  rewrite=False
  if old_head is not None:
   prior={'log_id':self.id,'epoch':self.epoch,'size':len(old_items),'root':root(old_items)}
   self.log_key.verify(bytes.fromhex(old_head['signature']),canon(prior))
   if old_head['head']!=prior:raise ValueError('old head mismatch')
   rewrite=tuple(items[:len(old_items)])!=tuple(old_items) or len(items)<len(old_items)
  c=self.db()
  try:
   c.execute('BEGIN IMMEDIATE')
   other=c.execute('SELECT observer,size,root FROM heads').fetchall()
   fork=any(size==len(items) and oldroot!=expected['root'] for _,size,oldroot in other)
   rollback=any(observer==name and size>len(items) for observer,size,_ in other)
   c.execute('INSERT OR IGNORE INTO heads VALUES(?,?,?)',(name,len(items),expected['root']))
   self.record(c,'OBSERVE',{'observer':name,'head':expected})
   status=self.decision() if False else c.execute("SELECT v FROM state WHERE k='decision'").fetchone()[0]
   if fork or rewrite:
    self.record(c,'FORK' if fork else 'PREFIX_REWRITE',{'observer':name,'head':expected,'other':other})
    status='QUARANTINE_SPLIT_VIEW' if fork else 'QUARANTINE_PREFIX_REWRITE'
   elif rollback:status='HOLD_ROLLBACK'
   elif any(s!=len(items) for _,s,_ in other) and old_head is None:status='HOLD_UNPROVEN_CONTINUITY'
   elif not status.startswith('QUARANTINE'):
    matching={n for n,s,r in other if s==len(items) and r==expected['root']}
    matching.add(name)
    status='LOCAL_AGREEMENT' if len(matching)==3 else 'HOLD_INCOMPLETE_GOSSIP'
   c.execute("UPDATE state SET v=? WHERE k='decision'",(status,))
   c.commit();return status
  except:c.rollback();raise
  finally:c.close()
