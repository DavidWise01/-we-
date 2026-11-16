"""WAG-093 GitHub compact reference: frozen-root / signed-beacon / Merkle evidence.
Full 45-test local version is supplied as a separate conversation artifact.
"""
import hashlib, json, sqlite3
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def H(b):return hashlib.sha256(b).digest()
def root_proof(chunks,index):
    if not chunks or index<0 or index>=len(chunks):raise ValueError('index')
    level=[H(b'\0'+x) for x in chunks];i=index;path=[]
    while len(level)>1:
        s=i^1;path.append(level[s].hex() if s<len(level) else None)
        level=[H(b'\1'+level[j]+level[j+1]) if j+1<len(level) else level[j] for j in range(0,len(level),2)]
        i//=2
    return level[0],path
def included(data,index,n,siblings,root):
    if not isinstance(data,bytes) or index<0 or index>=n:return False
    cur=H(b'\0'+data)
    try:
        for sibling in siblings:
            if n<=1:return False
            if index^1>=n:
                if sibling is not None:return False
            else:
                s=bytes.fromhex(sibling)
                cur=H(b'\1'+(s+cur if index%2 else cur+s))
            index//=2;n=(n+1)//2
    except (TypeError,ValueError):return False
    return n==1 and cur==root
def sample(seed,n,k):
    if len(seed)<16 or not 0<k<=n:raise ValueError('sample')
    seen=set();x=0;limit=(1<<256)//n*n
    while len(seen)<k:
        h=int.from_bytes(H(b'WAG093'+seed+x.to_bytes(8,'big')),'big');x+=1
        if h<limit:seen.add(h%n)
    return sorted(seen)
class Gate:
    def __init__(self,db,beacon_public,hosts):
        if len(hosts)!=3 or len(set(hosts))!=3:raise ValueError('three hosts')
        self.beacon_public=beacon_public;self.hosts=hosts
        self.db=sqlite3.connect(db,isolation_level=None)
        self.db.execute('CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY CHECK(id=1),epoch INTEGER,root TEXT,n INTEGER,receipt TEXT,nonce TEXT,indices TEXT,status TEXT)')
    def close(self):self.db.close()
    def freeze(self,epoch,root,n,receipt):
        if len(root)!=32 or n<3 or not receipt:raise ValueError('archive')
        try:self.db.execute('INSERT INTO state VALUES(1,?,?,?,?,?,?,?)',(epoch,root.hex(),n,receipt,None,None,'FROZEN'))
        except sqlite3.IntegrityError as e:raise ValueError('already frozen') from e
    def beacon(self,body,signature):
        row=self.db.execute('SELECT epoch,root,n,status FROM state').fetchone()
        if not row or row[-1]!='FROZEN':raise ValueError('not frozen')
        try:self.beacon_public.verify(bytes.fromhex(signature),enc(body))
        except Exception as e:raise ValueError('invalid beacon') from e
        epoch,root,n,_=row
        if body.get('v')!='WAG093' or body.get('epoch')!=epoch or not isinstance(body.get('value'),str):raise ValueError('beacon mismatch')
        nonce=H(b'WAG093-fixed'+enc([epoch,root,n,body])).hex()
        indices=sample(bytes.fromhex(nonce),n,3)
        self.db.execute('UPDATE state SET nonce=?,indices=?,status=?',(nonce,json.dumps(indices),'CHALLENGED'))
        return indices
    def certify(self,reports):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self.db.execute('SELECT epoch,root,n,nonce,indices,status FROM state').fetchone()
            if not row or row[-1]!='CHALLENGED' or len(reports)!=3:raise ValueError('no fresh three-signature quorum')
            epoch,root,n,nonce,indices,_=row;seen=set()
            for report in reports:
                b=report['body'];host=b['host']
                if host not in self.hosts or host in seen:raise ValueError('host')
                try:self.hosts[host].verify(bytes.fromhex(report['signature']),enc(b))
                except Exception as e:raise ValueError('host signature') from e
                if (b['epoch'],b['root'],b['nonce'])!=(epoch,root,nonce):raise ValueError('frozen context')
                if [s['i'] for s in b['samples']]!=json.loads(indices):raise ValueError('sample')
                for s in b['samples']:
                    if not included(bytes.fromhex(s['data']),s['i'],n,s['siblings'],bytes.fromhex(root)):raise ValueError('inclusion')
                seen.add(host)
            self.db.execute("UPDATE state SET status='CERTIFIED'")
            self.db.commit();return 'LOCAL_E2E_SAMPLED_STORAGE_ELIGIBLE'
        except Exception:self.db.rollback();raise
def demonstration():
    chunks=[f'chunk-{i}'.encode() for i in range(17)]
    root,_=root_proof(chunks,0);beacon=Ed25519PrivateKey.generate()
    private={f'W{i}':Ed25519PrivateKey.generate() for i in (1,2,3)}
    gate=Gate(':memory:',beacon.public_key(),{k:v.public_key() for k,v in private.items()})
    gate.freeze(93,root,17,'archive-commit')
    body={'v':'WAG093','epoch':93,'value':'beacon-output'}
    ids=gate.beacon(body,beacon.sign(enc(body)).hex())
    row=gate.db.execute('SELECT nonce FROM state').fetchone();nonce=row[0]
    reports=[]
    for name,key in private.items():
        samples=[{'i':i,'data':chunks[i].hex(),'siblings':root_proof(chunks,i)[1]} for i in ids]
        b={'epoch':93,'root':root.hex(),'nonce':nonce,'host':name,'samples':samples}
        reports.append({'body':b,'signature':key.sign(enc(b)).hex()})
    try:return {'decision':gate.certify(reports),'indices':ids}
    finally:gate.close()
if __name__=='__main__':print(demonstration())
