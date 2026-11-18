from itertools import combinations

def audit(graph, witnesses, trusted_roots):
    """Declared control graph: edges point from a subject to its controllers."""
    if len(witnesses)!=3 or len(set(witnesses))!=3:return 'HOLD_MEMBERSHIP',{}
    def roots(node,active):
        if node in active:raise ValueError('cycle')
        if node not in graph:raise ValueError('missing node')
        parents=graph[node]
        if not parents:
            if node not in trusted_roots:raise ValueError('unknown root')
            return {node}
        if node in trusted_roots:raise ValueError('root has controller')
        return set().union(*(roots(p,active|{node}) for p in parents))
    try:r={w:roots(w,set()) for w in witnesses}
    except (ValueError,TypeError):return 'HOLD_ANCESTRY',{}
    shared={f'{a}/{b}':sorted(r[a]&r[b]) for a,b in combinations(witnesses,2) if r[a]&r[b]}
    return ('HOLD_SHARED_ROOT' if shared else 'DISJOINT_DECLARED_ROOTS'),shared

def blast_radius(graph,witnesses,root):
    def reachable(n,seen):
        if n==root:return True
        if n in seen:return False
        return any(reachable(p,seen|{n}) for p in graph.get(n,()))
    return tuple(w for w in witnesses if reachable(w,set()))
