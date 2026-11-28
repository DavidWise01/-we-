"""Pinned Ed25519 roster and failure-independent contradiction observation. .dlw"""
import hashlib,json,importlib.util
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

def load(n):
    s=importlib.util.spec_from_file_location(n,Path(__file__).with_name(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
A=load('g95-ancestry');R=load('g93-reconcile');Q=load('g94-quarantine')
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def digest(domain,x): return hashlib.sha256(domain+canonical(x)).hexdigest()
def message(roster,graph,w): return b'G101\0'+canonical([roster,graph,w])
def authenticate(subject,graph,witnesses,roster,roster_pin,blocked,expected_result):
    def out(state): return {'state':state,'authority':'HOLD','independence_verified':False}
    if subject in blocked:return out('QUARANTINED')
    if len(roster)!=3 or not all(A.h(k) and A.h(v) for k,v in roster.items()) or len(set(roster.values()))!=3 or digest(b'G101-roster\0',roster)!=roster_pin:return out('ROSTER_MISMATCH')
    if len(witnesses)!=3:return out('INVALID_WITNESS')
    claims=[]
    try:
        for w,sig in witnesses:
            if w['root'] not in roster:return out('ROSTER_MISMATCH')
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(roster[w['root']])).verify(bytes.fromhex(sig),message(roster,graph,w))
            claims.append(w)
    except (ValueError,InvalidSignature,KeyError,TypeError):return out('SIGNATURE_INVALID')
    if any(w['result']!=expected_result for w in claims):return out('RESULT_MISMATCH')
    state=A.adjudicate(subject,graph,claims,blocked)['state']
    return out('SIGNED_DECLARED_AGREEMENT' if state=='DECLARED_AGREEMENT' else state)

def observe(revision,lock,pin,outputs,exits,subject,records,head):
    """Record complete, well-formed submitted streams even on declared failure."""
    Q.verify(records,head)
    result=R.reconcile(revision,lock,pin,outputs,exits)
    comparison=result
    if result['state']=='EXECUTION_FAILURE_DECLARED':
        comparison=R.reconcile(revision,lock,pin,outputs,dict.fromkeys(R.TARGETS,0))
    if 'sha256' in comparison:
        records,head=Q.append(records,head,subject,comparison['sha256'])
    return {'execution':result['state'],'comparison':comparison['state'],'records':records,'head':head,'blocked':Q.verify(records,head)['blocked'],'authority':'HOLD'}
