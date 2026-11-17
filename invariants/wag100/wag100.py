"""WAG-100: local synthetic revocation-safe witness succession.

Ed25519 authenticates test-key holders, not real-world organizations.
A SQLite transaction prevents partial local succession; not distributed consensus.
"""
import hashlib, json, os, sqlite3
from contextlib import closing
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()

def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

@dataclass(frozen=True)
class Identity:
    name: str
    ancestor: str
    controller: str
    domain: str
    public_key: bytes

    def __post_init__(self):
        if not all((self.name, self.ancestor, self.controller, self.domain)) or len(self.public_key)!=32:
            raise ValueError('invalid identity')

def sign(key, payload):
    return key.sign(canonical(payload))

def check(public, payload, signature):
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        Ed25519PublicKey.from_public_bytes(public).verify(signature, canonical(payload))
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False

class Succession:
    def __init__(self, db, identities, active=('W1','W2','W3'), root='root-99', epoch=99):
        self.db=db
        self.ids={i.name:i for i in identities}
        if len(self.ids)!=len(tuple(identities)) or len(set(active))!=3 or not set(active)<=set(self.ids):
            raise ValueError('invalid roster')
        self._distinct(active)
        with closing(self._connect()) as conn, conn as c:
            c.execute('CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), epoch INTEGER, root TEXT, roster TEXT, challenge TEXT, quarantined TEXT)')
            c.execute('CREATE TABLE IF NOT EXISTS events (n INTEGER PRIMARY KEY, kind TEXT, data TEXT, prev TEXT, hash TEXT)')
            c.execute('CREATE TABLE IF NOT EXISTS consumed (receipt TEXT PRIMARY KEY)')
            c.execute('CREATE TABLE IF NOT EXISTS revoked (name TEXT PRIMARY KEY, epoch INTEGER, evidence TEXT)')
            if c.execute('SELECT 1 FROM state WHERE id=1').fetchone() is None:
                c.execute('INSERT INTO state VALUES(1,?,?,?,?,?)',(epoch,root,json.dumps(list(active)),f'challenge-{epoch}',None))
                self._append(c,'GENESIS',{'epoch':epoch,'root':root,'active':list(active)})

    def _connect(self):
        c=sqlite3.connect(self.db, timeout=5)
        c.execute('PRAGMA busy_timeout=5000')
        return c

    def _distinct(self, names):
        people=[self.ids[n] for n in names]
        for field in ('ancestor','controller','domain','public_key'):
            if len({getattr(p,field) for p in people})!=len(people):
                raise ValueError('shared '+field)

    def _append(self,c,kind,payload):
        row=c.execute('SELECT n,hash FROM events ORDER BY n DESC LIMIT 1').fetchone()
        n=0 if row is None else row[0]+1
        prev='0'*64 if row is None else row[1]
        d={'n':n,'kind':kind,'data':payload,'prev':prev}
        h=digest(d)
        c.execute('INSERT INTO events VALUES(?,?,?,?,?)',(n,kind,json.dumps(payload,sort_keys=True),prev,h))
        return h

    def state(self):
        c=self._connect()
        try:
            e,r,ro,ch,q=c.execute('SELECT epoch,root,roster,challenge,quarantined FROM state').fetchone()
            return {'epoch':e,'root':r,'roster':tuple(json.loads(ro)),'challenge':ch,'quarantined':q}
        finally:c.close()

    def audit(self):
        c=self._connect()
        try:
            rows=c.execute('SELECT n,kind,data,prev,hash FROM events ORDER BY n').fetchall()
            prev='0'*64
            for j,(n,k,p,pr,h) in enumerate(rows):
                if n!=j or pr!=prev or h!=digest({'n':n,'kind':k,'data':json.loads(p),'prev':pr}):return False
                prev=h
            return True
        finally:c.close()

    def events(self):
        c=self._connect()
        try:return [(k,json.loads(p)) for k,p in c.execute('SELECT kind,data FROM events ORDER BY n')]
        finally:c.close()

    def revoke(self, name, evidence):
        if not isinstance(evidence,str) or not evidence:raise ValueError('evidence required')
        c=self._connect()
        try:
            c.execute('BEGIN IMMEDIATE')
            e,r,ro,ch,q=c.execute('SELECT epoch,root,roster,challenge,quarantined FROM state').fetchone()
            if name not in json.loads(ro):raise ValueError('not active')
            if c.execute('SELECT 1 FROM revoked WHERE name=?',(name,)).fetchone():raise ValueError('already revoked')
            c.execute('INSERT INTO revoked VALUES(?,?,?)',(name,e,evidence))
            c.execute('UPDATE state SET quarantined=? WHERE id=1',(name,))
            self._append(c,'REVOKE',{'name':name,'epoch':e,'evidence':evidence})
            c.commit()
        except Exception:c.rollback();raise
        finally:c.close()

    def rotate(self, old, new, approvals, new_root):
        """Two distinct surviving reviewers sign same exact proposal; require fresh epoch and root."""
        c=self._connect()
        try:
            c.execute('BEGIN IMMEDIATE')
            e,r,ro,ch,q=c.execute('SELECT epoch,root,roster,challenge,quarantined FROM state').fetchone()
            active=json.loads(ro)
            if q!=old or old not in active or new in active or new not in self.ids:raise ValueError('invalid succession')
            if not c.execute('SELECT 1 FROM revoked WHERE name=?',(old,)).fetchone():raise ValueError('no revocation')
            if c.execute('SELECT 1 FROM revoked WHERE name=?',(new,)).fetchone():raise ValueError('successor revoked')
            if not isinstance(new_root,str) or not new_root or new_root==r:raise ValueError('need new root')
            reviewers=set(active)-{old}
            if set(approvals)!=reviewers:raise ValueError('two reviewers required')
            self._distinct(list(reviewers)+[new])
            # Replacement may not share origin with retired signer (even though no longer in ring).
            oldid,newid=self.ids[old],self.ids[new]
            for field in ('ancestor','controller','domain','public_key'):
                if getattr(oldid,field)==getattr(newid,field):raise ValueError('retired control reused')
            proposal={'operation':'rotate','old':old,'new':new,'epoch':e,'prior_root':r,'next_root':new_root,'challenge':ch}
            receipts=[]
            for name in sorted(reviewers):
                sig=approvals[name]
                if not check(self.ids[name].public_key,proposal,sig):raise ValueError('bad review signature')
                rid=digest({'signer':name,'proposal':proposal,'signature':sig.hex()})
                if c.execute('SELECT 1 FROM consumed WHERE receipt=?',(rid,)).fetchone():raise ValueError('reused review')
                receipts.append(rid)
            for rid in receipts:c.execute('INSERT INTO consumed VALUES(?)',(rid,))
            next_roster=sorted(reviewers|{new})
            c.execute('UPDATE state SET epoch=?,root=?,roster=?,challenge=?,quarantined=NULL WHERE id=1',(e+1,new_root,json.dumps(next_roster),f'challenge-{e+1}',))
            self._append(c,'ROTATE',{'proposal':proposal,'approvers':sorted(reviewers),'active':next_roster})
            c.commit()
            return proposal
        except Exception:c.rollback();raise
        finally:c.close()

    def certify(self, attestations):
        c=self._connect()
        try:
            c.execute('BEGIN IMMEDIATE')
            e,r,ro,ch,q=c.execute('SELECT epoch,root,roster,challenge,quarantined FROM state').fetchone()
            active=json.loads(ro)
            if q or set(attestations)!=set(active):raise ValueError('quorum missing or quarantined')
            statement={'operation':'attest','epoch':e,'root':r,'challenge':ch,'roster':sorted(active)}
            receipts=[]
            for name in sorted(active):
                if c.execute('SELECT 1 FROM revoked WHERE name=?',(name,)).fetchone():raise ValueError('revoked signer')
                sig=attestations[name]
                if not check(self.ids[name].public_key,statement,sig):raise ValueError('invalid attestation')
                rid=digest({'signer':name,'statement':statement,'signature':sig.hex()})
                if c.execute('SELECT 1 FROM consumed WHERE receipt=?',(rid,)).fetchone():raise ValueError('replay')
                receipts.append(rid)
            for rid in receipts:c.execute('INSERT INTO consumed VALUES(?)',(rid,))
            self._append(c,'CERTIFY',{'statement':statement,'signers':sorted(active)})
            c.commit()
            return 'LOCAL_RECONSTITUTED_QUORUM'
        except Exception:c.rollback();raise
        finally:c.close()

    def historic(self, name):
        c=self._connect()
        try:return c.execute('SELECT epoch,evidence FROM revoked WHERE name=?',(name,)).fetchone()
        finally:c.close()


def demo(db):
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    keys={w:Ed25519PrivateKey.generate() for w in ('W1','W2','W3','W4')}
    ids=[Identity(w,'ancestor-'+w,'controller-'+w,'domain-'+w,keys[w].public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)) for w in keys]
    a=Succession(db,ids)
    a.revoke('W1','equivocation-signed-A-and-B')
    s=a.state()
    proposal={'operation':'rotate','old':'W1','new':'W4','epoch':s['epoch'],'prior_root':s['root'],'next_root':'root-100','challenge':s['challenge']}
    a.rotate('W1','W4',{w:sign(keys[w],proposal) for w in ('W2','W3')},'root-100')
    s=a.state()
    statement={'operation':'attest','epoch':s['epoch'],'root':s['root'],'challenge':s['challenge'],'roster':sorted(s['roster'])}
    result=a.certify({w:sign(keys[w],statement) for w in s['roster']})
    return a,keys,{'status':result,'state':a.state(),'historical':a.historic('W1'),'audit':a.audit(),'records':len(a.events())}

if __name__=='__main__':
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        _,_,result=demo(os.path.join(d,'succession.sqlite'))
        print(json.dumps(result,indent=2))
