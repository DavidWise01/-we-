"""Unanimous view change; conservative halt if old view could have certified."""
import json
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

def enc(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
class Witness:
 def __init__(self,name,key): self.name=name; self.key=key; self.view=0; self.lock=None; self.closed={}
 def vote(self,value):
  if self.view in self.closed or (self.lock is not None and self.lock!=value): raise ValueError('locked or closed')
  self.lock=value; return self.key.sign(enc(['vote',self.name,self.view,value])).hex()
 def close(self):
  if self.view not in self.closed:self.closed[self.view]=self.lock
  v=self.closed[self.view];return [v,self.key.sign(enc(['close',self.name,self.view,v])).hex()]
 def advance(self,proof,keys):
  if decision(self.view,proof,keys)!='ADVANCE':raise ValueError('unsafe')
  if self.view not in self.closed:raise ValueError('not closed')
  self.view+=1;self.lock=None

def check(view,proof,keys,tag):
 if len(keys)!=3 or len({k.public_bytes(Encoding.Raw,PublicFormat.Raw) for k in keys.values()})!=3 or set(proof)!=set(keys):return False
 try:
  for n,k in keys.items():
   value,sig=proof[n];k.verify(bytes.fromhex(sig),enc([tag,n,view,value]))
  return True
 except (InvalidSignature,ValueError,TypeError):return False

def decision(view,proof,keys):
 if not check(view,proof,keys,'close'):return 'HOLD_INVALID'
 values=[p[0] for p in proof.values()]
 if values[0] is not None and all(v==values[0] for v in values):return 'RECOVER_OLD_CERTIFICATE'
 return 'ADVANCE'

def certified(view,value,proof,keys):
 return value is not None and check(view,proof,keys,'vote') and all(p[0]==value for p in proof.values())
