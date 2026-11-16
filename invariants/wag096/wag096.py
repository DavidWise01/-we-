"""WAG-096: authenticated transparency-log heads and full-prefix continuity.
Reference implementation; no live off-host trust roots or timestamps.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from cryptography.exceptions import InvalidSignature

def enc(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()

def leaf(data):
    return sha256(b'\x00' + enc(data)).digest()

def parent(a,b):
    return sha256(b'\x01' + a + b).digest()

def root(leaves):
    if not leaves: return sha256(b'').digest()
    nodes=[leaf(x) for x in leaves]
    while len(nodes)>1:
        nodes=[parent(nodes[i],nodes[i+1]) if i+1<len(nodes) else nodes[i]
               for i in range(0,len(nodes),2)]
    return nodes[0]

def path(leaves,index):
    if not 0<=index<len(leaves): raise ValueError('index')
    nodes=[leaf(x) for x in leaves]; result=[]
    while len(nodes)>1:
        if index%2==0 and index+1<len(nodes):
            result.append(('R',nodes[index+1].hex()))
        elif index%2==1:
            result.append(('L',nodes[index-1].hex()))
        nodes=[parent(nodes[i],nodes[i+1]) if i+1<len(nodes) else nodes[i]
               for i in range(0,len(nodes),2)]
        index//=2
    return result

def inclusion(entry,index,size,proof,expected):
    if type(index)!=int or type(size)!=int or size<=0 or index<0 or index>=size:
        return False
    try:
        h=leaf(entry); position=index; width=size; cursor=0
        while width>1:
            has_sibling=(position%2==1 or position+1<width)
            if has_sibling:
                side,digest=proof[cursor]; cursor+=1
                sibling=bytes.fromhex(digest)
                if len(sibling)!=32 or side!=('L' if position%2 else 'R'):
                    return False
                h=parent(sibling,h) if side=='L' else parent(h,sibling)
            position//=2; width=(width+1)//2
        return cursor==len(proof) and h.hex()==expected
    except (ValueError,TypeError,IndexError,AttributeError):
        return False

@dataclass(frozen=True)
class Head:
    log: str
    size: int
    digest: str
    signature: str

def sign_head(key,log,leaves):
    data={'tag':'WAG096-head-v1','log':log,'size':len(leaves),'digest':root(leaves).hex()}
    return Head(log,len(leaves),data['digest'],key.sign(enc(data)).hex())

class Gate:
    def __init__(self,public_keys,ancestry):
        if len(public_keys)!=3 or len(ancestry)!=3 or set(public_keys)!=set(ancestry):
            raise ValueError('three authorities')
        if len(set(ancestry.values()))!=3: raise ValueError('shared declared ancestry')
        self.keys=public_keys; self.ancestry=ancestry
        self.pinned={}; self.evidence=[]; self.forks=[]

    def verify_head(self,head):
        if head.log not in self.keys or type(head.size)!=int or head.size<1:
            return False
        try:
            digest=bytes.fromhex(head.digest); sig=bytes.fromhex(head.signature)
            if len(digest)!=32: return False
            body={'tag':'WAG096-head-v1','log':head.log,'size':head.size,'digest':head.digest}
            self.keys[head.log].verify(sig,enc(body))
            return True
        except (InvalidSignature,ValueError,TypeError,AttributeError):
            return False

    def submit(self,head,entry,index,proof,prefix):
        if not self.verify_head(head): return self._hold('HOLD_INVALID_HEAD',head)
        if not inclusion(entry,index,head.size,proof,head.digest):
            return self._hold('HOLD_INVALID_INCLUSION',head)
        if type(prefix)!=list or len(prefix)!=head.size or root(prefix).hex()!=head.digest or prefix[index]!=entry:
            return self._hold('HOLD_INVALID_PREFIX',head)
        old=self.pinned.get(head.log)
        if old:
            old_head,old_prefix=old
            if head.size<old_head.size: return self._hold('HOLD_ROLLBACK',head)
            if prefix[:old_head.size]!=old_prefix:
                self.forks.append((old_head,head))
                self.evidence.append(('QUARANTINE_FORK',head))
                return 'QUARANTINE_FORK'
        self.pinned[head.log]=(head,list(prefix))
        self.evidence.append(('VERIFIED_LOCAL_PROOF',head))
        return 'VERIFIED_LOCAL_PROOF'

    def _hold(self,reason,head):
        self.evidence.append((reason,head)); return reason

    def checkpoint(self,entry):
        if self.forks: return 'QUARANTINE_FORK'
        if len(self.pinned)<3: return 'HOLD_MISSING_LOG'
        if not all(entry in prefix for _,prefix in self.pinned.values()):
            return 'HOLD_MISSING_ENTRY'
        return 'ELIGIBLE_FOR_EXTERNAL_TIME_AND_CUSTODY_VERIFICATION'
