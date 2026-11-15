"""WAG-049: reference entropy commitments, cutoff, reveal, and balanced assignment.

This does NOT authenticate entropy sources or establish real-world secrecy.
"""
from dataclasses import dataclass
from hashlib import sha256
from hmac import new as hmac_new
from collections import Counter
import json

def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def commitment(source,secret_hex,protocol_hash):
    return digest({'tag':'WAG049:entropy:v1','source':source,
                   'secret':secret_hex,'protocol':protocol_hash})

@dataclass(frozen=True)
class Protocol:
    subjects: tuple
    treatment_count: int
    cutoff_tick: int
    entropy_source_ids: tuple
    witness_roots: tuple

class Ceremony:
    def __init__(self,protocol):
        if not isinstance(protocol,Protocol) or len(protocol.subjects)<4 or len(set(protocol.subjects))!=len(protocol.subjects) or not all(protocol.subjects) or not 0<protocol.treatment_count<len(protocol.subjects):
            raise ValueError('subjects/allocation')
        if type(protocol.cutoff_tick)!=int or protocol.cutoff_tick<1 or len(protocol.entropy_source_ids)<3 or len(set(protocol.entropy_source_ids))!=len(protocol.entropy_source_ids) or len(protocol.witness_roots)<3 or len(set(protocol.witness_roots))!=len(protocol.witness_roots):
            raise ValueError('cutoff/source/witness')
        self.protocol=protocol;self.protocol_hash=digest(vars(protocol))
        self.commits={};self.reveals={};self.cutoff=False;self.audit_witnesses=set()
        self.allocation=None;self.ledger=[]
        self._append('protocol',{'hash':self.protocol_hash,'protocol':vars(protocol)})
    def _append(self,kind,payload):
        rec={'seq':len(self.ledger),'previous':self.ledger[-1]['hash'] if self.ledger else '0'*64,'kind':kind,'payload':payload}
        rec['hash']=digest(rec);self.ledger.append(rec)
    def verify(self):
        return all(r['seq']==i and r['previous']==(self.ledger[i-1]['hash'] if i else '0'*64) and r['hash']==digest({k:v for k,v in r.items() if k!='hash'}) for i,r in enumerate(self.ledger))
    def commit(self,source,commit_hash,tick):
        if self.cutoff or source not in self.protocol.entropy_source_ids or source in self.commits or type(tick)!=int or not 0<=tick<self.protocol.cutoff_tick or not isinstance(commit_hash,str) or len(commit_hash)!=64 or any(c not in '0123456789abcdef' for c in commit_hash):
            raise ValueError('commit')
        self.commits[source]=commit_hash
        self._append('commit',{'source':source,'hash':commit_hash,'tick':tick})
    def seal_cutoff(self,tick,witness_roots):
        roots=tuple(witness_roots)
        if self.cutoff or type(tick)!=int or tick!=self.protocol.cutoff_tick or set(self.commits)!=set(self.protocol.entropy_source_ids) or len(roots)<3 or len(set(roots))!=len(roots) or not set(roots).issubset(self.protocol.witness_roots):
            raise ValueError('cutoff')
        self.cutoff=True;self.audit_witnesses=set(roots)
        self._append('cutoff',{'tick':tick,'commitments':sorted(self.commits.items()),'roots':sorted(roots)})
    def reveal(self,source,secret_hex,tick):
        if not self.cutoff or self.allocation is not None or source not in self.commits or source in self.reveals or type(tick)!=int or tick<=self.protocol.cutoff_tick or not isinstance(secret_hex,str) or len(secret_hex)!=64 or any(c not in '0123456789abcdef' for c in secret_hex) or commitment(source,secret_hex,self.protocol_hash)!=self.commits[source]:
            raise ValueError('reveal')
        self.reveals[source]=secret_hex
        self._append('reveal',{'source':source,'tick':tick,'secret':secret_hex})
    def finalize(self,tick,concealment_attested,witnesses):
        roots=tuple(witnesses)
        if not self.cutoff or self.allocation is not None or set(self.reveals)!=set(self.protocol.entropy_source_ids) or type(tick)!=int or tick<=self.protocol.cutoff_tick or concealment_attested is not True or len(roots)<3 or len(set(roots))!=len(roots) or not set(roots).issubset(self.audit_witnesses):
            raise ValueError('finalize')
        seed=sha256(b'WAG049:combined:v1\0'+bytes.fromhex(self.protocol_hash)+b''.join(bytes.fromhex(self.reveals[s]) for s in sorted(self.reveals))).digest()
        scores=sorted((hmac_new(seed,('WAG049:allocation:v1:'+s).encode(),'sha256').digest(),s) for s in self.protocol.subjects)
        treated={s for _,s in scores[:self.protocol.treatment_count]}
        self.allocation={s:('intervention' if s in treated else 'control') for s in self.protocol.subjects}
        result={'assignment_hash':digest(sorted(self.allocation.items())),'counts':dict(Counter(self.allocation.values())),'witnesses':sorted(roots),'tick':tick,'status':'REPRODUCED_FROM_REVEALS_NOT_ENTROPY_CERTIFIED'}
        self._append('allocation',result)
        return result

def demonstration():
    p=Protocol(tuple(f'S{i:02d}' for i in range(48)),24,10,('physical','beacon','astronomical'),('ff','cf','rr'))
    c=Ceremony(p)
    secrets={s:sha256(('SYNTHETIC-ONLY:'+s).encode()).hexdigest() for s in p.entropy_source_ids}
    for s in p.entropy_source_ids:c.commit(s,commitment(s,secrets[s],c.protocol_hash),2)
    c.seal_cutoff(10,('ff','cf','rr'))
    for s in p.entropy_source_ids:c.reveal(s,secrets[s],11)
    return c,c.finalize(12,True,('ff','cf','rr'))

if __name__=='__main__':
    c,result=demonstration()
    print(json.dumps({'result':result,'ledger_records':len(c.ledger),'ledger_valid':c.verify()},indent=2))
