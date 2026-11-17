"""WAG-101: signed complete control-graph snapshot and succession gate.
Synthetic trusted external authority; not proof of real-world control independence.
"""
import json, hashlib
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(x): return hashlib.sha256(canon(x)).hexdigest()
def valid(key,p,s):
    try: Ed25519PublicKey.from_public_bytes(key).verify(s,canon(p)); return True
    except (ValueError,TypeError,InvalidSignature): return False
@dataclass(frozen=True)
class Actor:
    name:str
    key:bytes
    controller:str

def closure(graph,node):
    seen=set(); active=set()
    def walk(n):
        if n in active: raise ValueError('cycle')
        if n in seen:return
        if n not in graph:raise ValueError('unknown ancestor')
        active.add(n)
        for p in graph[n]:walk(p)
        active.remove(n);seen.add(n)
    walk(node);return seen

class Gate:
    def __init__(self,actors,epoch,root,nonce):
        self.actors={a.name:a for a in actors};self.epoch=epoch;self.root=root;self.nonce=nonce
        if set(self.actors)!=set(('W1','W2','W3','W4','E')) or len({a.key for a in actors})!=5:raise ValueError('roster/key collision')
        self.records=[];self.used=False
    def proposal(self):return {'type':'WAG101/rotation','epoch':self.epoch,'root':self.root,'nonce':self.nonce,'old':'W1','new':'W4','keys':{n:a.key.hex() for n,a in self.actors.items()},'controllers':{n:a.controller for n,a in self.actors.items()}}
    def snapshot(self,graph):return {'type':'WAG101/control','proposal':digest(self.proposal()),'graph':graph,'complete':True}
    def approval(self,snapshot):return {'type':'WAG101/approve','proposal':digest(self.proposal()),'snapshot':digest(snapshot)}
    def log(self,status,snapshot,signature,reviews):
        p={'seq':len(self.records),'previous':self.records[-1]['hash'] if self.records else '0'*64,'status':status,'snapshot':snapshot,'signature':signature.hex(),'reviews':{n:s.hex() for n,s in reviews.items()}}
        p['hash']=digest(p);self.records.append(p);return status
    def evaluate(self,snapshot,signature,reviews):
        # Freeze caller-owned values before evaluating or retaining them.
        snapshot=json.loads(canon(snapshot)); reviews=dict(reviews)
        def finish(s):return self.log(s,snapshot,signature,reviews)
        if self.used:return finish('HOLD_CONSUMED')
        if not valid(self.actors['E'].key,snapshot,signature):return finish('HOLD_EXTERNAL_SIGNATURE')
        if snapshot.get('proposal')!=digest(self.proposal()) or snapshot.get('type')!='WAG101/control' or snapshot.get('complete') is not True:return finish('HOLD_SCOPE')
        graph=snapshot.get('graph')
        try:
            if not isinstance(graph,dict) or any(not isinstance(v,list) or any(not isinstance(p,str) for p in v) for v in graph.values()):raise ValueError('graph')
            for n in graph:closure(graph,n)
            paths={n:closure(graph,a.controller) for n,a in self.actors.items()}
        except (ValueError,TypeError):return finish('HOLD_UNKNOWN_ANCESTRY')
        # Conservative rule: any common control ancestor blocks succession.
        from itertools import combinations
        if any(paths[a]&paths[b] for a,b in combinations(paths,2)):return finish('HOLD_SHARED_CONTROL')
        if set(reviews)!={'W2','W3'} or not all(valid(self.actors[n].key,self.approval(snapshot),s) for n,s in reviews.items()):return finish('HOLD_REVIEWS')
        self.used=True
        return finish('LOCAL_ROTATION_ELIGIBLE')
    def verify_audit(self):
        return all(r['seq']==i and r['previous']==(self.records[i-1]['hash'] if i else '0'*64) and r['hash']==digest({k:v for k,v in r.items() if k!='hash'}) for i,r in enumerate(self.records))