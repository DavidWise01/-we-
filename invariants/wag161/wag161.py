import sqlite3,json,hashlib
from contextlib import closing
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

def enc(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(x): return hashlib.sha256(enc(x)).hexdigest()
class Gate:
 def __init__(self,db,keys,mesh):
    self.db,self.keys,self.mesh=db,tuple(keys),mesh
    ids=[k.public_bytes_raw().hex() for k in keys]
    if len(ids)!=10 or len(set(ids))!=10 or not mesh: raise ValueError('identity')
    genesis=dict(mesh=mesh,keys=ids,version=0,x=[3,2,1]+[2]*7,b=[54]*10,spent=0)
    with closing(self.open()) as c:
     c.execute('BEGIN IMMEDIATE');c.execute('CREATE TABLE IF NOT EXISTS head(body TEXT, genesis TEXT)');c.execute('CREATE TABLE IF NOT EXISTS branches(id TEXT PRIMARY KEY, body TEXT, status TEXT)');c.execute('CREATE TABLE IF NOT EXISTS log(seq INTEGER PRIMARY KEY, body TEXT)')
     if not c.execute('SELECT 1 FROM head').fetchone():c.execute('INSERT INTO head VALUES(?,?)',(enc(genesis).decode(),digest(genesis)))
     if c.execute('SELECT genesis FROM head').fetchone()[0]!=digest(genesis):raise ValueError('genesis')
     c.commit()
 def open(self):
    c=sqlite3.connect(self.db);c.execute('PRAGMA synchronous=FULL');return c
 def head(self):
    with closing(self.open()) as c:return json.loads(c.execute('SELECT body FROM head').fetchone()[0])
 def admit(self,nonce,path):
    if not isinstance(nonce,str) or not nonce or not 2<=len(path)<=10 or any(type(i)!=int or not 0<=i<10 for i in path) or len(set(path))!=len(path) or any((j-i)%10 not in (1,9) for i,j in zip(path,path[1:])):raise ValueError('proposal')
    with closing(self.open()) as c:
     c.execute('BEGIN IMMEDIATE');s=json.loads(c.execute('SELECT body FROM head').fetchone()[0]);p=['WAG161',self.mesh,digest(s),nonce,list(path),1];i=digest(p)
     c.execute('INSERT INTO branches VALUES(?,?,?)',(i,enc(p).decode(),'OPEN'));c.execute('INSERT INTO log(body) VALUES(?)',(enc(['ADMIT',i,p]).decode(),));c.commit();return p
 def close(self,p,sigs,withdraw=None):
    with closing(self.open()) as c:
     c.execute('BEGIN IMMEDIATE');i=digest(p);row=c.execute('SELECT body,status FROM branches WHERE id=?',(i,)).fetchone()
     if row!=(enc(p).decode(),'OPEN'):raise ValueError('not open')
     s=json.loads(c.execute('SELECT body FROM head').fetchone()[0]);path=p[4];a=p[5]
     if withdraw is not None:
      if withdraw not in path or set(sigs)!={withdraw}:raise ValueError('scope')
      self.keys[withdraw].verify(sigs[withdraw],enc(['NO',withdraw,p]));kind='WITHDRAW';t=s
     else:
      if p[2]!=digest(s) or set(sigs)!=set(path):raise ValueError('stale or missing')
      for k in path:self.keys[k].verify(sigs[k],enc(['YES',k,p]))
      x,b=s['x'][:],s['b'][:]
      if x[path[0]]-a<2 or x[path[-1]]+a>2 or any(x[k]!=2 for k in path[1:-1]) or any(b[k]<a for k in path[:-1]):raise ValueError('capacity')
      x[path[0]]-=a;x[path[-1]]+=a
      for k in path[:-1]:b[k]-=a
      t={**s,'x':x,'b':b,'spent':s['spent']+a*(len(path)-1),'version':s['version']+1};kind='COMMIT'
     assert sum(t['x'])==20 and sum(t['b'])+t['spent']==540
     c.execute('UPDATE branches SET status=? WHERE id=?',(kind,i));c.execute('UPDATE head SET body=?',(enc(t).decode(),));c.execute('INSERT INTO log(body) VALUES(?)',(enc([kind,i,digest(s),digest(t),{str(k):v.hex() for k,v in sigs.items()}]).decode(),));c.commit();return t
