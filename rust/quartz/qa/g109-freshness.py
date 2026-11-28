"""Nonce-bound three-custodian confirmation; no authority. .dlw"""
import hashlib,json,secrets,re
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def h(x): return isinstance(x,str) and re.fullmatch('[0-9a-f]{64}',x) is not None and x!='0'*64
def digest(x): return hashlib.sha256(b'G109-roster\0'+canonical(x)).hexdigest()
def message(nonce,ledger,root,ref): return b'G109\0'+canonical([nonce,ledger,root,ref])
class Challenge:
    def __init__(self,ledger,roster,pin,minimum=0):
        if not h(ledger) or not isinstance(roster,dict) or len(roster)!=3 or not all(h(k) and h(v) for k,v in roster.items()) or len(set(roster.values()))!=3 or digest(roster)!=pin or type(minimum)is not int or not 0<=minimum<=256: raise ValueError('configuration')
        self.ledger=ledger; self.roster=dict(roster);self.minimum=minimum;self.nonce=secrets.token_hex(32);self.used=False
    def verify(self,responses):
        def out(state):return {'state':state,'authority':'HOLD','independence_verified':False}
        if self.used:return out('REPLAY')
        self.used=True
        if not isinstance(responses,list) or len(responses)!=3:return out('MISSING_OR_EXTRA')
        seen=set();refs=[]
        try:
            for r in responses:
                if set(r)!={'root','nonce','reference','signature'}:return out('INVALID')
                root=r['root'];ref=r['reference']
                if root not in self.roster or root in seen:return out('ROSTER_MISMATCH')
                if r['nonce']!=self.nonce:return out('NONCE_MISMATCH')
                if set(ref)!={'ledger','count','head','evidence'} or ref['ledger']!=self.ledger or type(ref['count'])is not int or not 0<=ref['count']<=256:return out('REFERENCE_INVALID')
                if ref['count']==0:
                    if ref['head']!='0'*64 or ref['evidence']!='0'*64:return out('REFERENCE_INVALID')
                elif not h(ref['head']) or not h(ref['evidence']):return out('REFERENCE_INVALID')
                Ed25519PublicKey.from_public_bytes(bytes.fromhex(self.roster[root])).verify(bytes.fromhex(r['signature']),message(self.nonce,self.ledger,root,ref))
                seen.add(root);refs.append(ref)
        except (ValueError,TypeError,KeyError,InvalidSignature):return out('SIGNATURE_OR_SCHEMA_INVALID')
        if any(x!=refs[0] for x in refs):return out('CONFLICT')
        if refs[0]['count']<self.minimum:return out('STALE_COUNT')
        return dict(out('FRESH_SIGNED_DECLARATIONS'),reference=dict(refs[0]))
