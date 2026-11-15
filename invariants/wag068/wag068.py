"""WAG-068: recursive dependency cascade and minimal failure-domain cut sets.

Deterministic synthetic model. A dependent component fails if ANY listed prerequisite
fails (OR-failure semantics). Shared domains are counted once; the model does not
establish probabilistic independence or Byzantine tolerance.
"""
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json

def hash_event(x):
    return sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

@dataclass(frozen=True)
class Node:
    name: str
    kind: str
    parents: tuple = ()
    ancestor: str = ''

class CascadeAudit:
    def __init__(self, quorum=3, max_cut_size=4):
        if type(quorum) is not int or quorum < 1 or type(max_cut_size) is not int or max_cut_size < 1:
            raise ValueError('policy')
        self.quorum, self.max_cut_size = quorum, max_cut_size
        self.nodes = {}
        self.history = []
        self._record('policy', {'quorum': quorum, 'max_cut_size': max_cut_size,
                                'semantics': 'any failed prerequisite fails dependent'})

    def _record(self, kind, payload):
        item = {'sequence': len(self.history), 'previous': self.history[-1]['hash'] if self.history else '0'*64,
                'kind': kind, 'payload': payload}
        item['hash'] = hash_event(item)
        self.history.append(item)

    def verify(self):
        return all(e['sequence'] == i and e['previous'] == (self.history[i-1]['hash'] if i else '0'*64)
                   and e['hash'] == hash_event({k:v for k,v in e.items() if k != 'hash'})
                   for i,e in enumerate(self.history))

    def add(self, node):
        if not isinstance(node, Node) or not node.name or node.name in self.nodes or node.kind not in ('domain','component','witness'):
            raise ValueError('invalid node')
        if len(node.parents) != len(set(node.parents)) or node.name in node.parents:
            raise ValueError('duplicate or cyclic parent')
        if node.kind == 'domain' and node.parents:
            raise ValueError('root domain cannot have parent')
        if node.kind != 'domain' and not node.parents:
            raise ValueError('dependent needs parents')
        if any(p not in self.nodes for p in node.parents):
            raise ValueError('unknown parent / cycle')
        if node.kind == 'witness':
            if not node.ancestor or any(n.kind == 'witness' and n.ancestor == node.ancestor for n in self.nodes.values()):
                raise ValueError('unique witness ancestry required')
        elif node.ancestor:
            raise ValueError('ancestor only for witnesses')
        self.nodes[node.name] = node
        self._record('node', {'name':node.name,'kind':node.kind,'parents':node.parents,'ancestor':node.ancestor})

    def witnesses(self):
        return tuple(sorted(n.name for n in self.nodes.values() if n.kind == 'witness'))

    def domains(self):
        return tuple(sorted(n.name for n in self.nodes.values() if n.kind == 'domain'))

    def failed_nodes(self, domains):
        domains = frozenset(domains)
        if not domains.issubset(self.domains()):
            raise ValueError('unknown failed domain')
        failed = set(domains)
        for node in self.nodes.values():
            if node.kind != 'domain' and any(p in failed for p in node.parents):
                failed.add(node.name)
        return frozenset(failed)

    def status(self, domains):
        failed = self.failed_nodes(domains)
        survivors = set(self.witnesses()) - failed
        return {'failed': sorted(failed), 'survivors': sorted(survivors),
                'quorum':len(survivors) >= self.quorum,
                'decision':'QUORUM_ELIGIBLE' if len(survivors) >= self.quorum else 'HOLD_CASCADE'}

    def minimal_cuts(self, target='quorum_loss'):
        if target not in ('quorum_loss','all_witnesses'):
            raise ValueError('target')
        ds = self.domains()
        minimal = []
        for size in range(1,min(self.max_cut_size,len(ds))+1):
            for group in combinations(ds,size):
                s = frozenset(group)
                if any(x.issubset(s) for x in minimal):
                    continue
                outcome=self.status(s)
                hit = not outcome['quorum'] if target == 'quorum_loss' else not outcome['survivors']
                if hit:
                    minimal.append(s)
        return [tuple(sorted(s)) for s in minimal]

    def inspect_failure(self, domain_names):
        names=tuple(sorted(set(domain_names)))
        output=self.status(names)
        self._record('failure',{'domains':names,'result':output})
        return output

def demonstration():
    graph=CascadeAudit(quorum=3)
    for name in ('power-y','power-z','host-a','host-b','host-c'):
        graph.add(Node(name,'domain'))
    graph.add(Node('network-x','component',('power-y',)))
    graph.add(Node('network-z','component',('power-z',)))
    graph.add(Node('router-a','component',('network-x','host-a')))
    graph.add(Node('router-b','component',('network-x','host-b')))
    graph.add(Node('router-c','component',('network-z','host-c')))
    for label,router,ancestor in [('W1','router-a','A'),('W2','router-b','B'),('W3','router-c','C')]:
        graph.add(Node(label,'witness',(router,),ancestor))
    cuts=graph.minimal_cuts()
    all_cuts=graph.minimal_cuts('all_witnesses')
    failed=graph.inspect_failure(('power-y',))
    return graph,{'quorum_cuts':cuts,'all_witness_cuts':all_cuts,'power_y_failure':failed,
                  'ledger_records':len(graph.history),'valid':graph.verify()}

if __name__ == '__main__':
    print(json.dumps(demonstration()[1],indent=2))
