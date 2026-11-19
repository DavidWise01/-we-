import json, hashlib, sqlite3
from contextlib import closing
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def enc(v): return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def digest(v): return hashlib.sha256(enc(v)).hexdigest()
class Gate:
    def __init__(self,path,keys):
        self.path=path; self.keys=tuple(keys)
        ids=[k.public_bytes_raw().hex() for k in keys]
        if len(ids)!=10 or len(set(ids))!=10: raise ValueError('keys')
        g=dict(mesh='WAG160',keys=ids,seq=0,x=[3,2,1]+[2]*7,b=[54]*10,spent=0,closed=[])
        with closing(self.open()) as c:
            c.execute('BEGIN IMMEDIATE');c.execute('CREATE TABLE IF NOT EXISTS head(body TEXT, genesis TEXT)');c.execute('CREATE TABLE IF NOT EXISTS log(seq INTEGER PRIMARY KEY, body TEXT)')
            if not c.execute('SELECT 1 FROM head').fetchone(): c.execute('INSERT INTO head VALUES(?,?)',(enc(g).decode(),digest(g)))
            if c.execute('SELECT genesis FROM head').fetchone()[0]!=digest(g): raise ValueError('genesis')
            c.commit()
    def open(self):
        c=sqlite3.connect(self.path);c.execute('PRAGMA synchronous=FULL');return c
    def head(self):
        with closing(self.open()) as c:return json.loads(c.execute('SELECT body FROM head').fetchone()[0])
    def propose(self,path=(0,1,2),amount=1):
        return ['WAG160',digest(self.head()),list(path),amount]
    def execute(self,p,signatures,withdraw=None):
        with closing(self.open()) as c:
            c.execute('BEGIN IMMEDIATE');s=json.loads(c.execute('SELECT body FROM head').fetchone()[0])
            if len(p)!=4 or p[:2]!=['WAG160',digest(s)]: raise ValueError('stale parent')
            path,a=p[2:];x,b=s['x'][:],s['b'][:]
            if type(a)!=int or a<=0 or not 2<=len(path)<=10 or len(set(path))!=len(path) or any(type(i)!=int or not 0<=i<10 for i in path) or any((j-i)%10 not in (1,9) for i,j in zip(path,path[1:])):raise ValueError('route')
            if withdraw is not None:
                if withdraw not in path or set(signatures)!={withdraw}:raise ValueError('withdraw scope')
                self.keys[withdraw].verify(signatures[withdraw],enc(['NO',withdraw,p]));kind='WITHDRAW';cost=0
            else:
                if set(signatures)!=set(path):raise ValueError('missing consent')
                for i in path:self.keys[i].verify(signatures[i],enc(['YES',i,p]))
                if x[path[0]]-a<2 or x[path[-1]]+a>2 or any(x[i]!=2 for i in path[1:-1]) or any(b[i]<a for i in path[:-1]):raise ValueError('capacity')
                x[path[0]]-=a;x[path[-1]]+=a
                for i in path[:-1]:b[i]-=a
                kind='COMMIT';cost=a*(len(path)-1)
            t={**s,'seq':s['seq']+1,'x':x,'b':b,'spent':s['spent']+cost,'closed':s['closed']+[digest(p)]}
            assert sum(x)==20 and sum(b)+t['spent']==540 and min(x+b)>=0
            r=dict(kind=kind,proposal=p,signatures={str(i):v.hex() for i,v in signatures.items()},result=digest(t))
            c.execute('INSERT INTO log VALUES(?,?)',(t['seq'],enc(r).decode()));c.execute('UPDATE head SET body=?',(enc(t).decode(),));c.commit();return t
