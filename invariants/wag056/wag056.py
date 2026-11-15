"""WAG-056: signed anchors, inclusion proofs, and time-scoped trust.

Synthetic reference only; public anchoring and external authentication absent.
"""
from dataclasses import dataclass
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
import json

def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def H(data): return sha256(data).digest()
def leaf_hash(cert_hash):return H(b'WAG056-leaf\0'+bytes.fromhex(cert_hash))
def node_hash(left,right):return H(b'WAG056-node\0'+left+right)
def inclusion_root(cert_hash,steps):
    root=leaf_hash(cert_hash)
    for direction,sibling in steps:
        if direction not in ('L','R') or len(sibling)!=64:raise ValueError('invalid proof')
        s=bytes.fromhex(sibling)
        root=node_hash(s,root) if direction=='L' else node_hash(root,s)
    return root.hex()
def receipt_message(anchor_id,cert_hash,merkle_root,epoch):
    return canon({'domain':'WAG056:anchor:v1','anchor':anchor_id,'certificate':cert_hash,'root':merkle_root,'epoch':epoch})

@dataclass(frozen=True)
class Anchor:
    name:str
    operator:str
    failure_domain:str
    public_key_hex:str
    root_hex:str
    signature_hex:str
    epoch:int
    proof:tuple=()

class CheckpointAudit:
    def __init__(self,certificate,signer,min_anchors=3):
        if not isinstance(certificate,dict) or not signer or type(min_anchors)!=int or min_anchors<2:raise ValueError('invalid policy')
        self.certificate=json.loads(json.dumps(certificate,sort_keys=True))
        self.cert_hash=sha256(canon(self.certificate)).hexdigest()
        self.signer=signer;self.min_anchors=min_anchors
        self.anchors={};self.revocations={};self.events=[];self.issued=False
        self._append('genesis',{'certificate_hash':self.cert_hash,'signer':signer})
    def _append(self,kind,data):
        e={'seq':len(self.events),'prev':self.events[-1]['hash'] if self.events else '0'*64,'kind':kind,'data':data}
        e['hash']=sha256(canon(e)).hexdigest();self.events.append(e)
    def verify_chain(self):
        return all(r['seq']==i and r['prev']==(self.events[i-1]['hash'] if i else '0'*64)
            and r['hash']==sha256(canon({k:v for k,v in r.items() if k!='hash'})).hexdigest()
            for i,r in enumerate(self.events))
    def anchor(self,a):
        if not isinstance(a,Anchor) or not a.name or not a.operator or not a.failure_domain or not isinstance(a.epoch,int) or a.epoch<0 or a.name in self.anchors or self.issued:raise ValueError('invalid anchor')
        if any(a.operator==x.operator or a.failure_domain==x.failure_domain for x in self.anchors.values()):raise ValueError('declared shared domain')
        if inclusion_root(self.cert_hash,a.proof)!=a.root_hex:raise ValueError('invalid inclusion proof')
        try:
            pub=Ed25519PublicKey.from_public_bytes(bytes.fromhex(a.public_key_hex))
            pub.verify(bytes.fromhex(a.signature_hex),receipt_message(a.name,self.cert_hash,a.root_hex,a.epoch))
        except (ValueError,InvalidSignature):
            raise ValueError('invalid receipt signature')
        self.anchors[a.name]=a
        self._append('anchor',{'anchor':a.name,'operator':a.operator,'failure_domain':a.failure_domain,'root':a.root_hex,'epoch':a.epoch,'signature':a.signature_hex})
    def issue(self):
        if self.issued or len(self.anchors)<self.min_anchors:raise ValueError('insufficient anchors')
        self.issued=True;self._append('issue',{'certificate_hash':self.cert_hash,'anchor_ids':sorted(self.anchors)})
    def revoke(self,identity,epoch,reason):
        if not self.issued or not identity or not reason or not isinstance(epoch,int) or epoch<0 or identity in self.revocations:raise ValueError('invalid revocation')
        if identity!=self.signer and identity not in self.anchors:raise ValueError('unknown signer')
        if identity in self.anchors and epoch<self.anchors[identity].epoch:raise ValueError('revocation predates anchor')
        self.revocations[identity]={'epoch':epoch,'reason':reason}
        self._append('revoke',{'identity':identity,'epoch':epoch,'reason':reason})
    def trust(self,epoch):
        if not isinstance(epoch,int) or epoch<0:raise ValueError('invalid epoch')
        if not self.issued:return {'historical':'NOT_ISSUED','current':'HOLD','active_anchors':0}
        active=sum(a.epoch<=epoch and (a.name not in self.revocations or self.revocations[a.name]['epoch']>epoch) for a in self.anchors.values())
        revoked=self.signer in self.revocations and self.revocations[self.signer]['epoch']<=epoch
        state='HOLD_REVOKED_SIGNER' if revoked else ('CURRENT' if active>=self.min_anchors else 'HOLD_ANCHOR_QUORUM')
        return {'historical':'SEALED_AT_ISSUANCE','current':state,'active_anchors':active}
def demonstration():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    a=CheckpointAudit({'checkpoint':'C1','parent':'C0','state':'CLOSED_SUCCESS'},'S2')
    for i in range(3):
        key=Ed25519PrivateKey.generate();name=f'A{i+1}';root=inclusion_root(a.cert_hash,())
        sig=key.sign(receipt_message(name,a.cert_hash,root,10)).hex()
        pub=key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()
        a.anchor(Anchor(name,f'operator{i}',f'domain{i}',pub,root,sig,10))
    a.issue();before=a.trust(11);a.revoke('S2',12,'synthetic compromise')
    return a,before,a.trust(13)
if __name__=='__main__':
    a,b,c=demonstration()
    print(json.dumps({'before':b,'after':c,'records':len(a.events),'verified':a.verify_chain()},indent=2))
