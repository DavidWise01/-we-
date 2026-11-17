import json, hashlib, sqlite3
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

def enc(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def root(x): return hashlib.sha256(enc(x)).hexdigest()
def genesis(): return {'generation':0,'balances':[156,0,0],'pending':{},'spent':[],'parent':None}
def total(s): return sum(s['balances'])+sum(p['q'] for p in s['pending'].values())
def step(s,op):
 t=json.loads(enc(s));t['parent']=root(s);t['generation']+=1
 if op['kind']=='send':
  a,b,q,k=[op[x] for x in ('src','dst','q','id')]
  if type(a)!=int or not 0<=a<3 or b!=(a+1)%3 or type(q)!=int or not 0<q<=t['balances'][a] or k in t['pending'] or k in t['spent']:raise ValueError('send')
  t['balances'][a]-=q;t['pending'][k]={'src':a,'dst':b,'q':q}
 elif op['kind']=='receive':
  k=op['id'];p=t['pending'].pop(k,None)
  if p is None:raise ValueError('receipt')
  t['balances'][p['dst']]+=p['q'];t['spent'].append(k)
 elif op['kind']!='graduate':raise ValueError('operation')
 if total(t)!=156:raise ValueError('conservation')
 return t

def statement(mesh,s,op,t):return enc(['WAG124',mesh,root(s),op,root(t)])
def verify(keys,message,cert):
 if len(keys)!=3 or set(keys)!=set(cert) or len({k.public_bytes(Encoding.Raw,PublicFormat.Raw) for k in keys.values()})!=3:raise ValueError('membership')
 try:
  for n,k in keys.items():k.verify(bytes.fromhex(cert[n]),message)
 except (InvalidSignature,ValueError,TypeError):raise ValueError('signature')
class Anchor:
 def __init__(self,path,mesh,keys):
  self.db=sqlite3.connect(path);self.mesh=mesh;self.keys=keys
  self.db.execute('CREATE TABLE IF NOT EXISTS log(g INTEGER PRIMARY KEY, state TEXT, cert TEXT, op TEXT)');self.db.execute('CREATE TABLE IF NOT EXISTS identity(v TEXT PRIMARY KEY)')
  ident=enc([mesh,{n:k.public_bytes(Encoding.Raw,PublicFormat.Raw).hex() for n,k in keys.items()}]).decode()
  old=self.db.execute('SELECT v FROM identity').fetchone()
  if old and old[0]!=ident:raise ValueError('identity')
  if not old:self.db.execute('INSERT INTO identity VALUES(?)',(ident,));self.db.execute('INSERT INTO log VALUES(0,?,NULL,NULL)',(enc(genesis()).decode(),))
  self.db.commit()
 def head(self):return json.loads(self.db.execute('SELECT state FROM log ORDER BY g DESC LIMIT 1').fetchone()[0])
 def append(self,s,op,cert):
  t=step(s,op);verify(self.keys,statement(self.mesh,s,op,t),cert)
  with self.db:
   self.db.execute('BEGIN IMMEDIATE')
   if self.head()!=s:raise ValueError('stale parent')
   self.db.execute('INSERT INTO log VALUES(?,?,?,?)',(t['generation'],enc(t).decode(),enc(cert).decode(),enc(op).decode()))
  return t
 def reconcile(self,local):
  h=self.head()
  if local==h:return 'CURRENT',h
  r=self.db.execute('SELECT state FROM log WHERE g=?',(local['generation'],)).fetchone()
  if r and json.loads(r[0])==local:return 'ROLLBACK_HOLD',h
  return 'FORK_HOLD',h
