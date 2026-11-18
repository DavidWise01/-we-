import json, hashlib
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.exceptions import InvalidSignature

def enc(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def root(x): return hashlib.sha256(enc(x)).hexdigest()
def membership(keys):
    return len(keys)==3 and len({k.public_bytes(Encoding.Raw,PublicFormat.Raw) for k in keys.values()})==3

def issue(mesh, events, signers, replay):
    if not membership({n:k.public_key() for n,k in signers.items()}): raise ValueError('membership')
    state=replay(events)
    body=['WAG130',mesh,len(events),root(events),root(state)]
    return [body,{n:k.sign(enc(body)).hex() for n,k in signers.items()}]

def check(mesh,events,keys,bound,replay):
    if bound is None:return 'HOLD_MISSING'
    try:
        body,cert=bound;tag,scope,g,h,s=body
        if not membership(keys) or set(cert)!=set(keys) or (tag,scope)!=('WAG130',mesh) or type(g)!=int or g<0:raise ValueError('scope')
        for n,k in keys.items():k.verify(bytes.fromhex(cert[n]),enc(body))
    except (ValueError,TypeError,KeyError,InvalidSignature):return 'HOLD_INVALID_BOUND'
    try:
        replay(events)
        if len(events)<g:return 'HOLD_TRUNCATED'
        if root(events[:g])!=h or root(replay(events[:g]))!=s:return 'HOLD_FORK'
    except (ValueError,TypeError,KeyError,InvalidSignature):return 'HOLD_INVALID_HISTORY'
    return 'COMPLETE_THROUGH_BOUND'
