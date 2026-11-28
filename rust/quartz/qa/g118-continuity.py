"""Persistent single-use challenge and dual-head prefix continuity. .dlw"""
import os,json,importlib.util
from pathlib import Path

def load(n):
    s=importlib.util.spec_from_file_location(n,Path(__file__).with_name(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
F=load('g109-freshness'); T=load('g106-transaction')

def issue(directory,ledger,roster,roster_pin,prior):
    c=F.Challenge(ledger,roster,roster_pin,prior['count'])
    if prior['ledger']!=ledger: raise ValueError('ledger')
    body=T.C.canonical(dict(ledger=ledger,roster=roster_pin,prior=prior))
    publish(directory,c.nonce+'.issued',body)
    return c.nonce

def publish(directory,name,body):
    with (Path(directory)/name).open('xb') as f:
        f.write(body);f.flush();os.fsync(f.fileno())
    T.C.M.syncdir(directory)

def verify(directory,nonce,responses,roster,roster_pin,root,objects,prior,prior_sig,prior_pin,candidate_sig,key):
    def out(state):return dict(state=state,authority='HOLD',independence_verified=False)
    if not F.h(nonce):return out('INVALID_NONCE')
    ledger=prior['ledger']; c=F.Challenge(ledger,roster,roster_pin,prior['count']);c.nonce=nonce
    expected=T.C.canonical(dict(ledger=ledger,roster=roster_pin,prior=prior))
    with (Path(directory)/(nonce+'.issued')).open('rb') as f: actual=f.read(4097)
    if actual!=expected:return out('CHALLENGE_MISMATCH')
    try:publish(directory,nonce+'.used',b'consumed\n')
    except FileExistsError:return out('REPLAY')
    result=c.verify(responses)
    if result['state']!='FRESH_SIGNED_DECLARATIONS':return result
    ref=result['reference']
    old=T.recover(root,objects,prior,prior_sig,key,prior_pin,ledger)
    new=T.recover(root,objects,ref,candidate_sig,key,T.fingerprint(ref,candidate_sig),ledger)
    h=ref['evidence']
    for _ in range(ref['count']-prior['count']):h=json.loads(T.S.recover(objects,h))['previous']
    if new[:len(old)]!=old or h!=prior['evidence']:return out('PREFIX_MISMATCH')
    return dict(out('SIGNED_PREFIX_CONFIRMED'),reference=ref)
