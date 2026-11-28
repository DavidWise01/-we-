"""G113 pinned signed capacity constitution; no authority promotion. .dlw"""
import hashlib,json,re
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def message(policy):
    return b'G113\0'+json.dumps(policy,sort_keys=True,separators=(',',':')).encode()
def fingerprint(policy,sig):
    return hashlib.sha256(message(policy)+sig).hexdigest()
def verify(policy,sig,key,pin,ledger,minimum):
    if type(policy) is not dict or set(policy)!={'ledger','generation','bytes','files'}: raise ValueError('schema')
    if not isinstance(ledger,str) or not re.fullmatch('[0-9a-f]{64}',ledger) or ledger=='0'*64 or policy['ledger']!=ledger: raise ValueError('ledger')
    if type(minimum) is not int or not 0<=minimum<2**64: raise ValueError('minimum')
    for k,lo,hi in [('generation',minimum,2**64-1),('bytes',0,2**63-1),('files',1,2**32-1)]:
        if type(policy[k]) is not int or not lo<=policy[k]<=hi: raise ValueError(k)
    if type(sig) is not bytes or len(sig)!=64 or type(key) is not bytes or len(key)!=32: raise ValueError('signature/key')
    if fingerprint(policy,sig)!=pin: raise ValueError('pin')
    Ed25519PublicKey.from_public_bytes(key).verify(sig,message(policy))
    return dict(policy,authority='HOLD')
