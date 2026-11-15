"""WAG-055 signed recovery verification reference; mock anchor is NOT external."""
from dataclasses import dataclass
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
import json

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()

def sha(obj):
    return sha256(canonical(obj)).hexdigest()

@dataclass(frozen=True)
class Identity:
    signer: str
    root: str
    domain: str
    public_key_hex: str
    revoked: bool = False

@dataclass(frozen=True)
class Attestation:
    signer: str
    signature_hex: str

class RecoverySeal:
    def __init__(self, identities, original_id='C0', recovered_id='C1', source_roots=('E0','E1','E2'), fallback_root='R'):
        if not original_id or not recovered_id or original_id == recovered_id or not fallback_root or fallback_root in source_roots:
            raise ValueError('invalid recovery lineage')
        self.identities = {x.signer:x for x in identities}
        if len(self.identities) != len(identities):
            raise ValueError('duplicate signer')
        self.original_id, self.recovered_id = original_id, recovered_id
        self.source_roots, self.fallback_root = tuple(source_roots), fallback_root
        self.records=[]; self.state='PENDING'; self.certificate=None
        self._append('genesis', {'original':original_id,'recovery':recovered_id,'sources':self.source_roots,'fallback':fallback_root})

    def _append(self, kind, payload):
        r={'seq':len(self.records),'previous':self.records[-1]['hash'] if self.records else '0'*64,'kind':kind,'payload':payload}
        r['hash']=sha(r);self.records.append(r)

    def verify_ledger(self):
        return all(r['seq']==i and r['previous']==(self.records[i-1]['hash'] if i else '0'*64)
                   and r['hash']==sha({k:v for k,v in r.items() if k!='hash'}) for i,r in enumerate(self.records))

    def payload(self):
        return {'protocol':'WAG-055:v1','original':self.original_id,'recovery':self.recovered_id,
                'sources':self.source_roots,'fallback':self.fallback_root,'outcome':'CLOSED_SUCCESS'}

    def candidate_digest(self):
        return sha(self.payload())

    def certify(self, attestations, *, anchor_receipt=None, anchor_verifier=None):
        if self.state != 'PENDING':
            raise ValueError('checkpoint already decided')
        if len(attestations) != 3 or len({a.signer for a in attestations}) != 3:
            raise ValueError('requires exactly three signers')
        ids=[]
        for a in attestations:
            ident=self.identities.get(a.signer)
            if ident is None or ident.revoked:
                raise ValueError('unknown or revoked signer')
            try:
                Ed25519PublicKey.from_public_bytes(bytes.fromhex(ident.public_key_hex)).verify(bytes.fromhex(a.signature_hex), canonical(self.payload()))
            except (ValueError, InvalidSignature):
                raise ValueError('invalid signature') from None
            ids.append(ident)
        if len({x.root for x in ids})!=3 or len({x.domain for x in ids})!=3:
            raise ValueError('shared witness ancestry or domain')
        if anchor_receipt is None or anchor_verifier is None:
            self._append('hold', {'reason':'NO_VERIFIED_EXTERNAL_ANCHOR','digest':self.candidate_digest()})
            self.state='HOLD'
            return 'HOLD_EXTERNAL_ANCHOR'
        if not anchor_verifier(anchor_receipt, self.candidate_digest()):
            raise ValueError('external anchor verification failed')
        self.certificate={'checkpoint':self.recovered_id,'parent':self.original_id,'digest':self.candidate_digest(),
                          'signers':sorted(a.signer for a in attestations),'anchor_receipt':anchor_receipt}
        self._append('certificate',self.certificate.copy())
        self.state='CERTIFIED'
        return 'CERTIFIED'

def demo():
    """Synthetic signer identities and MOCK verifier; NOT externally anchored."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    keys=[Ed25519PrivateKey.generate() for _ in range(3)]
    identities=[Identity(f'w{i}',f'root{i}',f'domain{i}',k.public_key().public_bytes(
        serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()) for i,k in enumerate(keys)]
    auditor=RecoverySeal(identities)
    proof=[Attestation(f'w{i}',k.sign(canonical(auditor.payload())).hex()) for i,k in enumerate(keys)]
    mock_receipt={'service':'MOCK-NOT-EXTERNAL','digest':auditor.candidate_digest(),'id':'fixture'}
    verdict=auditor.certify(proof,anchor_receipt=mock_receipt,
                             anchor_verifier=lambda r,d:r.get('service')=='MOCK-NOT-EXTERNAL' and r.get('digest')==d)
    return auditor,verdict

if __name__=='__main__':
    a,v=demo();print(json.dumps({'synthetic_verdict':v,'externally_anchored':False,'records':len(a.records),'ledger_verified':a.verify_ledger()},indent=2))
