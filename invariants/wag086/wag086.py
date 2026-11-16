"""WAG-086: synthetic sampled storage audit, not a proof of retrievability."""
import hashlib, hmac, json, os, sqlite3
from dataclasses import dataclass
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

def H(b):return hashlib.sha256(b).digest()
def leaf(b):return H(b'\x00'+b)
def node(a,b):return H(b'\x01'+a+b)
def merkle(chunks):
    if not chunks:raise ValueError('empty archive')
    level=[leaf(c) for c in chunks]; layers=[level]
    while len(level)>1:
        level=[node(level[i],level[i+1]) if i+1<len(level) else level[i] for i in range(0,len(level),2)]
        layers.append(level)
    return layers[-1][0],layers
def proof(layers,index):
    if index<0 or index>=len(layers[0]):raise ValueError('index')
    out=[];i=index
    for level in layers[:-1]:
        sibling=i^1
        out.append(level[sibling].hex() if sibling<len(level) else None)
        i//=2
    return out
def verify(chunk,index,count,siblings,root):
    if not isinstance(chunk,bytes) or count<=0 or not 0<=index<count:return False
    height=0;n=count
    while n>1: height+=1;n=(n+1)//2
    if len(siblings)!=height:return False
    cur=leaf(chunk);i=index;n=count
    try:
        for s in siblings:
            if i^1>=n:
                if s is not None:return False
            else:
                if not isinstance(s,str) or len(s)!=64:return False
                sib=bytes.fromhex(s)
                cur=node(sib,cur) if i%2 else node(cur,sib)
            i//=2;n=(n+1)//2
    except (ValueError,TypeError):return False
    return hmac.compare_digest(cur,root)
def challenge_indices(seed,count,k):
    if not isinstance(seed,bytes) or len(seed)<16 or not 0<k<=count:raise ValueError('challenge')
    # deterministic rejection-sampled pseudo-random selection from challenge seed
    chosen=set();counter=0
    bitlen=(count-1).bit_length();limit=1<<bitlen
    while len(chosen)<k:
        block=H(b'WAG086-SAMPLE'+seed+counter.to_bytes(8,'big'));counter+=1
        v=int.from_bytes(block,'big')%limit
        if v<count:chosen.add(v)
    return tuple(sorted(chosen))
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
@dataclass(frozen=True)
class Host:
    name:str
    ancestor:str
    domain:str
    key:Ed25519PrivateKey
class Gate:
    def __init__(self,db,hosts,root,count,epoch=86,k=3):
        self.hosts=tuple(hosts);self.root=root;self.count=count;self.epoch=epoch;self.k=k
        if len(hosts)!=3 or len({h.name for h in hosts})!=3 or len({h.ancestor for h in hosts})!=3 or len({h.domain for h in hosts})!=3:raise ValueError('host declarations')
        if len(root)!=32 or not 0<k<=count:raise ValueError('root/sample size')
        self.db=Path(db);self.conn=sqlite3.connect(self.db)
        self.conn.execute('create table if not exists used(nonce text primary key)')
        self.conn.execute('create table if not exists ledger(seq integer primary key,kind text, payload text, previous text, hash text)')
        self.conn.commit()
    def close(self):self.conn.close()
    def audit(self,kind,payload):
        prev=self.conn.execute('select hash from ledger order by seq desc limit 1').fetchone()
        row=(kind,canon(payload).decode(),prev[0] if prev else '0'*64)
        d=H(canon(row)).hex();self.conn.execute('insert into ledger(kind,payload,previous,hash) values(?,?,?,?)',(*row,d))
    def ledger_ok(self):
        rows=self.conn.execute('select kind,payload,previous,hash from ledger order by seq').fetchall();prev='0'*64
        for kind,payload,p,h in rows:
            if p!=prev or H(canon((kind,payload,p))).hex()!=h:return False
            prev=h
        return True
    def signed_response(self,host,chunks,nonce):
        root,layers=merkle(chunks)
        indices=challenge_indices(nonce,self.count,self.k)
        samples=[{'i':i,'chunk':chunks[i].hex(),'path':proof(layers,i)} for i in indices]
        body={'protocol':'WAG-086-v1','host':host.name,'epoch':self.epoch,'root':self.root.hex(),'count':self.count,'nonce':nonce.hex(),'indices':list(indices),'samples':samples}
        return {'body':body,'signature':host.key.sign(canon(body)).hex()}
    def accept(self,responses,nonce):
        if not isinstance(nonce,bytes) or len(nonce)<16:raise ValueError('nonce')
        if len(responses)!=3:raise ValueError('three host responses required')
        indices=challenge_indices(nonce,self.count,self.k)
        seen=set()
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            if self.conn.execute('select 1 from used where nonce=?',(nonce.hex(),)).fetchone():raise ValueError('replayed challenge')
            for resp in responses:
                body=resp['body'];name=body['host']
                if name in seen:raise ValueError('duplicate host')
                host=next((h for h in self.hosts if h.name==name),None)
                if host is None:raise ValueError('unknown host')
                try:host.key.public_key().verify(bytes.fromhex(resp['signature']),canon(body))
                except (InvalidSignature,ValueError,TypeError):raise ValueError('bad signature')
                if body['protocol']!='WAG-086-v1' or body['epoch']!=self.epoch or body['root']!=self.root.hex() or body['count']!=self.count or body['nonce']!=nonce.hex() or body['indices']!=list(indices):raise ValueError('wrong snapshot/challenge')
                if [s['i'] for s in body['samples']]!=list(indices):raise ValueError('wrong sampled indices')
                for s in body['samples']:
                    if not verify(bytes.fromhex(s['chunk']),s['i'],self.count,s['path'],self.root):raise ValueError('bad inclusion proof')
                seen.add(name)
            if seen!={h.name for h in self.hosts}:raise ValueError('missing host')
            self.conn.execute('insert into used(nonce) values(?)',(nonce.hex(),))
            self.audit('sample-audit-accepted',{'epoch':self.epoch,'nonce':nonce.hex(),'root':self.root.hex(),'hosts':sorted(seen),'indices':indices})
            self.conn.commit();return 'LOCAL_SAMPLED_STORAGE_ELIGIBLE'
        except Exception:
            self.conn.rollback();raise

def demo(db=':memory:'):
    chunks=[f'block-{i:04d}'.encode() for i in range(17)]
    root,_=merkle(chunks)
    hosts=[Host(f'W{i}',f'ancestor-{i}',f'domain-{i}',Ed25519PrivateKey.generate()) for i in range(1,4)]
    gate=Gate(db,hosts,root,len(chunks));nonce=b'fixed-demo-nonce-086'
    responses=[gate.signed_response(h,chunks,nonce) for h in hosts]
    try:
        decision=gate.accept(responses,nonce)
        try:gate.accept(responses,nonce);replay='NOT_REJECTED'
        except ValueError:replay='REJECTED'
        return {'decision':decision,'replay':replay,'indices':challenge_indices(nonce,len(chunks),3),'audit_ok':gate.ledger_ok(),'events':gate.conn.execute('select count(*) from ledger').fetchone()[0]}
    finally:gate.close()
if __name__=='__main__':print(demo())