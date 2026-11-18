import json, hashlib, secrets
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

def enc(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(x): return hashlib.sha256(enc(x)).hexdigest()
def raw(k): return k.public_bytes(Encoding.Raw,PublicFormat.Raw).hex()
def audit(graph, witnesses, trusted):
    def roots(n,seen):
        if n in seen or n not in graph: raise ValueError('ancestry')
        if not graph[n]:
            if n not in trusted: raise ValueError('unknown root')
            return {n}
        if n in trusted: raise ValueError('root has controller')
        return set().union(*(roots(p,seen|{n}) for p in graph[n]))
    sets=[roots(w,set()) for w in witnesses]
    return all(not sets[i]&sets[j] for i in range(3) for j in range(i))

def manifest(mesh,version,graph,keys,authority):
    body=['WAG133-manifest',mesh,version,graph,{n:raw(k) for n,k in keys.items()}]
    return [body,authority.sign(enc(body)).hex()]

def response(mesh,nonce,topology,head,name,key):
    body=['WAG133-response',mesh,nonce,topology,head,name]
    return [body,key.sign(enc(body)).hex()]

class Gate:
    def __init__(self,mesh,authority,keys,trusted,expected_version,expected_hash):
        self.mesh,self.authority,self.keys,self.trusted=mesh,authority,keys,trusted
        self.version,self.expected_hash=expected_version,expected_hash
        self.nonce=secrets.token_hex(32);self.used=False
    def verify(self,m,responses,head):
        if self.used:return 'HOLD_USED'
        self.used=True
        try:
            b,s=m;self.authority.verify(bytes.fromhex(s),enc(b))
            tag,mesh,v,graph,bindings=b
            if tag!='WAG133-manifest' or mesh!=self.mesh:return 'HOLD_SCOPE'
            if v!=self.version or digest(b)!=self.expected_hash:return 'HOLD_STALE_TOPOLOGY'
            if len(self.keys)!=3 or len(set(map(raw,self.keys.values())))!=3 or bindings!={n:raw(k) for n,k in self.keys.items()}:return 'HOLD_MEMBERSHIP'
            if not audit(graph,list(self.keys),self.trusted):return 'HOLD_SHARED_ROOT'
            if set(responses)!=set(self.keys):return 'HOLD_MISSING'
            for n,k in self.keys.items():
                body,sig=responses[n];k.verify(bytes.fromhex(sig),enc(body))
                if body!=['WAG133-response',self.mesh,self.nonce,digest(b),head,n]:return 'HOLD_RESPONSE_SCOPE'
            return 'VERIFIED_DECLARED_TOPOLOGY'
        except (InvalidSignature,ValueError,TypeError,KeyError,AttributeError):return 'HOLD_INVALID'
