import sqlite3,json,hashlib,secrets
from contextlib import closing
from cryptography.exceptions import InvalidSignature

def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def root(x):return hashlib.sha256(enc(x)).hexdigest()
def genesis():return {'g':0,'q':[156,0,0],'pending':{},'spent':[]}
def step(s,o):
 t=json.loads(enc(s));t['g']+=1;k=o['kind']
 if k=='send':
  a,b,q,p=[o[x] for x in ('src','dst','q','id')]
  if type(a)!=int or not 0<=a<3 or b!=(a+1)%3 or type(q)!=int or not 0<q<=t['q'][a] or p in t['pending'] or p in t['spent']:raise ValueError('send')
  t['q'][a]-=q;t['pending'][p]=[b,q]
 elif k=='receive':
  p=o['id'];b,q=t['pending'].pop(p);t['q'][b]+=q;t['spent'].append(p)
 elif k!='graduate':raise ValueError('kind')
 if sum(t['q'])+sum(q for b,q in t['pending'].values())!=156:raise ValueError('conservation')
 return t
class Gate:
 def __init__(self,path,mesh,key,keys):
  self.path=path;self.mesh=mesh;self.key=key;self.keys=keys
  from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
  raw=lambda k:k.public_bytes(Encoding.Raw,PublicFormat.Raw).hex()
  if len(keys)!=3 or len(set(map(raw,keys.values())))!=3:raise ValueError('membership')
  identity=enc([mesh,raw(key.public_key()),{n:raw(k) for n,k in keys.items()}]).decode()
  with closing(self.open()) as c:
   c.execute('BEGIN IMMEDIATE');c.execute('CREATE TABLE IF NOT EXISTS head(id INTEGER PRIMARY KEY, state TEXT, identity TEXT)');c.execute('CREATE TABLE IF NOT EXISTS events(g INTEGER PRIMARY KEY, nonce TEXT UNIQUE, receipt TEXT)');c.execute('INSERT OR IGNORE INTO head VALUES(1,?,?)',(enc(genesis()).decode(),identity))
   if c.execute('SELECT identity FROM head').fetchone()[0]!=identity:raise ValueError('identity')
   c.commit()
 def open(self):
  c=sqlite3.connect(self.path,timeout=10);c.execute('PRAGMA synchronous=FULL');return c
 def head(self):
  with closing(self.open()) as c:return json.loads(c.execute('SELECT state FROM head').fetchone()[0])
 def proposal(self,o):
  s=self.head();return ['WAG128',self.mesh,secrets.token_hex(32),root(s),o,root(step(s,o))]
 def commit(self,p,cert):
  if len(p)!=6 or p[:2]!=['WAG128',self.mesh] or set(cert)!=set(self.keys):raise ValueError('scope or membership')
  for n,k in self.keys.items():k.verify(bytes.fromhex(cert[n]),enc(p))
  with closing(self.open()) as c:
   c.execute('BEGIN IMMEDIATE');s=json.loads(c.execute('SELECT state FROM head').fetchone()[0]);old=c.execute('SELECT receipt FROM events WHERE nonce=?',(p[2],)).fetchone()
   if old:
    r=json.loads(old[0]);
    if r[0][2]!=root(p):raise ValueError('nonce conflict')
    return r
   if root(s)!=p[3]:raise ValueError('stale parent')
   t=step(s,p[4])
   if root(t)!=p[5]:raise ValueError('wrong result')
   body=['WAG128-commit',self.mesh,root(p),t['g'],root(t)];r=[body,self.key.sign(enc(body)).hex()]
   c.execute('INSERT INTO events VALUES(?,?,?)',(t['g'],p[2],enc(r).decode()));c.execute('UPDATE head SET state=?',(enc(t).decode(),));c.commit();return r
