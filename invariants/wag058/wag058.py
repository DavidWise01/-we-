"""WAG-058: compact RFC6962-style consistency and authenticated witness gossip.
Reference demonstration only; keys, time, witness identity and network are local.
"""
import hashlib,json
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def H(b):return hashlib.sha256(b).digest()
def leaf(b):return H(b'\0'+b)
def node(a,b):return H(b'\1'+a+b)
def split(n):return 1<<((n-1).bit_length()-1)
def root(items):
    if not items:return H(b'')
    if len(items)==1:return leaf(items[0])
    k=split(len(items))
    return node(root(items[:k]),root(items[k:]))
def proof(items,m):
    if not 0<m<=len(items):raise ValueError('size')
    def sub(v,k,b):
        if len(v)==k:return [] if b else [root(v)]
        cut=split(len(v))
        return (sub(v[:cut],k,b)+[root(v[cut:])] if k<=cut
                else sub(v[cut:],k-cut,False)+[root(v[:cut])])
    return [x.hex() for x in sub(items,m,True)]
def verify(m,n,old,new,path):
    if type(m)!=int or type(n)!=int or not 0<m<=n:return False
    try:
        a,b=bytes.fromhex(old),bytes.fromhex(new)
        p=[bytes.fromhex(x) for x in path]
        if len(a)!=32 or len(b)!=32 or any(len(x)!=32 for x in p):return False
    except (TypeError,ValueError):return False
    if m==n:return a==b and not p
    fn=m-1;sn=n-1
    while fn&1:fn>>=1;sn>>=1
    if fn==0:fr=sr=a;index=0
    else:
        if not p:return False
        fr=sr=p[0];index=1
    for h in p[index:]:
        if sn==0:return False
        if fn&1 or fn==sn:
            fr=node(h,fr);sr=node(h,sr)
            while fn and not fn&1:fn>>=1;sn>>=1
        else:sr=node(sr,h)
        fn>>=1;sn>>=1
    return fr==a and sr==b and sn==0
def msg(log,n,r,t):return canon({'domain':'WAG058:log-head:v1','log':log,'size':n,'root':r,'epoch':t})
def gossipmsg(w,head,t):return canon({'domain':'WAG058:gossip:v1','witness':w,'head':head,'epoch':t})
def check(key,message,sig):
    try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(key)).verify(bytes.fromhex(sig),message)
    except (ValueError,InvalidSignature,TypeError):raise ValueError('bad signature')
@dataclass(frozen=True)
class Head:
    log:str
    size:int
    root:str
    epoch:int
    signature:str
@dataclass(frozen=True)
class Witness:
    name:str
    root:str
    domain:str
    public_key:str
class Auditor:
    def __init__(self,log,key,minimum=3):
        if not log or not key or minimum<3:raise ValueError('policy')
        self.log=log;self.key=key;self.minimum=minimum
        self.witnesses={};self.reports={};self.proofs={};self.events=[];self.closed=False
        self.append('policy',{'log':log,'key':key,'minimum':minimum})
    def append(self,kind,data):
        x={'seq':len(self.events),'prev':self.events[-1]['hash'] if self.events else '0'*64,
           'kind':kind,'data':data}
        x['hash']=H(canon(x)).hex();self.events.append(x)
    def verify_history(self):
        return all(x['seq']==i and x['prev']==(self.events[i-1]['hash'] if i else '0'*64)
            and x['hash']==H(canon({k:v for k,v in x.items() if k!='hash'})).hex()
            for i,x in enumerate(self.events))
    def register(self,w):
        if self.closed or not isinstance(w,Witness) or not all(vars(w).values()) or w.name in self.witnesses or any(w.root==x.root or w.domain==x.domain for x in self.witnesses.values()):raise ValueError('witness')
        self.witnesses[w.name]=w;self.append('witness',vars(w))
    def submit(self,name,head,epoch,signature):
        if self.closed or name not in self.witnesses or name in self.reports or not isinstance(head,Head) or head.log!=self.log or type(head.size)!=int or head.size<1 or type(head.epoch)!=int or epoch<head.epoch:raise ValueError('report')
        m=msg(head.log,head.size,head.root,head.epoch)
        check(self.key,m,head.signature)
        hh=H(m+bytes.fromhex(head.signature)).hex()
        check(self.witnesses[name].public_key,gossipmsg(name,hh,epoch),signature)
        self.reports[name]=head
        self.append('gossip',{'witness':name,'head':vars(head),'epoch':epoch,'signature':signature})
    def add_proof(self,small,large,small_root,large_root,path):
        if self.closed or not 0<small<large or not isinstance(path,(list,tuple)):raise ValueError('proof')
        key=(small,large,small_root,large_root)
        if key in self.proofs:raise ValueError('duplicate proof')
        result=verify(small,large,small_root,large_root,path)
        self.proofs[key]=result;self.append('proof',{'key':key,'path':list(path),'valid':result})
        return result
    def decide(self):
        if self.closed:raise ValueError('closed')
        heads=list(self.reports.items());conflicts=[];missing=[]
        for i,(wa,a) in enumerate(heads):
            for wb,b in heads[i+1:]:
                if a.size==b.size:
                    if a.root!=b.root:conflicts.append((wa,wb,'SAME_SIZE_EQUIVOCATION'))
                else:
                    s,l=(a,b) if a.size<b.size else (b,a)
                    k=(s.size,l.size,s.root,l.root)
                    if k in self.proofs and not self.proofs[k]:conflicts.append((wa,wb,'INVALID_PROOF'))
                    elif k not in self.proofs:missing.append((wa,wb,'MISSING_PROOF'))
        status=('QUARANTINE_CONFLICT' if conflicts else
                'HOLD_INCOMPLETE' if len(heads)<self.minimum or missing else
                'CONSISTENT_RECEIVED_VIEWS')
        result={'status':status,'reports':len(heads),'conflicts':conflicts,'missing':missing}
        self.closed=True;self.append('decision',result);return result

def demo():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    pub=lambda k:k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()
    operator=Ed25519PrivateKey.generate();a=Auditor('JANE-LOG',pub(operator))
    leaves=[('event-'+str(i)).encode() for i in range(6)]
    for i,n in enumerate((3,6,6)):
        w='W'+str(i+1);k=Ed25519PrivateKey.generate()
        a.register(Witness(w,'root'+str(i),'domain'+str(i),pub(k)))
        h=Head('JANE-LOG',n,root(leaves[:n]).hex(),10,'')
        h=Head(h.log,h.size,h.root,h.epoch,operator.sign(msg(h.log,h.size,h.root,h.epoch)).hex())
        m=msg(h.log,h.size,h.root,h.epoch);hh=H(m+bytes.fromhex(h.signature)).hex()
        a.submit(w,h,11,k.sign(gossipmsg(w,hh,11)).hex())
    a.add_proof(3,6,root(leaves[:3]).hex(),root(leaves).hex(),proof(leaves,3))
    return a,a.decide()
if __name__=='__main__':
    a,r=demo();print(r,'records',len(a.events),'ledger',a.verify_history())
