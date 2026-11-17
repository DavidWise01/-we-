"""Durable control ancestry pinning: compact reference."""
import sqlite3,json,hashlib
from contextlib import closing
from itertools import combinations
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(x):return hashlib.sha256(canon(x)).hexdigest()
def roots(g,n,active=frozenset()):
 if n in active or n not in g:raise ValueError('unknown/cycle')
 if not isinstance(g[n],list):raise ValueError('parents')
 return {n}.union(*(roots(g,p,active|{n}) for p in g[n]))
def independent(g,actors):
 for n in g:roots(g,n)
 return all(not a&b for a,b in combinations([roots(g,n) for n in actors],2))
class Gate:
 def __init__(self,path,graph,actors,keys):
  self.path=str(path);self.actors=tuple(actors);self.keys=dict(keys)
  if len(keys)!=2 or len(set(keys.values()))!=2 or len(set(actors))!=len(actors) or not independent(graph,actors):raise ValueError('policy')
  p=digest([actors,{n:k.hex() for n,k in keys.items()}])
  with closing(sqlite3.connect(self.path)) as c,c:
   c.execute('CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY,epoch INTEGER,graph TEXT,policy TEXT)')
   c.execute('CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY,body TEXT,hash TEXT)')
   c.execute('INSERT OR IGNORE INTO state VALUES(1,0,?,?)',(canon(graph).decode(),p))
   if c.execute('SELECT policy FROM state').fetchone()[0]!=p:raise ValueError('policy mismatch')
 def state(self):
  with closing(sqlite3.connect(self.path)) as c:
   e,g=c.execute('SELECT epoch,graph FROM state').fetchone();return e,json.loads(g)
 def proposal(self,g):
  e,old=self.state();return {'type':'WAG102/correction','epoch':e,'old':digest(old),'new':digest(g)}
 def evaluate(self,g,p,s):
  g=json.loads(canon(g));p=json.loads(canon(p));s=dict(s)
  with closing(sqlite3.connect(self.path)) as c,c:
   c.execute('BEGIN IMMEDIATE')
   e,old=c.execute('SELECT epoch,graph FROM state').fetchone();old=json.loads(old)
   expected={'type':'WAG102/correction','epoch':e,'old':digest(old),'new':digest(g)}
   status='HOLD_STALE'
   if p==expected:
    if g==old:status='UNCHANGED'
    else:
     try:
      if not independent(g,self.actors):status='HOLD_SHARED_CONTROL'
      elif set(s)!=set(self.keys):status='HOLD_CORROBORATION'
      else:
       for n,k in self.keys.items():Ed25519PublicKey.from_public_bytes(k).verify(s[n],canon(p))
       c.execute('UPDATE state SET epoch=?,graph=?',(e+1,canon(g).decode()));status='LOCAL_CORRECTION_ACCEPTED'
     except (InvalidSignature,TypeError):status='HOLD_SIGNATURE'
     except (ValueError,RecursionError):status='HOLD_ANCESTRY'
   prev=c.execute('SELECT seq,hash FROM audit ORDER BY seq DESC LIMIT 1').fetchone()
   seq=prev[0]+1 if prev else 0
   body={'seq':seq,'previous':prev[1] if prev else '0'*64,'status':status,'old_graph':old,'candidate':g,'proposal':p,'signatures':{n:v.hex() for n,v in s.items()}}
   c.execute('INSERT INTO audit VALUES(?,?,?)',(seq,canon(body).decode(),digest(body)));return status
 def verify_audit(self):
  with closing(sqlite3.connect(self.path)) as c:
   prev='0'*64
   for i,(seq,body,h) in enumerate(c.execute('SELECT seq,body,hash FROM audit ORDER BY seq')):
    b=json.loads(body)
    if seq!=i or b['seq']!=i or b['previous']!=prev or digest(b)!=h:return False
    prev=h
   return True
