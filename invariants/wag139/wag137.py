from wag135 import enc,root,validate,verify,transition
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import json

def topology(t):
    if set(t)!=set('HON'): raise ValueError('topology membership')
    if any(not isinstance(v,list) or not v or any(not isinstance(x,str) or not x for x in v) for v in t.values()): raise ValueError('roots')
    sets=list(map(set,t.values()))
    if any(a&b for i,a in enumerate(sets) for b in sets[:i]): raise ValueError('shared root')

def start(mesh,members,roots):
    validate(members);topology(roots)
    return dict(mesh=mesh,seq=0,epoch=0,members=members,retired=[],q=[156,0,0],pending={},spent=[],roots=roots)

def advance(s,o):
    t=transition(s,o)
    if o['kind']=='rotate':
        topology(o['roots']);t['roots']=o['roots']
    return t

def propose(s,o):return ['WAG137',s['mesh'],root(s),o,root(advance(s,o))]

def replay(g,events):
    if g!=start(g['mesh'],g['members'],g['roots']):raise ValueError('genesis')
    s=json.loads(enc(g))
    for p,a,b in events:
        if len(p)!=5 or p[:3]!=['WAG137',s['mesh'],root(s)] or p!=propose(s,p[3]):raise ValueError('ancestry')
        verify(s['members'],['approve',p],a);t=advance(s,p[3])
        if p[3]['kind']=='rotate':verify(t['members'],['accept',p],b or {})
        elif b is not None:raise ValueError('unexpected acceptance')
        s=t
    return s

def bound(g,events,keeper):
    s=replay(g,events);b=['WAG137-bound',root(g),len(events),root(events),root(s)]
    return [b,keeper.sign(enc(b)).hex()]

def check(g,events,certificate,public):
    b,sig=certificate;public.verify(bytes.fromhex(sig),enc(b))
    if len(b)!=5 or b[:2]!=['WAG137-bound',root(g)] or type(b[2])!=int or b[2]<0:raise ValueError('scope')
    n=b[2]
    if len(events)<n:raise ValueError('truncated')
    if root(events[:n])!=b[3] or root(replay(g,events[:n]))!=b[4]:raise ValueError('prefix')
    return replay(g,events)
