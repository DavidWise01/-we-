import sqlite3,json,secrets,time
from contextlib import closing
from wag137 import enc,root,bound,check,replay
from cryptography.exceptions import InvalidSignature

class Keeper:
 def __init__(self,path,g,key,initialize=False):
  self.path,self.g,self.key=path,g,key
  with closing(self.open()) as c:
   if initialize:
    c.execute('CREATE TABLE log(n INTEGER PRIMARY KEY, cert TEXT NOT NULL)')
    c.execute('INSERT INTO log VALUES(0,?)',(enc(bound(g,[],key)).decode(),));c.commit()
   self.head(c)
 def open(self):
  c=sqlite3.connect(self.path);c.execute('PRAGMA synchronous=FULL');return c
 def head(self,c):
  n,raw=c.execute('SELECT n,cert FROM log ORDER BY n DESC LIMIT 1').fetchone();b=json.loads(raw)
  self.key.public_key().verify(bytes.fromhex(b[1]),enc(b[0]))
  if b[0][:3]!=['WAG137-bound',root(self.g),n]:raise ValueError('identity')
  return b
 def retain(self,events):
  with closing(self.open()) as c:
   c.execute('BEGIN IMMEDIATE');old=self.head(c);check(self.g,events,old,self.key.public_key());new=bound(self.g,events,self.key)
   if new[0]!=old[0]:c.execute('INSERT INTO log VALUES(?,?)',(len(events),enc(new).decode()))
   c.commit();return new
 def respond(self,nonce):
  with closing(self.open()) as c:b=self.head(c)
  body=['WAG138',root(self.g),nonce,b];return [body,self.key.sign(enc(body)).hex()]

class Challenge:
 def __init__(self,g,clock=time.monotonic,ttl=5):
  self.g,self.clock=g,clock;self.deadline=clock()+ttl;self.nonce=secrets.token_hex(32);self.used=False
 def verify(self,events,pub,response):
  if self.used:raise ValueError('used')
  self.used=True
  if self.clock()>self.deadline or response is None:raise ValueError('expired or unavailable')
  b,sig=response;pub.verify(bytes.fromhex(sig),enc(b))
  if b[:3]!=['WAG138',root(self.g),self.nonce] or len(b)!=4:raise ValueError('challenge')
  s=check(self.g,events,b[3],pub)
  if len(events)!=b[3][0][2]:raise ValueError('unretained extension')
  return s
