"""WAG-090: commit/freeze/reveal and unbiased chunk selection reference.

Three *declared* witness identities contribute seeds. A permanently frozen round
never redraws on abort. The seed combiner is deterministic once all reveals exist.
This is a local test model, NOT a bias-resistant real-world coin-tossing protocol:
last revealer can selectively abort after seeing the other reveals.
"""
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def H(x):
    return sha256(canonical(x)).hexdigest()


def commit_digest(round_id, who, secret):
    if not isinstance(secret, bytes) or len(secret) < 16:
        raise ValueError('seed must be at least 16 bytes')
    return sha256(b'WAG090/COMMIT/v1\0' + canonical(round_id) + b'\0' + who.encode() + b'\0' + secret).hexdigest()


@dataclass(frozen=True)
class RoundID:
    epoch: int
    checkpoint_root: str
    challenge: str
    archive_chunks: int
    sample_count: int

    def __post_init__(self):
        if not isinstance(self.epoch, int) or self.epoch < 0:
            raise ValueError('epoch')
        if not all(isinstance(v, str) and v for v in (self.checkpoint_root, self.challenge)):
            raise ValueError('checkpoint/challenge')
        if type(self.archive_chunks) is not int or type(self.sample_count) is not int or not 1 <= self.sample_count <= self.archive_chunks:
            raise ValueError('sample parameters')


class ChallengeRound:
    def __init__(self, rid, witnesses=('W1','W2','W3')):
        if not isinstance(rid, RoundID):
            raise ValueError('round')
        if len(witnesses) != 3 or len(set(witnesses)) != 3 or any(not isinstance(w,str) or not w for w in witnesses):
            raise ValueError('three distinct witnesses required')
        self.rid=rid
        self.witnesses=tuple(witnesses)
        self.commits={}
        self.reveals={}
        self.phase='COMMIT'
        self.events=[]
        self._record('genesis',{'round':vars(rid),'witnesses':self.witnesses})

    def _record(self,kind,data):
        r={'seq':len(self.events),'prev':self.events[-1]['hash'] if self.events else '0'*64,'kind':kind,'data':data}
        r['hash']=H(r)
        self.events.append(r)

    def audit_valid(self):
        return all(r['seq']==i and r['prev']==(self.events[i-1]['hash'] if i else '0'*64)
                   and r['hash']==H({k:v for k,v in r.items() if k!='hash'}) for i,r in enumerate(self.events))

    def commit(self,w,commitment):
        if self.phase!='COMMIT':raise ValueError('commit closed')
        if w not in self.witnesses or w in self.commits:raise ValueError('unauthorized/duplicate witness')
        if not isinstance(commitment,str) or len(commitment)!=64 or any(c not in '0123456789abcdef' for c in commitment):raise ValueError('invalid commitment')
        self.commits[w]=commitment
        self._record('commit',{'witness':w,'digest':commitment})

    def freeze(self):
        if self.phase!='COMMIT' or set(self.commits)!=set(self.witnesses):
            raise ValueError('three commitments required')
        self.phase='REVEAL'
        self._record('freeze',{'commitments':sorted(self.commits.items())})

    def reveal(self,w,secret):
        if self.phase!='REVEAL':raise ValueError('reveals not open')
        if w not in self.commits or w in self.reveals:raise ValueError('unknown/duplicate reveal')
        if commit_digest(vars(self.rid),w,secret)!=self.commits[w]:
            self.phase='HOLD_INVALID_REVEAL'
            self._record('invalid_reveal',{'witness':w})
            return self.phase
        self.reveals[w]=bytes(secret)
        self._record('reveal',{'witness':w,'seed_hash':sha256(secret).hexdigest()})
        return 'REVEAL_ACCEPTED'

    def close_reveals(self):
        if self.phase!='REVEAL':raise ValueError('not in reveal phase')
        missing=sorted(set(self.witnesses)-set(self.reveals))
        if missing:
            self.phase='HOLD_SELECTIVE_ABORT'
            self._record('missing_reveal',{'missing':missing})
            return self.phase
        self.phase='READY'
        self._record('reveal_complete',{'witnesses':sorted(self.witnesses)})
        return 'READY'

    def derive(self):
        if self.phase not in ('READY','DERIVED'):raise ValueError('no valid frozen full reveal')
        # Canonical identity order prevents reveal ordering from changing result.
        blob=b'WAG090/SEED/v1\0'+canonical(vars(self.rid))
        for w in sorted(self.witnesses):
            seed=self.reveals[w]
            blob+=len(w).to_bytes(2,'big')+w.encode()+len(seed).to_bytes(4,'big')+seed
        key=sha256(blob).digest()
        self.phase='DERIVED'
        return unbiased_without_replacement(key,self.rid.archive_chunks,self.rid.sample_count)


def unbiased_without_replacement(key,N,k):
    """SHA-256 counter-mode rejection sampler: no modulo reduction bias."""
    if not isinstance(key,bytes) or len(key)!=32 or not 1<=k<=N:
        raise ValueError('sampler inputs')
    available=list(range(N));result=[];counter=0
    for i in range(k):
        n=len(available)
        limit=(1<<256)//n*n
        while True:
            raw=int.from_bytes(sha256(b'WAG090/SELECT/v1\0'+key+counter.to_bytes(8,'big')).digest(),'big')
            counter+=1
            if raw<limit:break
        j=raw % n
        result.append(available.pop(j))
    return tuple(result)


def example():
    rid=RoundID(90,'root-A','challenge-90',17,3)
    r=ChallengeRound(rid)
    seeds={'W1':b'a'*32,'W2':b'b'*32,'W3':b'c'*32}
    for w in r.witnesses:r.commit(w,commit_digest(vars(rid),w,seeds[w]))
    r.freeze()
    for w in ('W2','W1','W3'):r.reveal(w,seeds[w])
    r.close_reveals()
    indexes=r.derive()
    return {'indices':indexes,'audit_records':len(r.events),'audit_valid':r.audit_valid(),'state':r.phase}

if __name__=='__main__':print(json.dumps(example(),indent=2))
