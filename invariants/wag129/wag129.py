from wag128 import enc,root,genesis,step,Gate as BaseGate
import json
from contextlib import closing

def replay(mesh,keys,gate,events,expected=None):
    s=genesis(); seen=set()
    if len(keys)!=3: raise ValueError('membership')
    for p,cert,r in events:
        if len(p)!=6 or p[:2]!=['WAG128',mesh] or set(cert)!=set(keys) or p[2] in seen or p[3]!=root(s):raise ValueError('proposal ancestry')
        for n,k in keys.items():k.verify(bytes.fromhex(cert[n]),enc(p))
        t=step(s,p[4]);body=['WAG128-commit',mesh,root(p),t['g'],root(t)]
        if p[5]!=root(t) or r[0]!=body:raise ValueError('result')
        gate.verify(bytes.fromhex(r[1]),enc(body));seen.add(p[2]);s=t
    if expected is not None and root(s)!=expected:raise ValueError('head mismatch')
    return s

class Gate(BaseGate):
    def __init__(self,*args):
        super().__init__(*args)
        with closing(self.open()) as c:
            c.execute('CREATE TABLE IF NOT EXISTS evidence(g INTEGER PRIMARY KEY, body TEXT NOT NULL)');c.commit()
    def commit(self,p,cert):
        if len(p)!=6 or p[:2]!=['WAG128',self.mesh] or set(cert)!=set(self.keys):raise ValueError('scope')
        for n,k in self.keys.items():k.verify(bytes.fromhex(cert[n]),enc(p))
        with closing(self.open()) as c:
            c.execute('BEGIN IMMEDIATE');s=json.loads(c.execute('SELECT state FROM head').fetchone()[0]);old=c.execute('SELECT receipt FROM events WHERE nonce=?',(p[2],)).fetchone()
            if old:
                r=json.loads(old[0])
                if r[0][2]!=root(p):raise ValueError('nonce conflict')
                return r
            if root(s)!=p[3]:raise ValueError('stale parent')
            t=step(s,p[4])
            if root(t)!=p[5]:raise ValueError('wrong result')
            body=['WAG128-commit',self.mesh,root(p),t['g'],root(t)];r=[body,self.key.sign(enc(body)).hex()]
            c.execute('INSERT INTO events VALUES(?,?,?)',(t['g'],p[2],enc(r).decode()));c.execute('INSERT INTO evidence VALUES(?,?)',(t['g'],enc([p,cert,r]).decode()));c.execute('UPDATE head SET state=?',(enc(t).decode(),));c.commit();return r
    def export(self):
        with closing(self.open()) as c:
            c.execute('BEGIN');s=json.loads(c.execute('SELECT state FROM head').fetchone()[0]);events=[json.loads(r[0]) for r in c.execute('SELECT body FROM evidence ORDER BY g')];replay(self.mesh,self.keys,self.key.public_key(),events,root(s));return events,root(s)
