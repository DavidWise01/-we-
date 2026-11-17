"""WAG-103: persistent hold and independently signed policy anchor model."""
import json, sqlite3, hashlib
from contextlib import closing
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(x): return hashlib.sha256(canon(x)).hexdigest()
def closure(g,n,path=()):
    if n in path or n not in g or not isinstance(g[n],list): raise ValueError('unknown/cycle')
    return {n}.union(*(closure(g,p,path+(n,)) for p in g[n]))
def independent(g,actors):
    for n in g: closure(g,n)
    roots=[closure(g,n) for n in actors]
    return all(not a&b for i,a in enumerate(roots) for b in roots[i+1:])
class Gate:
    def __init__(self,path,graph,actors,keys,anchor_key,scope):
        self.path=str(path); self.actors=tuple(actors); self.keys=dict(keys); self.anchor_key=anchor_key; self.scope=scope
        if len(self.actors)!=3 or len(set(self.actors))!=3 or len(keys)!=3 or len(set(keys.values())|{anchor_key})!=4 or not independent(graph,actors): raise ValueError('policy')
        self.policy=digest([scope,self.actors,{k:v.hex() for k,v in keys.items()},anchor_key.hex()])
        with closing(sqlite3.connect(self.path)) as c,c:
            c.execute('CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY, body TEXT)')
            c.execute('CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY,body TEXT,hash TEXT)')
            s={'policy':self.policy,'epoch':0,'graph':graph,'holds':[]}
            c.execute('INSERT OR IGNORE INTO state VALUES(1,?)',(canon(s).decode(),))
            if self._state(c)['policy']!=self.policy: raise ValueError('policy changed')
    def _state(self,c): return json.loads(c.execute('SELECT body FROM state').fetchone()[0])
    def state(self):
        with closing(sqlite3.connect(self.path)) as c:return self._state(c)
    def _record(self,c,s,event,detail):
        row=c.execute('SELECT seq,hash FROM audit ORDER BY seq DESC LIMIT 1').fetchone()
        b={'seq':row[0]+1 if row else 0,'prev':row[1] if row else '0'*64,'event':event,'detail':detail,'state':s}
        c.execute('INSERT INTO audit VALUES(?,?,?)',(b['seq'],canon(b).decode(),digest(b)))
        c.execute('UPDATE state SET body=? WHERE id=1',(canon(s).decode(),))
    def observe(self,g):
        with closing(sqlite3.connect(self.path)) as c,c:
            c.execute('BEGIN IMMEDIATE');s=self._state(c)
            if digest(g)==digest(s['graph']):return 'HOLD_MUTATION' if s['holds'] else 'UNCHANGED'
            h=digest(g)
            if h not in s['holds']:
                s['holds'].append(h);s['holds'].sort();self._record(c,s,'mutation',g)
            return 'HOLD_MUTATION'
    def proposal(self,g):
        s=self.state();return {'type':'WAG103/revalidate','scope':self.scope,'prior':digest(s),'next_epoch':s['epoch']+1,'graph':digest(g)}
    def revalidate(self,g,p,sigs):
        with closing(sqlite3.connect(self.path)) as c,c:
            c.execute('BEGIN IMMEDIATE');s=self._state(c)
            expected={'type':'WAG103/revalidate','scope':self.scope,'prior':digest(s),'next_epoch':s['epoch']+1,'graph':digest(g)}
            if not s['holds'] or p!=expected:return 'HOLD_STALE'
            try:
                if not independent(g,self.actors):return 'HOLD_SHARED_CONTROL'
            except (ValueError,RecursionError,TypeError):return 'HOLD_ANCESTRY'
            if set(sigs)!=set(self.keys):return 'HOLD_QUORUM'
            try:
                for n,k in self.keys.items():Ed25519PublicKey.from_public_bytes(k).verify(sigs[n],canon(p))
            except Exception:return 'HOLD_SIGNATURE'
            old=s;s={**s,'epoch':s['epoch']+1,'graph':g,'holds':[]}
            self._record(c,s,'revalidate',{'old':old,'proposal':p,'signatures':{n:v.hex() for n,v in sigs.items()}})
            return 'HOLD_PENDING_ANCHOR'
    def anchor_statement(self):
        s=self.state();return {'type':'WAG103/anchor','scope':self.scope,'epoch':s['epoch'],'state':digest(s)}
    def decision(self,anchor,signature):
        s=self.state()
        if s['holds']:return 'HOLD_MUTATION'
        try:Ed25519PublicKey.from_public_bytes(self.anchor_key).verify(signature,canon(anchor))
        except Exception:return 'HOLD_ANCHOR_SIGNATURE'
        if anchor!={'type':'WAG103/anchor','scope':self.scope,'epoch':s['epoch'],'state':digest(s)}:return 'HOLD_ANCHOR_MISMATCH'
        return 'LOCAL_ELIGIBLE'
    def verify_audit(self):
        with closing(sqlite3.connect(self.path)) as c:
            prev='0'*64;last=None
            for i,(seq,body,h) in enumerate(c.execute('SELECT seq,body,hash FROM audit ORDER BY seq')):
                b=json.loads(body)
                if seq!=i or b['seq']!=i or b['prev']!=prev or digest(b)!=h:return False
                prev=h;last=b['state']
            return last is None or last==self._state(c)
