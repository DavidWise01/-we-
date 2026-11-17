"""Three retained signed chains; trusted read channels, fail closed."""
import json, hashlib, sqlite3
from contextlib import closing
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

def enc(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def root(x): return hashlib.sha256(enc(x)).hexdigest()
def genesis(): return {'g':0,'balances':[156,0,0],'pending':{},'spent':[]}
def step(s,o):
 t=json.loads(enc(s));t['g']+=1;k=o['kind']
 if k=='send':
  a,b,q,p=[o[x] for x in ('src','dst','q','id')]
  if type(a)!=int or not 0<=a<3 or b!=(a+1)%3 or type(q)!=int or not 0<q<=t['balances'][a] or not isinstance(p,str) or p in t['pending'] or p in t['spent']:raise ValueError('send')
  t['balances'][a]-=q;t['pending'][p]=[b,q]
 elif k=='receive':
  p=o['id'];b,q=t['pending'].pop(p);t['balances'][b]+=q;t['spent'].append(p)
 elif k!='graduate':raise ValueError('kind')
 assert sum(t['balances'])+sum(q for b,q in t['pending'].values())==156
 return t
def message(mesh,s,o):return ['WAG125',mesh,root(s),o,root(step(s,o))]
def replay(mesh,keys,chain):
 if len(keys)!=3 or len({k.public_bytes(Encoding.Raw,PublicFormat.Raw) for k in keys.values()})!=3:raise ValueError('membership')
 s=genesis()
 for e in chain:
  m=message(mesh,s,e['op']);cert=e['cert']
  if e['message']!=m or set(cert)!=set(keys):raise ValueError('chain')
  try:
   for n,k in keys.items():k.verify(bytes.fromhex(cert[n]),enc(m))
  except (InvalidSignature,TypeError,ValueError):raise ValueError('signature')
  s=step(s,e['op'])
 return s
class Anchor:
 def __init__(self,path):
  self.path=path
  with closing(sqlite3.connect(path)) as c:c.execute('CREATE TABLE IF NOT EXISTS log(g INTEGER PRIMARY KEY, body TEXT)');c.commit()
 def read(self):
  with closing(sqlite3.connect(self.path)) as c:return [json.loads(x[0]) for x in c.execute('SELECT body FROM log ORDER BY g')]
 def append(self,mesh,keys,e):
  with closing(sqlite3.connect(self.path)) as c:
   c.execute('BEGIN IMMEDIATE');chain=[json.loads(x[0]) for x in c.execute('SELECT body FROM log ORDER BY g')];replay(mesh,keys,chain+[e]);c.execute('INSERT INTO log VALUES(?,?)',(len(chain)+1,enc(e).decode()));c.commit()
def inspect(mesh,keys,chains):
 if len(chains)!=3 or any(c is None for c in chains):return 'HOLD_MISSING',None
 try:states=[replay(mesh,keys,c) for c in chains]
 except (ValueError,KeyError,TypeError,AssertionError):return 'HOLD_INVALID',None
 longest=max(chains,key=len)
 if any(c!=longest[:len(c)] for c in chains):return 'HOLD_FORK',None
 if any(c!=longest for c in chains):return 'HOLD_LAG',None
 return 'CURRENT',states[0]
