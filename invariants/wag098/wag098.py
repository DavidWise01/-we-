"""WAG-098 repository reference: signed cross-size Merkle gossip.
Synthetic keys and declared ancestry; not distributed Byzantine consensus.
Compact aligned-subtree frontier proof, not RFC6962 wire proof format.
"""
import hashlib,json
from dataclasses import dataclass
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def leaf(x):return hashlib.sha256(b'\0'+x).digest()
def node(a,b):return hashlib.sha256(b'\1'+a+b).digest()
def root(xs):
    if not xs:return hashlib.sha256(b'').digest()
    if len(xs)==1:return leaf(xs[0])
    n=1<<((len(xs)-1).bit_length()-1)
    return node(root(xs[:n]),root(xs[n:]))
def cover(a,b):
    out=[]
    while a<b:
        n=1<<((b-a).bit_length()-1)
        if a:n=min(n,a&-a)
        out.append((a,n));a+=n
    return out
def proof(xs,m):
    if not 1<=m<=len(xs):raise ValueError('prefix size')
    return {'m':m,'n':len(xs),'before':[(a,k,root(xs[a:a+k]).hex()) for a,k in cover(0,m)],
            'after':[(a,k,root(xs[a:a+k]).hex()) for a,k in cover(m,len(xs))]}
def fold(blocks):
    stack=[]
    for a,n,h in blocks:
        v=bytes.fromhex(h)
        if len(v)!=32:raise ValueError('digest')
        stack.append((a,n,v))
        while len(stack)>1:
            x,k,hx=stack[-2];y,j,hy=stack[-1]
            if k!=j or x+k!=y or x%(2*k)!=0:break
            stack[-2:]=[(x,2*k,node(hx,hy))]
    v=stack[-1][2]
    for _,_,h in reversed(stack[:-1]):v=node(h,v)
    return v
def verify(p,m,old,n,new):
    try:
        if p['m']!=m or p['n']!=n or not 1<=m<=n:return False
        a=p['before'];b=p['after']
        if [(s,k) for s,k,_ in a]!=cover(0,m) or [(s,k) for s,k,_ in b]!=cover(m,n):return False
        return fold(a)==old and fold(a+b)==new
    except (KeyError,TypeError,IndexError,ValueError):return False
@dataclass(frozen=True)
class Observer:
    name:str
    ancestor:str
    operator:str
    domain:str
    key:object
def sign_head(private,log,epoch,xs):
    body={'log':log,'epoch':epoch,'size':len(xs),'root':root(xs).hex()}
    return {'body':body,'sig':private.sign(b'HEAD\0'+enc(body))}
def sign_gossip(private,name,head,nonce):
    body={'observer':name,'head':head['body'],'nonce':nonce}
    return {'body':body,'sig':private.sign(b'GOSSIP\0'+enc(body))}
def sig_ok(public,signed,prefix):
    try:public.verify(signed['sig'],prefix+enc(signed['body']));return True
    except (InvalidSignature,ValueError,TypeError,KeyError):return False
class Gate:
    def __init__(self,log,epoch,nonce,log_key,observers):
        if len(observers)!=3:raise ValueError('three observers')
        for attr in ('name','ancestor','operator','domain'):
            vals=[getattr(o,attr) for o in observers]
            if len(set(vals))!=3 or not all(vals):raise ValueError('declared independence')
        self.log=log;self.epoch=epoch;self.nonce=nonce;self.log_key=log_key
        self.observers={o.name:o for o in observers}
        self.views={};self.edges=set();self.events=[];self.decision='HOLD_NO_OBSERVERS'
    def observe(self,name,head,gossip,prior=None,consistency=None):
        if name not in self.observers:raise ValueError('observer')
        if not sig_ok(self.log_key,head,b'HEAD\0'):raise ValueError('log signature')
        if not sig_ok(self.observers[name].key,gossip,b'GOSSIP\0'):raise ValueError('observer signature')
        h=head['body']
        if h['log']!=self.log or h['epoch']!=self.epoch or h['size']<1:raise ValueError('scope')
        if gossip['body']!={'observer':name,'head':h,'nonce':self.nonce}:raise ValueError('challenge')
        if prior is not None:
            if not sig_ok(self.log_key,prior,b'HEAD\0'):raise ValueError('old signature')
            o=prior['body']
            if o['log']!=self.log or o['epoch']!=self.epoch:raise ValueError('old scope')
            if not verify(consistency,o['size'],bytes.fromhex(o['root']),h['size'],bytes.fromhex(h['root'])):
                self.events.append(('INVALID_PROOF',prior,head))
                self.decision='HOLD_INVALID_PREFIX_PROOF';return self.decision
            self.edges.add((o['size'],o['root'],h['size'],h['root']))
        for (who,n,r),signed in self.views.items():
            if n==h['size'] and r!=h['root']:
                self.events.append(('SIGNED_FORK',signed,head))
                self.decision='QUARANTINE_SPLIT_VIEW';return self.decision
        self.views[(name,h['size'],h['root'])]=head
        self.events.append(('OBSERVE',name,h))
        if self.decision.startswith('QUARANTINE'):return self.decision
        high=max(n for _,n,_ in self.views);last={r for _,n,r in self.views if n==high}
        if len(last)!=1:self.decision='HOLD_UNPROVEN_EXTENSION';return self.decision
        target=(high,next(iter(last)))
        def reaches(start):
            if start==target:return True
            queue=[start];seen={start}
            while queue:
                u=queue.pop()
                for a,ar,b,br in self.edges:
                    v=(b,br)
                    if u==(a,ar) and v not in seen:
                        if v==target:return True
                        seen.add(v);queue.append(v)
            return False
        if not all(reaches((n,r)) for _,n,r in self.views):
            self.decision='HOLD_UNPROVEN_EXTENSION'
        elif len({who for who,n,r in self.views if (n,r)==target})==3:
            self.decision='LOCAL_CROSS_SIZE_AGREEMENT'
        else:self.decision='HOLD_INCOMPLETE_GOSSIP'
        return self.decision
