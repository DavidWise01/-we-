from wag135 import enc, root, validate, verify, proposal, transition
import json
from contextlib import closing


def replay(genesis, events, expected):
    validate(genesis['members'])
    if genesis != {'mesh':genesis['mesh'],'seq':0,'epoch':0,'members':genesis['members'],'retired':[],'q':[156,0,0],'pending':{},'spent':[]}:
        raise ValueError('genesis')
    s=json.loads(enc(genesis))
    for p,old,new in events:
        if len(p)!=5 or p[:3]!=['WAG135',s['mesh'],root(s)] or p != proposal(s,p[3]): raise ValueError('ancestry')
        verify(s['members'],['approve',p],old)
        t=transition(s,p[3])
        if p[3]['kind']=='rotate': verify(t['members'],['accept',p],new or {})
        elif new is not None: raise ValueError('unexpected acceptance')
        s=t
    if expected is None or root(s)!=expected: raise ValueError('head mismatch')
    return s


def export(gate, expected):
    with closing(gate.open()) as c:
        c.execute('BEGIN')
        rows=c.execute('SELECT seq,body FROM journal ORDER BY seq').fetchall()
        if [n for n,_ in rows]!=list(range(1,len(rows)+1)): raise ValueError('journal gap')
        events=[json.loads(b) for _,b in rows]
        s=replay(gate.genesis,events,expected)
        if s!=json.loads(c.execute('SELECT body FROM head').fetchone()[0]): raise ValueError('local head mismatch')
        return events,s
