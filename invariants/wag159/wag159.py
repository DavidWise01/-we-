import json, hashlib, sqlite3
from contextlib import closing
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def enc(v): return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def digest(v): return hashlib.sha256(enc(v)).hexdigest()
def proposal(s,path,amount): return ['WAG159',s['mesh'],digest(s),list(path),amount]
def apply(s,p,consent,keys):
    if len(p)!=5 or p[:3]!=['WAG159',s['mesh'],digest(s)]: raise ValueError('stale scope')
    path,a=p[3:]
    if type(a)!=int or a<=0 or not 2<=len(path)<=10 or any(type(i)!=int or not 0<=i<10 for i in path) or len(set(path))!=len(path): raise ValueError('path')
    if any((j-i)%10 not in (1,9) for i,j in zip(path,path[1:])): raise ValueError('adjacency')
    if set(consent)!=set(path): raise ValueError('consent missing')
    x,b=s['x'][:],s['b'][:]
    if x[path[0]]-a<2 or x[path[-1]]+a>2 or any(x[i]!=2 for i in path[1:-1]) or any(b[i]<a for i in path[:-1]): raise ValueError('capacity')
    for i in path: keys[i].verify(consent[i],enc(['YES',i,p]))
    x[path[0]]-=a;x[path[-1]]+=a
    for i in path[:-1]: b[i]-=a
    t={**s,'x':x,'b':b,'spent':s['spent']+a*(len(path)-1),'seq':s['seq']+1}
    assert sum(t['x'])==sum(s['x'])==20 and sum(t['b'])+t['spent']==sum(s['b'])+s['spent'] and min(x+b)>=0
    return t

class Gate:
    def __init__(self,path,mesh,keys):
        self.path=path;self.keys=keys
        if len(keys)!=10 or len({k.public_bytes_raw() for k in keys})!=10: raise ValueError('keys')
        g={'mesh':mesh,'seq':0,'x':[3,2,1]+[2]*7,'b':[54]*10,'spent':0,'keys':[k.public_bytes_raw().hex() for k in keys]}
        with closing(self.open()) as c:
            c.execute('CREATE TABLE IF NOT EXISTS head(id INTEGER PRIMARY KEY, body TEXT, genesis TEXT)')
            c.execute('CREATE TABLE IF NOT EXISTS receipts(seq INTEGER PRIMARY KEY, body TEXT)')
            c.execute('INSERT OR IGNORE INTO head VALUES(1,?,?)',(enc(g).decode(),digest(g)))
            if c.execute('SELECT genesis FROM head').fetchone()[0]!=digest(g):raise ValueError('genesis mismatch')
            c.commit()
    def open(self):
        c=sqlite3.connect(self.path);c.execute('PRAGMA synchronous=FULL');return c
    def head(self):
        with closing(self.open()) as c:return json.loads(c.execute('SELECT body FROM head').fetchone()[0])
    def commit(self,p,consent):
        with closing(self.open()) as c:
            c.execute('BEGIN IMMEDIATE');s=json.loads(c.execute('SELECT body FROM head').fetchone()[0]);t=apply(s,p,consent,self.keys)
            r={'proposal':p,'consent':{str(i):v.hex() for i,v in consent.items()},'result':digest(t)}
            c.execute('INSERT INTO receipts VALUES(?,?)',(t['seq'],enc(r).decode()));c.execute('UPDATE head SET body=?',(enc(t).decode(),));c.commit();return t
