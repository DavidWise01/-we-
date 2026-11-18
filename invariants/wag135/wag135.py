import json,hashlib,sqlite3
from contextlib import closing
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def root(x):return hashlib.sha256(enc(x)).hexdigest()
def keybytes(x):
 b=bytes.fromhex(x)
 if len(b)!=32 or x!=b.hex():raise ValueError('noncanonical key')
 return b
def validate(m):
 if set(m)!=set('HON') or len({keybytes(k) for k in m.values()})!=3:raise ValueError('membership')
def verify(m,body,cert):
 if set(cert)!=set(m):raise ValueError('quorum')
 for n,k in m.items():Ed25519PublicKey.from_public_bytes(keybytes(k)).verify(bytes.fromhex(cert[n]),enc(body))
def transition(s,o):
 t=json.loads(enc(s));t['seq']+=1;k=o['kind']
 if k=='rotate':
  m=o['members'];validate(m)
  if set(m.values())&set(t['retired']):raise ValueError('retired')
  t['retired']=sorted(set(t['retired'])|(set(t['members'].values())-set(m.values())));t['members']=m;t['epoch']+=1
 elif k=='send':
  a,b,q,p=[o[x] for x in ('src','dst','q','id')]
  if type(a)!=int or not 0<=a<3 or b!=(a+1)%3 or type(q)!=int or not 0<q<=t['q'][a] or p in t['pending'] or p in t['spent']:raise ValueError('send')
  t['q'][a]-=q;t['pending'][p]=[b,q]
 elif k=='receive':
  p=o['id'];b,q=t['pending'].pop(p);t['q'][b]+=q;t['spent'].append(p)
 else:raise ValueError('kind')
 if sum(t['q'])+sum(q for b,q in t['pending'].values())!=156:raise ValueError('conservation')
 return t
def proposal(s,o):return ['WAG135',s['mesh'],root(s),o,root(transition(s,o))]
class Gate:
 def __init__(self,path,mesh,members):
  self.path=path;validate(members);self.genesis={'mesh':mesh,'seq':0,'epoch':0,'members':members,'retired':[],'q':[156,0,0],'pending':{},'spent':[]}
  with closing(self.open()) as c:
   c.execute('BEGIN IMMEDIATE');c.execute('CREATE TABLE IF NOT EXISTS head(id INTEGER PRIMARY KEY,body TEXT,genesis TEXT)');c.execute('CREATE TABLE IF NOT EXISTS journal(seq INTEGER PRIMARY KEY,body TEXT)');c.execute('INSERT OR IGNORE INTO head VALUES(1,?,?)',(enc(self.genesis).decode(),root(self.genesis)))
   if c.execute('SELECT genesis FROM head').fetchone()[0]!=root(self.genesis):raise ValueError('genesis')
   c.commit()
 def open(self):
  c=sqlite3.connect(self.path,timeout=10);c.execute('PRAGMA synchronous=FULL');return c
 def head(self):
  with closing(self.open()) as c:return json.loads(c.execute('SELECT body FROM head').fetchone()[0])
 def commit(self,p,old,new=None):
  with closing(self.open()) as c:
   c.execute('BEGIN IMMEDIATE');s=json.loads(c.execute('SELECT body FROM head').fetchone()[0])
   if p!=proposal(s,p[3]):raise ValueError('stale or modified proposal')
   verify(s['members'],['approve',p],old);t=transition(s,p[3])
   if p[3]['kind']=='rotate':verify(t['members'],['accept',p],new or {})
   c.execute('INSERT INTO journal VALUES(?,?)',(t['seq'],enc([p,old,new]).decode()));c.execute('UPDATE head SET body=?',(enc(t).decode(),));c.commit();return t
