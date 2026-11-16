"""WAG-079: compact, range-frontier Merkle prefix proofs with signed witnesses.

Domain-separated hashing uses the RFC6962 leaf/internal node tags (0x00/0x01),
but this is a reference range-frontier consistency proof, not an RFC6962 wire proof.
The proof carries O(log n) subtree digests and no historical leaf bodies.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def leaf_hash(payload: bytes) -> bytes:
    return sha256(b'\x00' + payload).digest()


def node_hash(left: bytes, right: bytes) -> bytes:
    return sha256(b'\x01' + left + right).digest()


def _largest_power_less_than(n: int) -> int:
    return 1 << ((n - 1).bit_length() - 1)


def merkle_root(leaves: tuple[bytes, ...] | list[bytes]) -> bytes:
    """RFC6962-style tree root over leaf bodies, nonempty tree only."""
    n = len(leaves)
    if not n:
        return sha256(b'').digest()
    if n == 1:
        return leaf_hash(leaves[0])
    k = _largest_power_less_than(n)
    return node_hash(merkle_root(leaves[:k]), merkle_root(leaves[k:]))


def _range_root(leaves: tuple[bytes, ...], start: int, length: int) -> bytes:
    return merkle_root(leaves[start:start + length])


def _cover(start: int, end: int):
    """Minimal aligned dyadic cover of [start,end)."""
    if not (0 <= start <= end):
        raise ValueError('invalid interval')
    blocks = []
    cursor = start
    while cursor < end:
        remaining = end - cursor
        size = 1 << (remaining.bit_length() - 1)
        if cursor:
            size = min(size, cursor & -cursor)
        blocks.append((cursor, size))
        cursor += size
    return tuple(blocks)


@dataclass(frozen=True)
class Block:
    start: int
    length: int
    hash_hex: str


@dataclass(frozen=True)
class ConsistencyProof:
    old_size: int
    new_size: int
    old_blocks: tuple[Block, ...]
    appended_blocks: tuple[Block, ...]


def create_proof(leaves: tuple[bytes, ...], old_size: int) -> ConsistencyProof:
    if not isinstance(old_size, int) or not (1 <= old_size <= len(leaves)):
        raise ValueError('old size must be a nonempty prefix')
    if len(leaves) > 1000000:
        raise ValueError('too many leaves')
    def build(ranges):
        return tuple(Block(s, n, _range_root(leaves, s, n).hex()) for s, n in ranges)
    return ConsistencyProof(old_size, len(leaves), build(_cover(0,old_size)), build(_cover(old_size,len(leaves))))


def _parse_hex(h: str) -> bytes:
    if not isinstance(h, str) or len(h) != 64:
        raise ValueError('not a SHA-256 hex digest')
    raw = bytes.fromhex(h)
    if len(raw) != 32:
        raise ValueError('invalid digest')
    return raw


def _reconstruct(blocks: tuple[Block, ...]) -> bytes:
    """Reconstruct RFC6962 root from canonical ordered aligned subtrees."""
    if not blocks:
        return sha256(b'').digest()
    stack = []
    for b in blocks:
        stack.append((b.start, b.length, _parse_hex(b.hash_hex)))
        while len(stack) >= 2:
            ls, ln, lh = stack[-2]
            rs, rn, rh = stack[-1]
            if ln != rn or ls + ln != rs or ls % (2*ln) != 0:
                break
            stack[-2:] = [(ls, 2*ln, node_hash(lh,rh))]
    result = stack[-1][2]
    for _, _, h in reversed(stack[:-1]):
        result = node_hash(h,result)
    return result


def verify_proof(proof: ConsistencyProof, old_root: str, new_root: str) -> bool:
    if not isinstance(proof, ConsistencyProof):
        return False
    try:
        m, n = proof.old_size, proof.new_size
        if not isinstance(m,int) or not isinstance(n,int) or not (1 <= m <= n <= 1000000):
            return False
        if tuple((b.start,b.length) for b in proof.old_blocks) != _cover(0,m):
            return False
        if tuple((b.start,b.length) for b in proof.appended_blocks) != _cover(m,n):
            return False
        old = _reconstruct(proof.old_blocks)
        full = _reconstruct(proof.old_blocks + proof.appended_blocks)
        return old == _parse_hex(old_root) and full == _parse_hex(new_root)
    except (ValueError,TypeError,AttributeError,OverflowError):
        return False


@dataclass(frozen=True)
class Observer:
    identity: str
    ancestor: str
    operator: str
    domain: str
    public_key: bytes


@dataclass(frozen=True)
class Vote:
    identity: str
    old_size: int
    new_size: int
    old_root: str
    new_root: str
    epoch: int
    challenge: str
    signature: bytes


def vote_message(vote: Vote) -> bytes:
    body = {k:getattr(vote,k) for k in ('identity','old_size','new_size','old_root','new_root','epoch','challenge')}
    return b'WAG-079.consistency.vote.v1\x00' + json.dumps(body,sort_keys=True,separators=(',',':')).encode()


def sign_vote(identity: str, private: Ed25519PrivateKey, proof: ConsistencyProof, old_root: str, new_root: str, epoch: int, challenge: str) -> Vote:
    unsigned = Vote(identity,proof.old_size,proof.new_size,old_root,new_root,epoch,challenge,b'')
    return Vote(identity,proof.old_size,proof.new_size,old_root,new_root,epoch,challenge,private.sign(vote_message(unsigned)))


class PrefixGate:
    """Local testing gate; distinct declared ancestries are not external proof."""
    def __init__(self, observers: tuple[Observer, ...], frozen_size:int, frozen_root:str, epoch:int, challenge:str):
        if len(observers)!=3:
            raise ValueError('three observers required')
        for field in ('identity','ancestor','operator','domain','public_key'):
            vals=[getattr(o,field) for o in observers]
            if any(not v for v in vals) or len(set(vals)) != 3:
                raise ValueError('duplicate or missing observer provenance')
        if frozen_size < 1 or epoch < 0 or not challenge:
            raise ValueError('bad checkpoint')
        _parse_hex(frozen_root)
        self.observers={o.identity:o for o in observers}
        self.frozen_size=frozen_size
        self.frozen_root=frozen_root
        self.epoch=epoch
        self.challenge=challenge
        self.entries=[]
        self._log('freeze',{'old_size':frozen_size,'old_root':frozen_root,'epoch':epoch,'challenge':challenge})

    def _log(self, kind, info):
        record={'seq':len(self.entries),'previous':self.entries[-1]['hash'] if self.entries else '0'*64,'kind':kind,'data':info}
        record['hash']=digest(record)
        self.entries.append(record)

    def ledger_valid(self):
        return all(e['seq']==i and e['previous']==(self.entries[i-1]['hash'] if i else '0'*64) and e['hash']==digest({k:v for k,v in e.items() if k!='hash'}) for i,e in enumerate(self.entries))

    def certify(self, proof:ConsistencyProof, new_root:str, votes:tuple[Vote,...]):
        decision='HOLD'
        why=''
        if not isinstance(proof,ConsistencyProof) or proof.old_size!=self.frozen_size or not verify_proof(proof,self.frozen_root,new_root):
            decision,why='QUARANTINE_PREFIX','prefix proof failed'
        elif len(votes)!=3 or {v.identity for v in votes}!=set(self.observers):
            decision,why='HOLD_QUORUM','missing/duplicate observer'
        else:
            expected=(self.frozen_size,proof.new_size,self.frozen_root,new_root,self.epoch,self.challenge)
            for v in votes:
                if (v.old_size,v.new_size,v.old_root,v.new_root,v.epoch,v.challenge)!=expected:
                    decision,why='HOLD_STALE_OR_SPLIT','vote scope mismatch';break
                try:
                    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
                    Ed25519PublicKey.from_public_bytes(self.observers[v.identity].public_key).verify(v.signature,vote_message(v))
                except (InvalidSignature,ValueError,TypeError):
                    decision,why='HOLD_BAD_SIGNATURE','invalid signature';break
            else:
                decision,why='LOCAL_PREFIX_CERTIFIED','three valid matching synthetic votes'
        self._log('decision',{'decision':decision,'reason':why,'new_root':new_root,'votes':[v.identity for v in votes]})
        return decision


def demo():
    from cryptography.hazmat.primitives import serialization
    leaves=tuple(s.encode() for s in 'ABCDE')
    m=3
    old=merkle_root(leaves[:m]).hex();new=merkle_root(leaves).hex()
    proof=create_proof(leaves,m)
    priv=[Ed25519PrivateKey.generate() for _ in range(3)]
    obs=tuple(Observer('W'+str(i+1),'root'+str(i+1),'op'+str(i+1),'domain'+str(i+1),p.public_key().public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)) for i,p in enumerate(priv))
    gate=PrefixGate(obs,m,old,7,'challenge-079')
    votes=tuple(sign_vote(o.identity,p,proof,old,new,7,'challenge-079') for o,p in zip(obs,priv))
    accepted=gate.certify(proof,new,votes)
    tampered=tuple(b'X' if i==1 else x for i,x in enumerate(leaves))
    fake=create_proof(tampered,m)
    quarantined=gate.certify(fake,merkle_root(tampered).hex(),votes)
    return {'old_size':m,'new_size':len(leaves),'old_root':old,'new_root':new,'old_blocks':len(proof.old_blocks),'new_blocks':len(proof.appended_blocks),'accepted':accepted,'rewritten':quarantined,'ledger_records':len(gate.entries),'ledger_valid':gate.ledger_valid()}

if __name__ == '__main__':
    print(json.dumps(demo(),indent=2))