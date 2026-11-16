"""WAG-092: fixed signed-beacon sample identity and same-sample recovery.

Runnable compact GitHub reference. The complete 42-case tested source is in
this conversation's WAG-092 local artifacts.
"""
import hashlib,json,sqlite3
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

def pack(obj):return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
def h(data):return hashlib.sha256(data).hexdigest()
def beacon_payload(cp,round_id,out):
    return pack({'domain':'WAG-092-BEACON','checkpoint':cp,'round':round_id,'output':out.hex()})
def sample(cp,round_id,out,n,k):
    if not isinstance(out,bytes) or len(out)<16 or n<1 or k<1 or k>n:raise ValueError('invalid sample')
    seed=hashlib.sha256(b'WAG-092-SAMPLE'+beacon_payload(cp,round_id,out)).digest()
    selected=[];counter=0
    while len(selected)<k:
        block=hashlib.sha256(seed+counter.to_bytes(8,'big')).digest();counter+=1
        for o in range(0,32,8):
            v=int.from_bytes(block[o:o+8],'big')
            if v>=((1<<64)//n)*n:continue
            i=v%n
            if i not in selected:selected.append(i)
            if len(selected)==k:break
    return tuple(selected)
@dataclass(frozen=True)
class Beacon:
    checkpoint:str
    round_id:int
    output:bytes
    sig:bytes
@dataclass(frozen=True)
class Receipt:
    host:str
    checkpoint:str
    round_id:int
    indices:tuple
    root:str
    identifier:str
    sig:bytes

def sign_beacon(sk,cp,rd,out):return Beacon(cp,rd,out,sk.sign(beacon_payload(cp,rd,out)))
def receipt_payload(r):
    return pack({'domain':'WAG-092-HOST','host':r.host,'checkpoint':r.checkpoint,'round':r.round_id,'indices':list(r.indices),'root':r.root,'receipt':r.identifier})
def sign_receipt(sk,host,cp,rd,indices,root,identifier):
    r=Receipt(host,cp,rd,tuple(indices),root,identifier,b'')
    return Receipt(host,cp,rd,tuple(indices),root,identifier,sk.sign(receipt_payload(r)))
class Gate:
    def __init__(self,path,beacon_key,hosts):
        if len(hosts)!=3 or len({k.public_bytes_raw() for k in hosts.values()})!=3:raise ValueError('distinct host keys required')
        self.path=str(path);self.beacon_key=beacon_key;self.hosts=hosts
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS rounds(cp TEXT,rd INTEGER,indices TEXT,beacon TEXT,root TEXT,status TEXT,PRIMARY KEY(cp,rd))')
            db.execute('CREATE TABLE IF NOT EXISTS receipts(id TEXT PRIMARY KEY)')
            db.execute('CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY AUTOINCREMENT,kind TEXT,cp TEXT,rd INTEGER,prev TEXT,hash TEXT)')
    def connect(self):
        db=sqlite3.connect(self.path,isolation_level=None,timeout=10)
        db.execute('PRAGMA synchronous=FULL')
        return _Connection(db)
    def log(self,db,kind,cp,rd):
        last=db.execute('SELECT hash FROM audit ORDER BY seq DESC LIMIT 1').fetchone()
        prev=last[0] if last else '0'*64
        digest=h(pack([kind,cp,rd,prev]))
        db.execute('INSERT INTO audit(kind,cp,rd,prev,hash) VALUES(?,?,?,?,?)',(kind,cp,rd,prev,digest))
    def verify_audit(self):
        with self.connect() as db:rows=db.execute('SELECT kind,cp,rd,prev,hash FROM audit ORDER BY seq').fetchall()
        prev='0'*64
        for kind,cp,rd,p,digest in rows:
            if prev!=p or digest!=h(pack([kind,cp,rd,p])):return False
            prev=digest
        return True
    def freeze(self,beacon,n,k,root):
        self.beacon_key.verify(beacon.sig,beacon_payload(beacon.checkpoint,beacon.round_id,beacon.output))
        ix=sample(beacon.checkpoint,beacon.round_id,beacon.output,n,k)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            try:
                db.execute('INSERT INTO rounds VALUES(?,?,?,?,?,?)',(beacon.checkpoint,beacon.round_id,json.dumps(ix),h(beacon_payload(beacon.checkpoint,beacon.round_id,beacon.output)),root,'FROZEN'))
                self.log(db,'FREEZE',beacon.checkpoint,beacon.round_id);db.execute('COMMIT')
            except Exception:db.execute('ROLLBACK');raise
        return ix
    def state(self,cp,rd):
        with self.connect() as db:r=db.execute('SELECT indices,status,root FROM rounds WHERE cp=? AND rd=?',(cp,rd)).fetchone()
        return (tuple(json.loads(r[0])),r[1],r[2]) if r else None
    def change(self,cp,rd,from_state,to_state,event):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            try:
                if db.execute('UPDATE rounds SET status=? WHERE cp=? AND rd=? AND status=?',(to_state,cp,rd,from_state)).rowcount!=1:raise ValueError('invalid transition')
                self.log(db,event,cp,rd);db.execute('COMMIT')
            except Exception:db.execute('ROLLBACK');raise
        return self.state(cp,rd)[0]
    def abort(self,cp,rd):return self.change(cp,rd,'FROZEN','HOLD_ABORT','ABORT')
    def recover_same_sample(self,cp,rd):return self.change(cp,rd,'HOLD_ABORT','FROZEN','RECOVER_SAME_SAMPLE')
    def accept(self,cp,rd,responses):
        if len(responses)!=3 or {r.host for r in responses}!=set(self.hosts):raise ValueError('three distinct hosts required')
        if len({r.identifier for r in responses})!=3 or any(not r.identifier for r in responses):raise ValueError('receipt identities')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            try:
                row=db.execute('SELECT indices,status,root FROM rounds WHERE cp=? AND rd=?',(cp,rd)).fetchone()
                if not row or row[1]!='FROZEN':raise ValueError('round not open')
                ix=tuple(json.loads(row[0]))
                for r in responses:
                    if (r.checkpoint,r.round_id,r.indices,r.root)!=(cp,rd,ix,row[2]):raise ValueError('changed sample')
                    self.hosts[r.host].verify(r.sig,receipt_payload(r))
                    if db.execute('SELECT 1 FROM receipts WHERE id=?',(r.identifier,)).fetchone():raise ValueError('receipt replay')
                for r in responses:db.execute('INSERT INTO receipts(id) VALUES(?)',(r.identifier,))
                db.execute('UPDATE rounds SET status=? WHERE cp=? AND rd=?',('LOCAL_ELIGIBLE',cp,rd))
                self.log(db,'ACCEPT',cp,rd);db.execute('COMMIT')
            except Exception:db.execute('ROLLBACK');raise
        return 'LOCAL_ELIGIBLE'
class _Connection:
    def __init__(self,db):self.db=db
    def __enter__(self):return self.db
    def __exit__(self,*args):self.db.close()
def demo(path):
    beacon_sk=Ed25519PrivateKey.generate()
    hosts={w:Ed25519PrivateKey.generate() for w in ('W1','W2','W3')}
    g=Gate(path,beacon_sk.public_key(),{w:k.public_key() for w,k in hosts.items()})
    b=sign_beacon(beacon_sk,'cp91',92,b'demo signed output from beacon')
    indices=g.freeze(b,17,3,'root')
    g.abort('cp91',92)
    assert g.recover_same_sample('cp91',92)==indices
    receipts=[sign_receipt(sk,w,'cp91',92,indices,'root','receipt-'+w) for w,sk in hosts.items()]
    return {'sample':indices,'result':g.accept('cp91',92,receipts),'audit':g.verify_audit()}
if __name__=='__main__':
    import tempfile
    with tempfile.TemporaryDirectory() as d:print(demo(d+'/gate.db'))
