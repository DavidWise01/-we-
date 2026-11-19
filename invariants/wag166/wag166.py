import hashlib, json

def H(b): return hashlib.sha256(b).digest()
def leaf(v): return H(b'\x00'+json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def pair(a,b): return H(b'\x01'+a+b)
def split(n): return 1<<((n-1).bit_length()-1)
def root(xs):
    if not xs:return H(b'')
    if len(xs)==1:return xs[0]
    k=split(len(xs));return pair(root(xs[:k]),root(xs[k:]))

def proof(xs,m):
    if not 0<m<=len(xs):raise ValueError('size')
    def sub(xs,m,b):
        if m==len(xs):return [] if b else [root(xs)]
        k=split(len(xs))
        if m<=k:return sub(xs[:k],m,b)+[root(xs[k:])]
        return sub(xs[k:],m-k,False)+[root(xs[:k])]
    return sub(xs,m,True)

def verify(m,n,old,new,p):
    if type(m)!=int or type(n)!=int or not 0<m<=n:return False
    if any(type(v)!=bytes or len(v)!=32 for v in [old,new,*p]):return False
    it=iter(p)
    def fold(m,n,b):
        if m==n:
            v=old if b else next(it);return v,v
        k=split(n)
        if m<=k:
            a,c=fold(m,k,b);return a,pair(c,next(it))
        a,c=fold(m-k,n-k,False);l=next(it);return pair(l,a),pair(l,c)
    try:
        a,c=fold(m,n,True)
        return a==old and c==new and next(it,None) is None
    except StopIteration:return False

def records(n):
    rs=[]
    for i in range(n):
        x=[3,2,1,3,2,1,2,2,2,2];b=[54]*10
        for k in range(min(i,2)):
            j=k*3;x[j]-=1;x[j+2]+=1;b[j]-=1;b[j+1]-=1
        rs.append(dict(generation=i,parent=leaf(rs[-1]).hex() if rs else None,x=x,b=b,center=6,spent=2*min(i,2)))
    return rs

if __name__=='__main__':
    xs=list(map(leaf,records(166)));p=proof(xs,165)
    assert verify(165,166,root(xs[:165]),root(xs),p)
    print('old',root(xs[:165]).hex());print('new',root(xs).hex());print('proof hashes',len(p),'bytes',32*len(p))
