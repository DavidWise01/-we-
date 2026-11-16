"""WAG-077 signed registry head reference. Local trust is not global transparency."""
from hashlib import sha256
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def h(x):return sha256(enc(x)).hexdigest()
class Registry:
 def __init__(self,name,key=None):
  if not name:raise ValueError('name')
  self.name=name;self.key=key or Ed25519PrivateKey.generate();self.public=self.key.public_key();self.events=[]
 def append(self,kind,subject,controller,epoch):
  if kind not in ('declare','revoke') or not subject or not controller or type(epoch)!=int or epoch<0:raise ValueError('event')
  e={'n':len(self.events),'kind':kind,'subject':subject,'controller':controller,'epoch':epoch,'prior':self.events[-1]['hash'] if self.events else '0'*64}
  e['hash']=h(e);self.events.append(e)
 def root(self,n=None):
  n=len(self.events) if n is None else n
  if type(n)!=int or not 0<=n<=len(self.events):raise ValueError('size')
  return h({'registry':self.name,'events':self.events[:n]})
 def head(self,n=None):
  n=len(self.events) if n is None else n
  record={'type':'WAG077_HEAD','registry':self.name,'size':n,'root':self.root(n)}
  return record,self.key.sign(enc(record))
 def valid(self):
  return all(e['n']==i and e['prior']==(self.events[i-1]['hash'] if i else '0'*64) and e['hash']==h({k:v for k,v in e.items() if k!='hash'}) for i,e in enumerate(self.events))
 def status(self,subject,controller,n=None):
  n=len(self.events) if n is None else n
  result='UNKNOWN'
  for e in self.events[:n]:
   if e['subject']==subject and e['controller']==controller:result='ACTIVE' if e['kind']=='declare' else 'REVOKED'
  return result
class Gate:
 def __init__(self,keys):
  if not keys:raise ValueError('keys')
  self.keys=dict(keys);self.observed={};self.quarantined=set();self.audit=[]
 def log(self,kind,data):
  row={'seq':len(self.audit),'prior':self.audit[-1]['hash'] if self.audit else '0'*64,'kind':kind,'data':data}
  row['hash']=h(row);self.audit.append(row)
 def audit_valid(self):
  return all(e['seq']==i and e['prior']==(self.audit[i-1]['hash'] if i else '0'*64) and e['hash']==h({k:v for k,v in e.items() if k!='hash'}) for i,e in enumerate(self.audit))
 def observe(self,record,signature,witness):
  if not witness or record.get('registry') not in self.keys:raise ValueError('unknown signer/witness')
  try:self.keys[record['registry']].verify(signature,enc(record))
  except (InvalidSignature,ValueError,TypeError) as ex:raise ValueError('signature') from ex
  if record.get('type')!='WAG077_HEAD' or type(record.get('size'))!=int or record['size']<0:raise ValueError('record')
  reg=record['registry'];previous=self.observed.get((reg,witness))
  if previous and record['size']<previous['size']:
   self.log('rollback',{'registry':reg,'witness':witness,'previous':previous,'new':record});self.quarantined.add(reg);return 'HOLD_ROLLBACK'
  if previous and record['size']==previous['size'] and record['root']!=previous['root']:
   self.log('fork',{'registry':reg,'witness':witness,'heads':[previous,record]});self.quarantined.add(reg);return 'QUARANTINE_SPLIT_VIEW'
  for (r,w),old in self.observed.items():
   if r==reg and w!=witness and old['size']==record['size'] and old['root']!=record['root']:
    self.log('fork',{'registry':reg,'witnesses':[w,witness],'heads':[old,record]});self.quarantined.add(reg);return 'QUARANTINE_SPLIT_VIEW'
  self.observed[(reg,witness)]=record
  self.log('observe',{'registry':reg,'witness':witness,'head':record})
  return 'OBSERVED'
 def evaluate(self,r,subject,controller,witnesses):
  if r.name not in self.keys:return 'HOLD_UNKNOWN_REGISTRY'
  if r.name in self.quarantined:return 'QUARANTINE_SPLIT_VIEW'
  if not r.valid():return 'HOLD_INVALID_LOG'
  heads=[self.observed.get((r.name,w)) for w in witnesses]
  if len(witnesses)!=3 or len(set(witnesses))!=3 or any(x is None for x in heads):return 'HOLD_MISSING_WITNESS'
  if len({(x['size'],x['root']) for x in heads})!=1:return 'HOLD_HEAD_DISAGREEMENT'
  if heads[0]['size']!=len(r.events) or heads[0]['root']!=r.root():return 'HOLD_STALE_OR_UNMATCHED_LOG'
  status=r.status(subject,controller)
  if status=='REVOKED':return 'HOLD_REVOKED'
  if status=='UNKNOWN':return 'HOLD_UNKNOWN_ANCESTRY'
  return 'LOCAL_DECLARED_ANCESTRY_ACCEPTED'
def demo():
 r=Registry('A');r.append('declare','W4','org-w',2);g=Gate({'A':r.public})
 for w in ('W1','W2','W3'):g.observe(*r.head(),w)
 first=g.evaluate(r,'W4','org-w',('W1','W2','W3'))
 r.append('revoke','W4','org-w',3)
 for w in ('W1','W2','W3'):g.observe(*r.head(),w)
 return {'initial':first,'after_revocation':g.evaluate(r,'W4','org-w',('W1','W2','W3')),'observations':len(g.audit),'audit_valid':g.audit_valid()}
if __name__=='__main__':print(demo())
