"""WAG-051 selective-abort preservation and explicit recovery.
Reference only: cannot certify unbiased entropy or independent witnesses.
"""
from dataclasses import dataclass
from hashlib import sha256
import json

def digest(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

@dataclass(frozen=True)
class Contributor:
    name: str
    root: str
    domain: str
    commitment: str

class CeremonyLedger:
    def __init__(self,cutoff=10,minimum=3):
        if type(cutoff) is not int or cutoff<1 or type(minimum) is not int or minimum<3:
            raise ValueError('policy')
        self.cutoff,self.minimum=cutoff,minimum
        self.rounds={};self.events=[]
        self._append('policy',dict(cutoff=cutoff,minimum=minimum,abort_policy='NO_SILENT_RETRY'))
    def _append(self,kind,value):
        r=dict(seq=len(self.events),previous=self.events[-1]['hash'] if self.events else '0'*64,kind=kind,value=value)
        r['hash']=digest(r);self.events.append(r)
    def verify(self):
        return all(r['seq']==i and r['previous']==(self.events[i-1]['hash'] if i else '0'*64)
                   and r['hash']==digest({k:v for k,v in r.items() if k!='hash'})
                   for i,r in enumerate(self.events))
    @staticmethod
    def pledge(round_id,name,secret):
        if not isinstance(secret,str) or len(secret)!=64 or any(c not in '0123456789abcdef' for c in secret):
            raise ValueError('secret')
        return digest(dict(tag='WAG051',round=round_id,contributor=name,secret=secret))
    def open_round(self,round_id,*,parent=None):
        if not round_id or round_id in self.rounds or (parent is not None and
           (parent not in self.rounds or self.rounds[parent]['status']!='ABORTED')):
            raise ValueError('invalid round lineage')
        self.rounds[round_id]=dict(parent=parent,status='OPEN',sources={},revealed={},close_reason=None)
        self._append('open',dict(round=round_id,parent=parent))
    def commit(self,round_id,source,tick):
        r=self.rounds.get(round_id)
        if (r is None or r['status']!='OPEN' or type(tick) is not int or tick>=self.cutoff
            or tick<0 or not isinstance(source,Contributor) or not all((source.name,source.root,source.domain))
            or source.name in r['sources'] or len(source.commitment)!=64
            or any(c not in '0123456789abcdef' for c in source.commitment)):
            raise ValueError('invalid commitment')
        r['sources'][source.name]=source
        self._append('commit',dict(round=round_id,tick=tick,source=vars(source)))
    def seal(self,round_id,tick):
        r=self.rounds.get(round_id)
        if (r is None or r['status']!='OPEN' or type(tick) is not int or tick!=self.cutoff
            or len(r['sources'])<self.minimum):
            raise ValueError('invalid seal')
        roots=[s.root for s in r['sources'].values()]
        domains=[s.domain for s in r['sources'].values()]
        if len(set(roots))!=len(roots) or len(set(domains))!=len(domains):
            raise ValueError('declared dependency')
        r['status']='SEALED'
        self._append('seal',dict(round=round_id,names=sorted(r['sources'])))
    def reveal(self,round_id,name,secret,tick):
        r=self.rounds.get(round_id)
        if (r is None or r['status']!='SEALED' or name not in r['sources']
            or name in r['revealed'] or type(tick) is not int or tick<=self.cutoff
            or self.pledge(round_id,name,secret)!=r['sources'][name].commitment):
            raise ValueError('invalid reveal')
        r['revealed'][name]=secret
        self._append('reveal',dict(round=round_id,name=name,tick=tick,secret=secret))
    def finalize(self,round_id,tick):
        r=self.rounds.get(round_id)
        if r is None or r['status']!='SEALED' or type(tick) is not int or tick<=self.cutoff:
            raise ValueError('invalid finalize')
        if len(r['revealed'])!=len(r['sources']):
            r['status']='ABORTED';r['close_reason']='WITHHELD_REVEAL'
            out=dict(status='ABORTED',missing=sorted(set(r['sources'])-set(r['revealed'])))
        else:
            r['status']='COMPLETE'
            material=b'WAG051:combine'+bytes([0])+b''.join(bytes.fromhex(r['revealed'][n]) for n in sorted(r['revealed']))
            out=dict(status='COMPLETE',output_digest=sha256(material).hexdigest())
        self._append('finalize',dict(round=round_id,tick=tick,result=out))
        return out
    def audit(self):
        statuses=[r['status'] for r in self.rounds.values()]
        complete=statuses.count('COMPLETE');aborted=statuses.count('ABORTED')
        return dict(attempts=len(statuses),complete=complete,aborted=aborted,
                    abort_rate=(aborted/(complete+aborted) if complete+aborted else None),
                    verdict='ABORT_HISTORY_PRESENT' if aborted else 'NO_RECORDED_ABORTS')

def demo():
    ledger=CeremonyLedger()
    for number,withholding,parent in ((1,False,None),(2,True,None),(3,False,'round-2')):
        name=f'round-{number}'
        ledger.open_round(name,parent=parent)
        secrets={s:sha256(('SYNTHETIC-'+name+'-'+s).encode()).hexdigest() for s in ('A','B','C')}
        for i,s in enumerate(('A','B','C')):
            ledger.commit(name,Contributor(s,'root'+s+'-'+name,'domain'+s,
                          ledger.pledge(name,s,secrets[s])),i+1)
        ledger.seal(name,10)
        for s in ('A','B','C'):
            if withholding and s=='C':continue
            ledger.reveal(name,s,secrets[s],11)
        ledger.finalize(name,12)
    return ledger

if __name__=='__main__':
    l=demo()
    print(json.dumps(dict(audit=l.audit(),valid=l.verify(),records=len(l.events)),indent=2))
