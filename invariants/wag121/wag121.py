"""Single-host three-witness prepare/commit reference; no Byzantine liveness."""
import sqlite3,json,hashlib
from contextlib import closing
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat

def enc(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(x): return hashlib.sha256(enc(x)).hexdigest()
GEN={'seq':0,'balances':[156,0,0],'pending':{},'delivered':[]}
def apply(s,e):
    s=json.loads(enc(s)); p=e['packet']; a,b,q,k=p['src'],p['dst'],p['q'],p['id']
    if e['seq']!=s['seq']+1 or e['prev']!=digest(s): raise ValueError('continuity')
    if type(a)!=int or not 0<=a<3 or b!=(a+1)%3 or type(q)!=int or q<=0 or not isinstance(k,str): raise ValueError('packet')
    if e['kind']=='send':
        if q>s['balances'][a] or k in s['pending'] or k in s['delivered']: raise ValueError('send')
        s['balances'][a]-=q;s['pending'][k]=p
    elif e['kind']=='receive':
        if s['pending'].get(k)!=p: raise ValueError('receive')
        s['balances'][b]+=q;del s['pending'][k];s['delivered'].append(k)
    else: raise ValueError('kind')
    s['seq']=e['seq'];return s

def body(name,e):return {'tag':'WAG121-prepare-v1','witness':name,'event':e}
def verify(keys,e,cert):
    if set(cert)!=set(keys) or len(keys)!=3: return False
    try:
        for n,k in keys.items():k.verify(bytes.fromhex(cert[n]),enc(body(n,e)))
        return True
    except (InvalidSignature,ValueError,TypeError):return False
class Witness:
    def __init__(self,path,name,key,keys):
        if len(keys)!=3 or len({k.public_bytes(Encoding.Raw,PublicFormat.Raw) for k in keys.values()})!=3:raise ValueError('keys')
        if key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)!=keys[name].public_bytes(Encoding.Raw,PublicFormat.Raw):raise ValueError('identity')
        self.path=path;self.name=name;self.key=key;self.keys=keys
        with closing(self.open()) as c:
            c.execute('CREATE TABLE IF NOT EXISTS locks(seq INTEGER PRIMARY KEY,event TEXT,sig TEXT)');c.execute('CREATE TABLE IF NOT EXISTS commits(seq INTEGER PRIMARY KEY,event TEXT,cert TEXT)');c.commit()
    def open(self):
        c=sqlite3.connect(self.path);c.execute('PRAGMA synchronous=FULL');return c
    def state(self,c):
        s=GEN
        for raw,cert in c.execute('SELECT event,cert FROM commits ORDER BY seq'):
            e=json.loads(raw)
            if not verify(self.keys,e,json.loads(cert)):raise ValueError('bad commit')
            s=apply(s,e)
        return s
    def prepare(self,e):
        with closing(self.open()) as c:
            c.execute('BEGIN IMMEDIATE');apply(self.state(c),e)
            row=c.execute('SELECT event,sig FROM locks WHERE seq=?',(e['seq'],)).fetchone()
            if row:
                if json.loads(row[0])!=e:raise ValueError('locked conflict')
                return row[1]
            sig=self.key.sign(enc(body(self.name,e))).hex()
            c.execute('INSERT INTO locks VALUES(?,?,?)',(e['seq'],enc(e).decode(),sig));c.commit();return sig
    def commit(self,e,cert):
        if not verify(self.keys,e,cert):raise ValueError('certificate')
        with closing(self.open()) as c:
            c.execute('BEGIN IMMEDIATE');s=self.state(c)
            old=c.execute('SELECT event FROM commits WHERE seq=?',(e['seq'],)).fetchone()
            if old:
                if json.loads(old[0])!=e:raise ValueError('fork')
                return
            apply(s,e)
            lock=c.execute('SELECT event FROM locks WHERE seq=?',(e['seq'],)).fetchone()
            if not lock or json.loads(lock[0])!=e:raise ValueError('missing lock')
            c.execute('INSERT INTO commits VALUES(?,?,?)',(e['seq'],enc(e).decode(),enc(cert).decode()));c.commit()
    def read(self):
        with closing(self.open()) as c:return self.state(c)
    def evidence(self,seq):
        with closing(self.open()) as c:
            r=c.execute('SELECT event,sig FROM locks WHERE seq=?',(seq,)).fetchone()
            return (json.loads(r[0]),r[1]) if r else None
    def certificate(self,seq):
        with closing(self.open()) as c:
            r=c.execute('SELECT event,cert FROM commits WHERE seq=?',(seq,)).fetchone()
            return (json.loads(r[0]),json.loads(r[1])) if r else None

def recover(ws,seq):
    saved=[w.certificate(seq) for w in ws]; saved=[x for x in saved if x]
    if saved:
        e,cert=saved[0]
        if any(x[0]!=e for x in saved):raise ValueError('fork')
    else:
        votes=[w.evidence(seq) for w in ws]
        if any(x is None for x in votes):return 'HOLD_INCOMPLETE'
        e=votes[0][0]
        if any(x[0]!=e for x in votes):return 'HOLD_CONFLICT'
        cert={w.name:v[1] for w,v in zip(ws,votes)}
    if not verify(ws[0].keys,e,cert):raise ValueError('certificate')
    for w in ws:w.commit(e,cert)
    return 'COMMITTED'

def total(s):return sum(s['balances'])+sum(p['q'] for p in s['pending'].values())
