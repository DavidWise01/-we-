"""WAG-098 reference: signed snapshots in three simulated anchor directories.
This is not actual off-host custody, nor independently witnessed chronology.
"""
import hashlib,json,os,sqlite3
from pathlib import Path
from cryptography.exceptions import InvalidSignature

def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def digest(x): return hashlib.sha256(canonical(x)).hexdigest()
def snapshot(logs,epoch):
    if type(epoch)!=int or epoch<0 or not isinstance(logs,dict) or set(logs)!={'A','B','C'}:raise ValueError('scope')
    if any(not isinstance(v,list) or not v for v in logs.values()):raise ValueError('nonempty logs')
    return {'tag':'WAG098-snapshot-v1','epoch':epoch,'logs':logs}

class Anchor:
    def __init__(self,name,folder,signing_key,pubkey=None):
        self.name=name;self.folder=Path(folder);self.folder.mkdir(parents=True,exist_ok=True)
        self.signer=signing_key;self.public=pubkey or signing_key.public_key()
    def file(self,epoch): return self.folder / f'{epoch:012d}.json'
    def sign(self,state):
        body={'tag':'WAG098-anchor-v1','anchor':self.name,'epoch':state['epoch'],'state_digest':digest(state)}
        return {'body':body,'signature':self.signer.sign(canonical(body)).hex(),'snapshot':state}
    def publish(self,state):
        item=self.sign(state);p=self.file(state['epoch'])
        try:fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        except FileExistsError:raise ValueError('immutable receipt already exists')
        with os.fdopen(fd,'wb') as f:
            f.write(canonical(item));f.flush();os.fsync(f.fileno())
        return item
    def read(self,epoch):
        p=self.file(epoch)
        return json.loads(p.read_text()) if p.is_file() else None

def verify_receipt(item,name,pub,epoch):
    try:
        b=item['body'];s=item['snapshot']
        expected={'tag':'WAG098-anchor-v1','anchor':name,'epoch':epoch,'state_digest':digest(s)}
        if b!=expected or s['epoch']!=epoch or s['tag']!='WAG098-snapshot-v1':return False
        snapshot(s['logs'],epoch)
        pub.verify(bytes.fromhex(item['signature']),canonical(b))
        return True
    except (InvalidSignature,ValueError,TypeError,KeyError,AttributeError,OverflowError):return False

class Recovery:
    def __init__(self,dbpath,anchors):
        if len(anchors)!=3 or len({a.name for a in anchors})!=3:raise ValueError('three anchors')
        self.dbpath=Path(dbpath);self.anchors=anchors;self.incidents=[]
    def decision(self,epoch):
        receipts=[a.read(epoch) for a in self.anchors]
        if any(x is None for x in receipts):
            self.incidents.append(('HOLD_MISSING_ANCHOR',epoch));return ('HOLD_MISSING_ANCHOR',None)
        for a,r in zip(self.anchors,receipts):
            if not verify_receipt(r,a.name,a.public,epoch):
                self.incidents.append(('QUARANTINE_INVALID_RECEIPT',r));return ('QUARANTINE_INVALID_RECEIPT',None)
        states=[r['snapshot'] for r in receipts]
        if len({digest(x) for x in states})!=1:
            self.incidents.append(('QUARANTINE_ANCHOR_DISAGREEMENT',receipts))
            return ('QUARANTINE_ANCHOR_DISAGREEMENT',None)
        return ('VERIFIED_THREE_SIMULATED_ANCHORS',states[0])
    def _connect(self):
        c=sqlite3.connect(self.dbpath);c.execute('PRAGMA synchronous=FULL')
        c.execute('CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), json TEXT NOT NULL)')
        return c
    def install(self,state):
        with self._connect() as c:
            c.execute('INSERT INTO state(id,json) VALUES(1,?) ON CONFLICT(id) DO UPDATE SET json=excluded.json',(canonical(state).decode(),))
    def local(self):
        if not self.dbpath.exists():return None
        try:
            with self._connect() as c:row=c.execute('SELECT json FROM state WHERE id=1').fetchone()
            return json.loads(row[0]) if row else None
        except (ValueError,sqlite3.DatabaseError,KeyError):return None
    def recover(self,epoch):
        _,state=self.decision(epoch)
        if state is None:return self.incidents[-1][0]
        local=self.local()
        if local is not None and digest(local)!=digest(state):
            self.incidents.append(('LOCAL_REPLACEMENT_DETECTED',{'local':local,'trusted':state}))
        self.install(state)
        return 'RECOVERED_AUTHENTICATED_SNAPSHOT' if local!=state else 'MATCHED_AUTHENTICATED_SNAPSHOT'
    def extend(self,new_state,old_epoch):
        status,old=self.decision(old_epoch)
        if old is None:return status
        try:snapshot(new_state['logs'],new_state['epoch'])
        except (KeyError,ValueError,TypeError):return 'HOLD_INVALID_STATE'
        if new_state['epoch']<=old_epoch:return 'HOLD_ROLLBACK'
        for log,leaves in old['logs'].items():
            newer=new_state['logs'][log]
            if len(newer)<len(leaves):return 'HOLD_ROLLBACK'
            if newer[:len(leaves)]!=leaves:
                self.incidents.append(('QUARANTINE_FORK',{'old':old,'new':new_state}))
                return 'QUARANTINE_FORK'
        return 'ELIGIBLE_TO_PUBLISH_NEW_ANCHORS'
