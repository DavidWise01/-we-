"""WAG-020 deterministic append-only fork reconciliation (single-writer reference)."""
from dataclasses import dataclass
from hashlib import sha256
import json

def digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

@dataclass(frozen=True)
class Packet:
    event: str
    scope: str
    observation: str
    root: str
    packet_id: str

class ForkLedger:
    def __init__(self):
        self.records=[]
        self.nodes={}
        self.packet_ids=set()
        self.head=self._commit('genesis',(),{'label':'C0'})

    def _commit(self,kind,parents,payload):
        data={'kind':kind,'parents':list(parents),'payload':payload}
        node=digest(data)
        if node in self.nodes: raise ValueError('duplicate node')
        record={'seq':len(self.records),'prev':self.records[-1]['chain'] if self.records else '0'*64,'node':node,'data':data}
        record['chain']=digest({k:record[k] for k in ('seq','prev','node','data')})
        self.records.append(record)
        self.nodes[node]=data
        return node

    def branch(self,parent,packet:Packet,author:str):
        if parent not in self.nodes: raise ValueError('unknown parent')
        if not all((packet.event,packet.scope,packet.observation,packet.root,packet.packet_id,author)):
            raise ValueError('empty field')
        if packet.packet_id in self.packet_ids: raise ValueError('replayed packet')
        node=self._commit('branch',(parent,),{'author':author,'packet':vars(packet)})
        self.packet_ids.add(packet.packet_id)
        return node

    def reconcile(self,left,right):
        if left==right or left not in self.nodes or right not in self.nodes:
            raise ValueError('invalid fork')
        a,b=self.nodes[left],self.nodes[right]
        if a['kind']!='branch' or b['kind']!='branch':
            raise ValueError('not branch nodes')
        if a['parents']!=b['parents']: raise ValueError('different ancestors')
        pa,pb=a['payload']['packet'],b['payload']['packet']
        if pa['packet_id']==pb['packet_id'] or pa['root']==pb['root']:
            decision,reason='HOLD','NONINDEPENDENT_EVIDENCE'
        elif (pa['event'],pa['scope'])!=(pb['event'],pb['scope']):
            decision,reason='HOLD','INCOMPARABLE_SCOPE'
        elif pa['observation']!=pb['observation']:
            decision,reason='CONFLICT','OBSERVATION_DISAGREEMENT'
        else:
            decision,reason='MERGE','MATCHING_OBSERVATIONS'
        parents=tuple(sorted((left,right)))
        node=self._commit('reconciliation',parents,{'decision':decision,'reason':reason,'ancestor':a['parents'][0]})
        if decision=='MERGE': self.head=node
        return {'node':node,'decision':decision,'reason':reason,'parents':parents}

    def verify(self):
        seen={}
        for i,r in enumerate(self.records):
            if r['seq']!=i or r['prev']!=(self.records[i-1]['chain'] if i else '0'*64): return False
            if r['node']!=digest(r['data']): return False
            if r['chain']!=digest({k:r[k] for k in ('seq','prev','node','data')}): return False
            if r['node'] in seen: return False
            if any(p not in seen for p in r['data']['parents']): return False
            seen[r['node']]=r['data']
        return seen==self.nodes

def demonstration():
    l=ForkLedger()
    c=l.head
    a=l.branch(c,Packet('E1','t0','7','root-A','pA'),'agent-A')
    b=l.branch(c,Packet('E1','t0','7','root-B','pB'),'agent-B')
    return l,l.reconcile(a,b)

if __name__=='__main__':
    l,result=demonstration()
    print(json.dumps({'result':result,'records':len(l.records),'ledger_valid':l.verify()},indent=2))
