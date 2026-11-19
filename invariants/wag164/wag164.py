import hashlib,json
from copy import deepcopy

def digest(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def genesis():
    return dict(generation=0,parent=None,branches=[],x=[3,2,1,3,2,1,2,2,2,2],b=[54]*10,spent=0,center=6)

def proposal(parent,path,amount=1):
    return dict(parent=digest(parent),path=list(path),amount=amount)

def advance(parent,branches):
    s=deepcopy(parent); seen=set(); ids=[]
    for q in sorted(branches,key=digest):
        p,a=q['path'],q['amount']
        if q['parent']!=digest(parent) or type(a)!=int or a<=0 or not 2<=len(p)<=10 or any(type(i)!=int or not 0<=i<10 for i in p) or len(set(p))!=len(p) or seen.intersection(p) or any((j-i)%10 not in (1,9) for i,j in zip(p,p[1:])): raise ValueError('invalid branch')
        if s['x'][p[0]]-a<2 or s['x'][p[-1]]+a>2 or any(s['x'][i]!=2 for i in p[1:-1]) or any(s['b'][i]<a for i in p[:-1]): raise ValueError('capacity')
        s['x'][p[0]]-=a; s['x'][p[-1]]+=a
        for i in p[:-1]: s['b'][i]-=a
        s['spent']+=a*(len(p)-1); seen.update(p); ids.append(digest(q))
    s.update(generation=parent['generation']+1,parent=digest(parent),branches=ids)
    if sum(s['x'])+s['center']!=26 or s['center']!=6 or sum(s['b'])+s['spent']!=540 or min(s['x']+s['b'])<0: raise ValueError('conservation')
    return s

def verify(chain):
    p=genesis()
    for branches,child in chain:
        if advance(p,branches)!=child: raise ValueError('lineage mismatch')
        p=child
    return p

if __name__=='__main__':
    p=genesis(); chain=[]
    for n in range(1,165):
        qs=[proposal(p,[0,1,2])] if n==1 else [proposal(p,[3,4,5])] if n==2 else []
        child=advance(p,qs);chain.append((qs,child));p=child
        if n in (1,2,164): print(n,sum(p['x'])+p['center'],sum(p['b']),p['spent'],digest(p))
    assert verify(chain)==p
    print('PASS: replayed 164 generations; 2 transfers, 162 observation-only checkpoints')
