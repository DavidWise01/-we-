"""WAG-082 GitHub reference: signed anchor chain and fail-closed local recovery.
For 30 tested cases see the full conversation artifact; this is a compact reference.
Same-host JSONL is NOT an independent external anchor.
"""
import json,hashlib,os,sqlite3
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(x):return hashlib.sha256(canonical(x)).hexdigest()
class Hold(Exception):pass
@dataclass(frozen=True)
class Observer:
    name:str
    ancestor:str
    domain:str
    public:bytes
def signed_payload(epoch,size,root,previous):
    return b'WAG-082.anchor.v1\x00'+canonical(dict(epoch=epoch,size=size,root=root,previous=previous))
class RecoveryGate:
    def __init__(self,db_path,anchor_path,observers):
        self.db_path=str(db_path);self.anchor_path=Path(anchor_path)
        self.observers={o.name:o for o in observers}
        if len(self.observers)!=3 or len(tuple(observers))!=3:raise Hold('INVALID_QUORUM')
        for attr in ('ancestor','domain','public'):
            vals=[getattr(o,attr) for o in self.observers.values()]
            if len(set(vals))!=3 or any(not x for x in vals):raise Hold('SHARED_DECLARED_PROVENANCE')
        with self.db() as c:
            c.execute('CREATE TABLE IF NOT EXISTS checkpoint (id INTEGER PRIMARY KEY CHECK(id=1),epoch INTEGER,size INTEGER,root TEXT)')
    @contextmanager
    def db(self):
        c=sqlite3.connect(self.db_path,isolation_level=None)
        try:
            c.execute('PRAGMA journal_mode=WAL');c.execute('PRAGMA synchronous=FULL')
            yield c
            if c.in_transaction:c.commit()
        except BaseException:
            if c.in_transaction:c.rollback()
            raise
        finally:c.close()
    def local(self):
        with self.db() as c:
            r=c.execute('SELECT epoch,size,root FROM checkpoint WHERE id=1').fetchone()
        return dict(epoch=r[0],size=r[1],root=r[2]) if r else None
    def set_local(self,epoch,size,root):
        if not isinstance(epoch,int) or epoch<0 or not isinstance(size,int) or size<=0 or not isinstance(root,str) or len(root)!=64:raise Hold('BAD_CHECKPOINT')
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE')
            old=c.execute('SELECT epoch FROM checkpoint WHERE id=1').fetchone()
            if old and epoch<=old[0]:raise Hold('NONMONOTONIC_LOCAL')
            c.execute('INSERT INTO checkpoint VALUES(1,?,?,?) ON CONFLICT(id) DO UPDATE SET epoch=excluded.epoch,size=excluded.size,root=excluded.root',(epoch,size,root))
            c.execute('COMMIT')
    def _read(self):
        if not self.anchor_path.exists():return []
        try:return [json.loads(line) for line in self.anchor_path.read_text().splitlines() if line.strip()]
        except (ValueError,UnicodeError) as exc:raise Hold('DAMAGED_ANCHOR_LOG') from exc
    def verify_entry(self,e,previous):
        try:
            if e['previous']!=previous or not isinstance(e['epoch'],int) or e['epoch']<0 or not isinstance(e['size'],int) or e['size']<1 or not isinstance(e['root'],str) or len(e['root'])!=64:raise Hold('INVALID_ANCHOR_CHAIN')
            if set(e['signatures'])!=set(self.observers):raise Hold('INVALID_ANCHOR_QUORUM')
            payload=signed_payload(e['epoch'],e['size'],e['root'],e['previous'])
            for name,sig in e['signatures'].items():Ed25519PublicKey.from_public_bytes(self.observers[name].public).verify(bytes.fromhex(sig),payload)
            if e.get('hash')!=digest({k:v for k,v in e.items() if k!='hash'}):raise Hold('INVALID_ANCHOR_HASH')
        except Hold:raise
        except (KeyError,TypeError,ValueError,InvalidSignature) as exc:raise Hold('BAD_ANCHOR_SIGNATURE_OR_FORMAT') from exc
    def chain(self):
        entries=self._read();previous='0'*64
        for i,e in enumerate(entries):
            self.verify_entry(e,previous)
            if i and (e['epoch']!=entries[i-1]['epoch']+1 or e['size']<=entries[i-1]['size']):raise Hold('INVALID_ANCHOR_ORDER')
            previous=e['hash']
        return entries
    def append_anchor(self,epoch,size,root,signatures):
        entries=self.chain()
        if entries and (epoch!=entries[-1]['epoch']+1 or size<=entries[-1]['size']):raise Hold('INVALID_ANCHOR_ORDER')
        if not entries and epoch!=0:raise Hold('ANCHOR_GENESIS_REQUIRED')
        previous=entries[-1]['hash'] if entries else '0'*64
        e=dict(epoch=epoch,size=size,root=root,previous=previous,signatures=signatures)
        e['hash']=digest(e);self.verify_entry(e,previous)
        self.anchor_path.parent.mkdir(parents=True,exist_ok=True)
        fd=os.open(self.anchor_path,os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
        try:os.write(fd,canonical(e)+b'\n');os.fsync(fd)
        finally:os.close(fd)
        return e
    def assess(self):
        try:entries=self.chain()
        except Hold as exc:return 'QUARANTINE_'+str(exc)
        local=self.local()
        if not local:return 'HOLD_NO_LOCAL'
        if not entries:return 'HOLD_NO_ANCHOR'
        head=entries[-1]
        if local['epoch']>head['epoch']:return 'HOLD_UNANCHORED_LOCAL_ADVANCE'
        if local['epoch']<head['epoch']:return 'HOLD_LOCAL_ROLLBACK'
        return 'RECOVERY_MATCH_LOCAL' if (local['size'],local['root'])==(head['size'],head['root']) else 'QUARANTINE_FORK'
def sign_bundle(keys,epoch,size,root,previous):
    msg=signed_payload(epoch,size,root,previous)
    return {name:key.sign(msg).hex() for name,key in keys.items()}
