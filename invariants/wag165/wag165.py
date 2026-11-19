import hashlib,json

def H(b): return hashlib.sha256(b).digest()
def enc(v): return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def leaf(v): return H(b'\x00'+enc(v))
def pair(a,b): return H(b'\x01'+a+b)
def split(n): return 1<<((n-1).bit_length()-1)
def root(xs):
    if not xs:return H(b'')
    if len(xs)==1:return xs[0]
    k=split(len(xs));return pair(root(xs[:k]),root(xs[k:]))
def proof(xs,i):
    if not 0<=i<len(xs):raise ValueError('index')
    if len(xs)==1:return []
    k=split(len(xs))
    return proof(xs[:k],i)+[root(xs[k:])] if i<k else proof(xs[k:],i-k)+[root(xs[:k])]
def verify(record,i,n,path,expected):
    if not 0<=i<n:return False
    it=iter(path)
    def fold(i,n):
        if n==1:return leaf(record)
        k=split(n)
        return pair(fold(i,k),next(it)) if i<k else right(i,k,n)
    def right(i,k,n):
        r=fold(i-k,n-k);return pair(next(it),r)
    try:
        got=fold(i,n)
        return next(it,None) is None and got==expected
    except (StopIteration,TypeError):return False

def records(n=165):
    out=[]
    for i in range(n):
        x=[3,2,1,3,2,1,2,2,2,2];b=[54]*10
        for k in range(min(i,2)):
            j=k*3;x[j]-=1;x[j+2]+=1;b[j]-=1;b[j+1]-=1
        out.append(dict(generation=i,parent=leaf(out[-1]).hex() if out else None,x=x,b=b,center=6,spent=2*min(i,2)))
    return out
if __name__=='__main__':
    rs=records();xs=list(map(leaf,rs));r=root(xs)
    sizes=[len(proof(xs,i)) for i in range(len(xs))]
    assert all(verify(v,i,len(xs),proof(xs,i),r) for i,v in enumerate(rs))
    assert all(sum(v['x'])+v['center']==26 and sum(v['b'])+v['spent']==540 for v in rs)
    print('records',len(rs),'root',r.hex());print('proof hashes min/max',min(sizes),max(sizes));print('proof bytes max',max(sizes)*32,'full canonical records bytes',sum(len(enc(v)) for v in rs));print('last proof hashes',sizes[-1]);print('all 165 inclusion proofs verified')
