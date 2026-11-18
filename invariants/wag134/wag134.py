import json, hashlib, sqlite3
from contextlib import closing
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

def enc(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(x): return hashlib.sha256(enc(x)).hexdigest()
def raw(k): return k.public_bytes(Encoding.Raw,PublicFormat.Raw).hex()
def validate(m):
    if set(m)!={'mesh','generation','keys','roots'} or type(m['generation']) is not int or m['generation']<0: raise ValueError('manifest')
    if len(m['keys'])!=3 or set(m['keys'])!=set(m['roots']) or len(set(m['keys'].values()))!=3: raise ValueError('membership')
    sets=[]
    for n,k in m['keys'].items():
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(k))
        r=m['roots'][n]
        if not isinstance(r,list) or not r or any(not isinstance(x,str) or not x for x in r):raise ValueError('roots')
        sets.append(set(r))
    if any(a&b for i,a in enumerate(sets) for b in sets[:i]):raise ValueError('shared root')
def statement(old,new,role):return ['WAG134',role,old['mesh'],digest(old),digest(new)]
def signatures(m,body,cert):
    if set(cert)!=set(m['keys']):raise ValueError('missing signatures')
    for n,k in m['keys'].items():Ed25519PublicKey.from_public_bytes(bytes.fromhex(k)).verify(bytes.fromhex(cert[n]),enc(body))
class Registry:
    def __init__(self,path,genesis):
        validate(genesis)
        if genesis['generation']!=0:raise ValueError('genesis')
        self.path=path;self.genesis=genesis
        with closing(self.open()) as c:
            c.execute('CREATE TABLE IF NOT EXISTS lineage(g INTEGER PRIMARY KEY, manifest TEXT, proof TEXT)')
            c.execute('INSERT OR IGNORE INTO lineage VALUES(0,?,NULL)',(enc(genesis).decode(),));c.commit()
            if json.loads(c.execute('SELECT manifest FROM lineage WHERE g=0').fetchone()[0])!=genesis:raise ValueError('genesis mismatch')
    def open(self):
        c=sqlite3.connect(self.path);c.execute('PRAGMA synchronous=FULL');return c
    def head(self):
        with closing(self.open()) as c:return self.read(c)[0]
    def read(self,c):
        old=self.genesis;retired=set();rows=c.execute('SELECT g,manifest,proof FROM lineage ORDER BY g').fetchall()
        if not rows or rows[0][0]!=0 or json.loads(rows[0][1])!=old:raise ValueError('genesis')
        for g,body,proof in rows[1:]:
            new=json.loads(body);a,b=json.loads(proof)
            self.verify(old,new,a,b,retired)
            if g!=new['generation']:raise ValueError('index')
            retired.update(set(old['keys'].values())-set(new['keys'].values()));old=new
        return old,retired
    def verify(self,old,new,a,b,retired):
        validate(new)
        if new['mesh']!=old['mesh'] or new['generation']!=old['generation']+1:raise ValueError('scope or generation')
        if retired&set(new['keys'].values()):raise ValueError('retired key')
        signatures(old,statement(old,new,'approve'),a);signatures(new,statement(old,new,'accept'),b)
    def advance(self,new,a,b):
        with closing(self.open()) as c:
            c.execute('BEGIN IMMEDIATE');old,retired=self.read(c);self.verify(old,new,a,b,retired)
            c.execute('INSERT INTO lineage VALUES(?,?,?)',(new['generation'],enc(new).decode(),enc([a,b]).decode()));c.commit()
    def authorize(self,body,cert):
        head=self.head()
        if len(body)!=4 or body[:3]!=['WAG134-observe',head['mesh'],digest(head)]:raise ValueError('stale topology')
        signatures(head,body,cert);return 'CURRENT_MEMBERSHIP_SIGNATURES'
