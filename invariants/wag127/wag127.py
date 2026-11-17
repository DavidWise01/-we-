import sqlite3,json,secrets,time
from contextlib import closing
from cryptography.exceptions import InvalidSignature
from wag125 import enc,root,inspect,replay

class LiveFloor:
 def __init__(self,path,mesh,key,keys,initialize=False):
  self.path=path;self.mesh=mesh;self.key=key;self.keys=keys
  with closing(sqlite3.connect(path)) as c:
   if initialize:
    c.execute('CREATE TABLE floor(id INTEGER PRIMARY KEY CHECK(id=1), mesh TEXT, g INTEGER, h TEXT)');c.execute('INSERT INTO floor VALUES(1,?,0,?)',(mesh,root(replay(mesh,keys,[]))));c.commit()
   if c.execute('SELECT mesh FROM floor').fetchone()!=(mesh,):raise ValueError('scope')
 def advance(self,chains):
  status,s=inspect(self.mesh,self.keys,chains)
  if status!='CURRENT':raise ValueError(status)
  with closing(sqlite3.connect(self.path)) as c:
   c.execute('BEGIN IMMEDIATE');g,h=c.execute('SELECT g,h FROM floor').fetchone()
   if s['g']<g or root(replay(self.mesh,self.keys,chains[0][:g]))!=h:raise ValueError('regression or fork')
   c.execute('UPDATE floor SET g=?,h=?',(s['g'],root(s)));c.commit()
 def respond(self,nonce):
  with closing(sqlite3.connect(self.path)) as c:g,h=c.execute('SELECT g,h FROM floor').fetchone()
  body=['WAG127',self.mesh,nonce,g,h];return [body,self.key.sign(enc(body)).hex()]
class Challenge:
 def __init__(self,mesh,ttl=5,clock=time.monotonic):
  self.mesh=mesh;self.nonce=secrets.token_hex(32);self.clock=clock;self.deadline=clock()+ttl;self.used=False
 def verify(self,pub,keys,chains,response):
  if self.used:return 'HOLD_USED'
  self.used=True
  if self.clock()>self.deadline:return 'HOLD_EXPIRED'
  if response is None:return 'HOLD_UNAVAILABLE'
  try:
   body,sig=response;pub.verify(bytes.fromhex(sig),enc(body));tag,mesh,nonce,g,h=body
   if (tag,mesh,nonce)!=('WAG127',self.mesh,self.nonce) or type(g)!=int or g<0:raise ValueError('scope')
  except (InvalidSignature,ValueError,TypeError,KeyError):return 'HOLD_INVALID'
  status,s=inspect(self.mesh,keys,chains)
  if status!='CURRENT':return status
  if s['g']<g:return 'HOLD_ROLLBACK'
  if root(replay(self.mesh,keys,chains[0][:g]))!=h:return 'HOLD_FORK'
  return 'CURRENT'
