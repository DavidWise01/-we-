"""Declared ancestry adjudication; never authenticates identities. .dlw"""
import hashlib,json,re

def h(x): return isinstance(x,str) and re.fullmatch(r'[0-9a-f]{64}',x) is not None and x!='0'*64

def subject(source,lock,procedure):
    if not all(h(x) for x in (source,lock,procedure)): raise ValueError('commitment')
    return hashlib.sha256(b'G95\0'+b''.join(bytes.fromhex(x) for x in (source,lock,procedure))).hexdigest()

def adjudicate(expected,graph,witnesses,blocked=()):
    def result(state): return {'state':state,'authority':'HOLD','authenticated':False}
    if not h(expected) or len(graph)>128 or len(witnesses)!=3: return result('INVALID')
    if any(not h(k) or not isinstance(v,list) or len(v)>8 or len(set(v))!=len(v) or not all(h(p) and p in graph for p in v) for k,v in graph.items()): return result('INVALID_GRAPH')
    cache={}
    def closure(k,active):
        if k in active: raise ValueError('cycle')
        if k not in cache:
            s={k}
            for p in graph[k]: s.update(closure(p,active|{k}))
            cache[k]=s
        return cache[k]
    try:
        for k in graph: closure(k,set())
    except ValueError: return result('INVALID_GRAPH')
    if any(set(w)!={'root','subject','observation','result'} or not all(h(v) for v in w.values()) or w['root'] not in graph for w in witnesses): return result('INVALID_WITNESS')
    if any(w['subject']!=expected for w in witnesses): return result('SUBJECT_MISMATCH')
    if expected in blocked: return result('QUARANTINED')
    if len({w['observation'] for w in witnesses})!=3: return result('DUPLICATE_OBSERVATION')
    roots=[cache[w['root']] for w in witnesses]
    if any(roots[i]&roots[j] for i in range(3) for j in range(i)): return result('SHARED_ANCESTRY')
    if len({w['result'] for w in witnesses})!=1: return result('CONTRADICTORY')
    return result('DECLARED_AGREEMENT')
