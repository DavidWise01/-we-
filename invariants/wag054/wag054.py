"""WAG-054 reference: disjoint fallback origin, one recovery, terminal closure."""
from dataclasses import dataclass,asdict
from hashlib import sha256
import json
def sha(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
@dataclass(frozen=True)
class Source:
 name:str
 ancestry:tuple
 operator:str
 infrastructure:str
 domain:str
class Ledger:
 def __init__(self):
  self.sources={};self.ceremonies={};self.children={};self.records=[]
  self.append('policy',{'max_recovery':1})
 def append(self,kind,data):
  r={'seq':len(self.records),'prev':self.records[-1]['hash'] if self.records else '0'*64,'kind':kind,'data':data}
  r['hash']=sha(r);self.records.append(r)
 def verify(self):
  return all(x['seq']==i and x['prev']==(self.records[i-1]['hash'] if i else '0'*64) and x['hash']==sha({k:v for k,v in x.items() if k!='hash'}) for i,x in enumerate(self.records))
 def source(self,s):
  if not isinstance(s,Source) or not all((s.name,s.ancestry,s.operator,s.infrastructure,s.domain)) or not all(s.ancestry) or s.name in self.sources:raise ValueError('source')
  self.sources[s.name]=s;self.append('source',asdict(s))
 def start(self,cid,ids):
  if not cid or cid in self.ceremonies or not ids or len(ids)!=len(set(ids)) or any(i not in self.sources for i in ids):raise ValueError('start')
  self.ceremonies[cid]={'id':cid,'sources':tuple(ids),'parent':None,'state':'OPEN'}
  self.append('start',self.ceremonies[cid].copy())
 def abort(self,cid,reason):
  if cid not in self.ceremonies or self.ceremonies[cid]['state']!='OPEN' or not reason:raise ValueError('abort')
  self.ceremonies[cid]['state']='ABORTED';self.append('abort',{'id':cid,'reason':reason})
 def recover(self,cid,newid,fallback):
  if cid not in self.ceremonies or self.ceremonies[cid]['state']!='ABORTED' or self.ceremonies[cid]['parent'] is not None or cid in self.children or not newid or newid in self.ceremonies or fallback not in self.sources:raise ValueError('recovery')
  old=self.ceremonies[cid];base=[self.sources[i] for i in old['sources']];r=self.sources[fallback]
  issues=[]
  if set(r.ancestry)&set().union(*(set(s.ancestry) for s in base)):issues.append('ancestry')
  for key in ('operator','infrastructure','domain'):
   if getattr(r,key) in [getattr(s,key) for s in base]:issues.append(key)
  if fallback in old['sources']:issues.append('reused')
  if issues:
   self.append('hold',{'parent':cid,'fallback':fallback,'issues':issues})
   return 'HOLD'
  self.ceremonies[newid]={'id':newid,'sources':old['sources']+(fallback,),'parent':cid,'state':'OPEN'}
  self.children[cid]=newid;self.append('recover',self.ceremonies[newid].copy())
  return 'RECOVERY_OPEN'
 def close(self,cid,success,reason=''):
  if cid not in self.ceremonies or self.ceremonies[cid]['state']!='OPEN' or (not success and not reason):raise ValueError('closure')
  self.ceremonies[cid]['state']='CLOSED_SUCCESS' if success else 'CLOSED_FAILED'
  self.append('closure',{'id':cid,'state':self.ceremonies[cid]['state'],'reason':reason})
 def terminal(self,cid):
  if cid not in self.ceremonies:raise ValueError('unknown')
  return self.ceremonies[cid]['state'].startswith('CLOSED_')
def demo():
 a=Ledger()
 for i in range(3):a.source(Source('E'+str(i),('r'+str(i),),'op'+str(i),'infra'+str(i),'d'+str(i)))
 a.source(Source('R',('new',),'newop','newinfra','newdomain'))
 a.start('C0',('E0','E1','E2'));a.abort('C0','withheld')
 decision=a.recover('C0','C1','R');a.close('C1',True)
 return a,decision
if __name__=='__main__':
 a,d=demo();print({'decision':d,'records':len(a.records),'verified':a.verify(),'terminal':a.terminal('C1')})
