"""RSI-010: three-witness exact checkpoint, atomic local recall."""
from rsi009 import ExperienceBook, canonical, digest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import json

class Continuity(ExperienceBook):
 def __init__(self,path,keys,witnesses,stream):
  if len(witnesses)!=3 or len(set(witnesses.values())|set(keys.values()))!=12:raise ValueError('distinct keys required')
  self.witnesses=dict(witnesses);self.stream=stream;super().__init__(path,keys)
  pin=canonical([stream,{k:v.hex() for k,v in witnesses.items()}])
  self.db.execute('CREATE TABLE IF NOT EXISTS continuity(id INTEGER PRIMARY KEY CHECK(id=1),pin TEXT)')
  self.db.execute('INSERT OR IGNORE INTO continuity VALUES(1,?)',(pin,))
  if self.db.execute('SELECT pin FROM continuity').fetchone()[0]!=pin:self.close();raise ValueError('continuity pin mismatch')
 def head(self):
  def tail(table,col):
   row=self.db.execute(f'SELECT {col},hash FROM {table} ORDER BY {col} DESC LIMIT 1').fetchone()
   return list(row) if row else [-1,'0'*64]
  return {'domain':'RSI010','stream':self.stream,'keys':digest({k:v.hex() for k,v in self.keys.items()}),'frames':tail('frames','t'),'experience':tail('signed','seq')}
 def snapshot(self):
  self.db.execute('BEGIN')
  try:
   if not self.verify():raise ValueError('invalid history')
   return self.head()
  finally:self.db.rollback()
 def recall(self,i):raise ValueError('checkpoint required')
 def checked_recall(self,i,checkpoint,signatures):
  self.db.execute('BEGIN')
  try:
   if set(signatures)!=set(self.witnesses):raise ValueError('three witnesses required')
   for w,key in self.witnesses.items():Ed25519PublicKey.from_public_bytes(key).verify(bytes.fromhex(signatures[w]),canonical(checkpoint).encode())
   if not self.verify() or self.head()!=checkpoint:raise ValueError('continuity mismatch: HOLD')
   return [json.loads(r[0]) for r in self.db.execute('SELECT body FROM signed WHERE i=? ORDER BY seq',(str(i),))]
  finally:self.db.rollback()
