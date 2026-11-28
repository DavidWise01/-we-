"""Bounded immutable-value quarantine chain; externally pinned head required. .dlw"""
import hashlib,json,re
ZERO='0'*64
MAX=256
TARGETS=('native','native-repeat','node','node-repeat','chromium','chromium-repeat')
def digest(x):
    return hashlib.sha256(b'G94\0'+json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def valid_hash(x): return isinstance(x,str) and re.fullmatch('[0-9a-f]{64}',x) is not None
def verify(records,head):
    if not isinstance(records,list) or len(records)>MAX or not valid_hash(head): raise ValueError('bound or head')
    previous=ZERO; blocked=set(); first={}
    for i,r in enumerate(records):
        if set(r)!={'index','previous','subject','streams','state','digest'} or type(r['index']) is not int or r['index']!=i or r['previous']!=previous: raise ValueError('chain')
        subject=r['subject']; streams=r['streams']
        if not valid_hash(subject) or set(streams)!=set(TARGETS) or not all(valid_hash(v) for v in streams.values()): raise ValueError('fields')
        values=set(streams.values()); conflict=len(values)!=1 or (subject in first and first[subject]!=streams['native'])
        first.setdefault(subject,streams['native'])
        if conflict: blocked.add(subject)
        state='QUARANTINED' if subject in blocked else 'CONSISTENT_SUBMISSION'
        if r['state']!=state or r['digest']!=digest({k:v for k,v in r.items() if k!='digest'}): raise ValueError('state or digest')
        previous=r['digest']
    if previous!=head: raise ValueError('pinned head mismatch')
    return {'blocked':sorted(blocked),'authority':'HOLD'}
def append(records,head,subject,streams):
    verify(records,head)
    if len(records)>=MAX: raise ValueError('capacity')
    if not valid_hash(subject) or set(streams)!=set(TARGETS) or not all(valid_hash(v) for v in streams.values()): raise ValueError('fields')
    blocked=any(r['subject']==subject and (r['state']=='QUARANTINED' or r['streams']['native']!=streams['native']) for r in records) or len(set(streams.values()))!=1
    r={'index':len(records),'previous':head,'subject':subject,'streams':dict(streams),'state':'QUARANTINED' if blocked else 'CONSISTENT_SUBMISSION'}
    r['digest']=digest(r)
    new=records+[r]; verify(new,r['digest']); return new,r['digest']
