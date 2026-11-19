import hashlib,json,sqlite3
from contextlib import closing
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

def enc(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def H(b):return hashlib.sha256(b).digest()
def leaf(v):return H(b'\x00'+enc(v))
def pair(a,b):return H(b'\x01'+a+b)
def split(n):return 1<<((n-1).bit_length()-1)
def root(xs):
    if not xs:return H(b'')
    if len(xs)==1:return xs[0]
    k=split(len(xs));return pair(root(xs[:k]),root(xs[k:]))
def proof(xs,m):
    def sub(xs,m,b):
        if m==len(xs):return [] if b else [root(xs)]
        k=split(len(xs))
        if m<=k:return sub(xs[:k],m,b)+[root(xs[k:])]
        return sub(xs[k:],m-k,False)+[root(xs[:k])]
    if not 0<m<=len(xs):raise ValueError('size')
    return sub(xs,m,True)
def verify(m,n,old,new,p):
    if type(m)!=int or type(n)!=int or not 0<m<n or any(type(v)!=bytes or len(v)!=32 for v in [old,new,*p]):return False
    it=iter(p)
    def fold(m,n,b):
        if m==n:
            v=old if b else next(it);return v,v
        k=split(n)
        if m<=k:
            a,c=fold(m,k,b);return a,pair(c,next(it))
        a,c=fold(m-k,n-k,False);l=next(it);return pair(l,a),pair(l,c)
    try:
        a,c=fold(m,n,True);return a==old and c==new and next(it,None) is None
    except StopIteration:return False

def records(n):
    rs=[]
    for i in range(n):
        x=[3,2,1,3,2,1,2,2,2,2];b=[54]*10
        for k in range(min(i,2)):
            j=k*3;x[j]-=1;x[j+2]+=1;b[j]-=1;b[j+1]-=1
        rs.append(dict(generation=i,parent=leaf(rs[-1]).hex() if rs else None,x=x,b=b,center=6,spent=2*min(i,2)))
    return rs

def statement(mesh,m,n,old,new):return ['WAG167',mesh,m,n,old.hex(),new.hex()]
class Witness:
    def __init__(self,db,mesh,name,key,m,r):
        self.db,self.mesh,self.name,self.key=db,mesh,name,key
        with closing(sqlite3.connect(db)) as c:
            c.execute('CREATE TABLE IF NOT EXISTS pin(id INTEGER PRIMARY KEY,scope TEXT,n INTEGER,r BLOB)')
            scope=enc([mesh,name,key.public_key().public_bytes_raw().hex(),m,r.hex()]).decode()
            c.execute('INSERT OR IGNORE INTO pin VALUES(1,?,?,?)',(scope,m,r))
            if c.execute('SELECT scope FROM pin').fetchone()[0]!=scope:raise ValueError('scope')
            c.commit()
    def sign(self,s,p):
        domain,mesh,m,n,a,b=s;old,new=bytes.fromhex(a),bytes.fromhex(b)
        if domain!='WAG167' or mesh!=self.mesh or not verify(m,n,old,new,p):raise ValueError('proof')
        with closing(sqlite3.connect(self.db)) as c:
            c.execute('BEGIN IMMEDIATE')
            if c.execute('SELECT n,r FROM pin').fetchone()!=(m,old):raise ValueError('stale pin')
            sig=self.key.sign(enc([self.name,s]))
            c.execute('UPDATE pin SET n=?,r=? WHERE id=1',(n,new));c.commit();return sig

def certify(s,registry,sigs):
    if len(registry)!=3 or set(sigs)!=set(registry):raise ValueError('quorum')
    if len({r for r,k in registry.values()})!=3 or len({k.public_bytes_raw() for r,k in registry.values()})!=3:raise ValueError('ancestry')
    for name,(_,k) in registry.items():k.verify(sigs[name],enc([name,s]))
    return True
