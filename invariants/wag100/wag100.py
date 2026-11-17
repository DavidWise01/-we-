"""Synthetic three-observer chronology gate. Slots are not trusted wall time."""
import json, hashlib
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

def enc(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def signed(key,body): return {'body':body,'sig':key.sign(enc(body)).hex()}
def digest(x): return hashlib.sha256(enc(x)).hexdigest()
def valid(key,p):
    try: key.verify(bytes.fromhex(p['sig']),enc(p['body'])); return True
    except (InvalidSignature,ValueError,TypeError,KeyError): return False

class Gate:
    def __init__(self,keys,roots,authority,witness,pin):
        if len(keys)!=3 or set(keys)!=set(roots) or len(set(roots.values()))!=3: raise ValueError('ancestry')
        fingerprints=[k.public_bytes(Encoding.Raw,PublicFormat.Raw) for k in [*keys.values(),authority,witness]]
        if len(set(fingerprints))!=5: raise ValueError('shared key')
        self.keys=keys; self.authority=authority; self.witness=witness; self.pin=pin
    def evaluate(self,observation,revocation,views):
        if not valid(self.witness,observation) or not valid(self.authority,revocation): return 'HOLD_SIGNATURE'
        r=revocation['body']; o=observation['body']
        if r.get('tag')!='revoke' or o.get('tag')!='observation' or r.get('key')!=o.get('key') or r.get('key')!='W1': return 'HOLD_SCOPE'
        if len(views)!=3 or set(views)!=set(self.keys): return 'HOLD_MISSING'
        for name,p in views.items():
            if not valid(self.keys[name],p): return 'HOLD_SIGNATURE'
            b=p['body']
            if b.get('tag')!='chronology' or b.get('observer')!=name or b.get('pin')!=self.pin or b.get('obs')!=digest(observation) or b.get('rev')!=digest(revocation): return 'HOLD_BINDING'
            if any(type(b.get(k))!=int or b[k]<0 for k in ('seen','cutoff','head')): return 'HOLD_SCOPE'
            if b['head']<max(b['seen'],b['cutoff']): return 'HOLD_STALE'
        positions={(p['body']['seen'],p['body']['cutoff']) for p in views.values()}
        if len(positions)!=1: return 'HOLD_DISAGREEMENT'
        seen,cutoff=positions.pop()
        if type(r.get('effective'))!=int or cutoff!=r['effective']: return 'HOLD_BINDING'
        return 'LOCAL_HISTORICAL_ELIGIBLE' if seen<cutoff else 'HOLD_REVOKED'
