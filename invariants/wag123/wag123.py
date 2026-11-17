"""Durable single-slot view closure. Honest fixed witnesses; no rollback resistance."""
import sqlite3,json
from contextlib import closing
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat

def enc(v): return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def msg(scope,view,name,kind,value): return ['WAG123',scope,view,name,kind,value]
def decision(scope,view,proof,keys):
    if len(keys)!=3 or set(proof)!=set(keys) or len({k.public_bytes(Encoding.Raw,PublicFormat.Raw) for k in keys.values()})!=3:return 'HOLD'
    try:
        for name,key in keys.items():
            value,sig=proof[name];key.verify(bytes.fromhex(sig),enc(msg(scope,view,name,'close',value)))
        vals=[p[0] for p in proof.values()]
        return 'RECOVER' if vals[0] is not None and all(v==vals[0] for v in vals) else 'ADVANCE'
    except (ValueError,TypeError,InvalidSignature,KeyError):return 'HOLD'
class Witness:
    def __init__(self,path,name,key,scope,keys):
        self.path=path;self.name=name;self.key=key;self.scope=scope;self.keys=keys
        if key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)!=keys[name].public_bytes(Encoding.Raw,PublicFormat.Raw):raise ValueError('identity')
        with closing(self.open()) as c:
            c.execute('CREATE TABLE IF NOT EXISTS views(view INTEGER PRIMARY KEY, val TEXT, closed INTEGER NOT NULL, closure TEXT)')
            c.execute('CREATE TABLE IF NOT EXISTS identity(id TEXT PRIMARY KEY)')
            ident=enc([scope,name,key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw).hex()]).decode()
            old=c.execute('SELECT id FROM identity').fetchone()
            if old and old[0]!=ident:raise ValueError('scope')
            if not old:c.execute('INSERT INTO identity VALUES(?)',(ident,));c.execute('INSERT INTO views VALUES(0,NULL,0,NULL)')
            c.commit()
    def open(self):
        c=sqlite3.connect(self.path);c.execute('PRAGMA synchronous=FULL');return c
    def current(self,c):return c.execute('SELECT view,val,closed,closure FROM views ORDER BY view DESC LIMIT 1').fetchone()
    def vote(self,value):
        if not isinstance(value,str) or not value:raise ValueError('value')
        with closing(self.open()) as c:
            c.execute('BEGIN IMMEDIATE');v,old,closed,_=self.current(c)
            if closed or (old is not None and old!=value):raise ValueError('locked')
            c.execute('UPDATE views SET val=? WHERE view=?',(value,v));sig=self.key.sign(enc(msg(self.scope,v,self.name,'vote',value))).hex();c.commit();return sig
    def close(self):
        with closing(self.open()) as c:
            c.execute('BEGIN IMMEDIATE');v,val,closed,sig=self.current(c)
            if not closed:
                sig=self.key.sign(enc(msg(self.scope,v,self.name,'close',val))).hex();c.execute('UPDATE views SET closed=1,closure=? WHERE view=?',(sig,v))
            c.commit();return [val,sig]
    def advance(self,proof):
        with closing(self.open()) as c:
            c.execute('BEGIN IMMEDIATE');v,val,closed,sig=self.current(c)
            if not closed or proof.get(self.name)!=[val,sig] or decision(self.scope,v,proof,self.keys)!='ADVANCE':raise ValueError('unsafe')
            c.execute('INSERT INTO views VALUES(?,NULL,0,NULL)',(v+1,));c.commit();return v+1
