"""Append-only binary Merkle frontier; trusted prior frontier required."""
from hashlib import sha256

def leaf(data): return sha256(b'\x00'+data).digest()
def node(a,b): return sha256(b'\x01'+a+b).digest()
def root(n,f):
    validate(n,f)
    r=None
    for k in sorted(f): r=f[k] if r is None else node(f[k],r)
    return r if r is not None else sha256(b'').digest()
def validate(n,f):
    if type(n)!=int or n<0 or set(f)!={k for k in range(n.bit_length()) if n>>k&1}: raise ValueError('frontier shape')
    if any(type(x)!=bytes or len(x)!=32 for x in f.values()): raise ValueError('hash')
def append(n,f,k,h):
    validate(n,f)
    if type(k)!=int or k<0 or type(h)!=bytes or len(h)!=32 or n%(1<<k): raise ValueError('unaligned block')
    f=dict(f); size=1<<k
    while k in f: h=node(f.pop(k),h); k+=1
    f[k]=h
    return n+size,f
def block_size(n,end):
    remaining=end-n
    k=remaining.bit_length()-1
    return min(k,(n&-n).bit_length()-1) if n else k
def verify(old_n,old_f,new_n,new_root,proof):
    try:
        validate(old_n,old_f)
        if type(new_n)!=int or new_n<old_n:return False
        n,f=old_n,dict(old_f)
        for k,h in proof:
            if n>=new_n or k!=block_size(n,new_n):return False
            n,f=append(n,f,k,h)
        return n==new_n and root(n,f)==new_root
    except (ValueError,TypeError,OverflowError):return False
def tree(xs):
    if len(xs)==1:return xs[0]
    m=1<<((len(xs)-1).bit_length()-1)
    return node(tree(xs[:m]),tree(xs[m:]))
def proof(xs,start):
    out=[]; n=start
    while n<len(xs):
        k=block_size(n,len(xs)); end=n+(1<<k)
        out.append((k,tree(xs[n:end]))); n=end
    return out
def frontier(xs):
    n,f=0,{}
    for h in xs:n,f=append(n,f,0,h)
    return n,f
