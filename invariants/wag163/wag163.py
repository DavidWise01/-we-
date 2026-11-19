import hashlib,json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def h(x):return hashlib.sha256(enc(x)).hexdigest()
G={'x':[3,2,1,3,2,1,2,2,2,2],'b':[54]*10,'center':6,'spent':0}

def branch(path):
    return {'parent':h(G),'path':list(path),'amount':1}

def join(branches):
    s=json.loads(enc(G)); seen=set(); ids=[]
    for q in sorted(branches,key=h):
        p=q['path']; a=q['amount']
        if q['parent']!=h(G) or type(a)!=int or a<=0 or not 2<=len(p)<=10 or len(set(p))!=len(p) or any(type(i)!=int or not 0<=i<10 for i in p) or any((j-i)%10 not in (1,9) for i,j in zip(p,p[1:])) or seen.intersection(p):raise ValueError('conflict or invalid path')
        if s['x'][p[0]]-a<2 or s['x'][p[-1]]+a>2 or any(s['x'][i]!=2 for i in p[1:-1]) or any(s['b'][i]<a for i in p[:-1]):raise ValueError('capacity')
        s['x'][p[0]]-=a;s['x'][p[-1]]+=a
        for i in p[:-1]:s['b'][i]-=a
        s['spent']+=a*(len(p)-1);seen.update(p);ids.append(h(q))
    assert sum(s['x'])+s['center']==26 and sum(s['b'])+s['spent']==540
    return {'parent':h(G),'branches':ids,'state':s}

def certify(branches,registry,observations):
    target=join(branches); roots=set(); keys=set()
    for name,checkpoint,sig in observations:
        root,key=registry[name]; raw=key.public_bytes_raw()
        if checkpoint!=h(target) or root in roots or raw in keys:raise ValueError('observation or ancestry')
        key.verify(sig,enc(['WAG163',name,root,checkpoint]));roots.add(root);keys.add(raw)
    if len(roots)!=3:raise ValueError('three distinct registered roots required')
    return target
