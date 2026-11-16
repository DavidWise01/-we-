"""WAG-094 GitHub reference: signed logical-order and ancestry gate.
This is NOT an independently witnessed clock or live beacon client.
"""
import hashlib,json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
def encode(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def H(x):return hashlib.sha256(encode(x)).hexdigest()
def sign(key,msg):return key.sign(encode(msg)).hex()
def valid(key,msg,sig):
 try:key.verify(bytes.fromhex(sig),encode(msg));return True
 except (ValueError,TypeError,InvalidSignature):return False
class Gate:
 def __init__(self,authors,root,epoch,round_id,n=17,k=3):
  if len(authors)!=3:raise ValueError('authorities')
  for field in ('root','operator','domain'):
   values=[authors[a][field] for a in authors]
   if len(set(values))!=3:raise ValueError('shared ancestry')
  if len(root)!=64 or not 0<k<=n:raise ValueError('size/root')
  self.authors=authors;self.root=root;self.epoch=epoch;self.round=round_id;self.n=n;self.k=k;self.commit=None;self.releases={};self.sampled=None
  self.events=[];self.record('genesis',{'root':root,'epoch':epoch,'round':round_id})
 def record(self,kind,data):
  item={'seq':len(self.events),'prev':self.events[-1]['hash'] if self.events else '0'*64,'kind':kind,'data':data}
  item['hash']=H(item);self.events.append(item)
 def verify(self):return all(x['seq']==i and x['prev']==(self.events[i-1]['hash'] if i else '0'*64) and x['hash']==H({k:v for k,v in x.items() if k!='hash'}) for i,x in enumerate(self.events))
 def add(self,msg,sig):
  if not isinstance(msg,dict):raise ValueError('message')
  who=msg.get('authority')
  if who not in self.authors:raise ValueError('authority')
  expected={'epoch':self.epoch,'round':self.round,'root':self.root}
  if not all(msg.get(k)==v for k,v in expected.items()):raise ValueError('scope')
  if not valid(self.authors[who]['key'],msg,sig):raise ValueError('signature')
  if msg.get('kind')=='commit':
   if who!='clock' or self.commit is not None or self.releases:raise ValueError('commit order')
   if not isinstance(msg.get('slot'),int) or msg['slot']<0:raise ValueError('slot')
   if set(msg)!=set(expected)|{'kind','authority','slot'}:raise ValueError('fields')
   self.commit=dict(msg);self.record('commit',msg);return
  if msg.get('kind')!='release' or who not in ('b','c') or self.commit is None or self.sampled is not None or who in self.releases:raise ValueError('release order')
  if set(msg)!=set(expected)|{'kind','authority','slot','output'}:raise ValueError('fields')
  if not isinstance(msg.get('slot'),int) or msg['slot']<=self.commit['slot']:raise ValueError('slot')
  if not isinstance(msg.get('output'),str) or len(msg['output'])!=64 or any(ch not in '0123456789abcdef' for ch in msg['output']):raise ValueError('output')
  self.releases[who]=dict(msg);self.record('release',msg)
 def sample(self):
  if self.commit is None or set(self.releases)!={'b','c'} or self.sampled is not None:raise ValueError('not ready')
  seed=bytes.fromhex(H({'commit':self.commit,'beacons':[self.releases['b'],self.releases['c']]}))
  ans=[];counter=0;limit=(1<<256)//self.n*self.n
  while len(ans)<self.k:
   v=int.from_bytes(hashlib.sha256(seed+counter.to_bytes(8,'big')).digest(),'big');counter+=1
   if v>=limit:continue
   pos=v%self.n
   if pos not in ans:ans.append(pos)
  self.sampled=tuple(ans);self.record('sample',ans);return self.sampled
def demo():
 keys=[Ed25519PrivateKey.generate() for _ in range(3)]
 authors={name:{'key':key.public_key(),'root':'r'+name,'operator':'o'+name,'domain':'d'+name} for name,key in zip(('clock','b','c'),keys)}
 g=Gate(authors,hashlib.sha256(b'archive bytes').hexdigest(),94,'round-01')
 messages=[{'kind':'commit','authority':'clock','epoch':94,'round':'round-01','root':g.root,'slot':12}]
 messages +=[{'kind':'release','authority':name,'epoch':94,'round':'round-01','root':g.root,'slot':i+12,'output':hashlib.sha256(name.encode()).hexdigest()} for i,name in enumerate(('b','c'),1)]
 for key,m in zip(keys,messages):g.add(m,sign(key,m))
 return {'positions':g.sample(),'audit_valid':g.verify(),'records':len(g.events)}
if __name__=='__main__':print(demo())
