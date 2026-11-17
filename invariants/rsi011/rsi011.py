"""Separate monotonic anchor and durable hold; single-host reference."""
import sqlite3,json
from rsi010 import Continuity,canonical,digest,Ed25519PublicKey

class Anchor:
 def __init__(self,path,stream,witnesses):
  self.db=sqlite3.connect(path,isolation_level=None);self.stream=stream;self.keys=dict(witnesses)
  if len(self.keys)!=3 or len(set(self.keys.values()))!=3:raise ValueError('three distinct witnesses')
  self.db.executescript('CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY CHECK(id=1),pin TEXT,head TEXT,signatures TEXT,held INTEGER); CREATE TABLE IF NOT EXISTS incidents(seq INTEGER PRIMARY KEY,reason TEXT);')
  pin=canonical([stream,{k:v.hex() for k,v in self.keys.items()}]);self.db.execute('INSERT OR IGNORE INTO state VALUES(1,?,NULL,NULL,0)',(pin,))
  if self.db.execute('SELECT pin FROM state').fetchone()[0]!=pin:self.db.close();raise ValueError('anchor pin mismatch')
 def close(self):self.db.close()
 def authenticate(self,h,s):
  if h['domain']!='RSI010' or h['stream']!=self.stream or set(s)!=set(self.keys):raise ValueError('wrong stream or quorum')
  for k,v in self.keys.items():Ed25519PublicKey.from_public_bytes(v).verify(bytes.fromhex(s[k]),canonical(h).encode())
 def publish(self,h,s):
  self.authenticate(h,s);self.db.execute('BEGIN IMMEDIATE')
  try:
   old,held=self.db.execute('SELECT head,held FROM state').fetchone()
   if held:raise ValueError('HOLD')
   if old:
    o=json.loads(old)
    if h['keys']!=o['keys'] or any(h[k][0]<o[k][0] or (h[k][0]==o[k][0] and h[k]!=o[k]) for k in ('frames','experience')):raise ValueError('nonmonotonic checkpoint')
   self.db.execute('UPDATE state SET head=?,signatures=?',(canonical(h),canonical(s)));self.db.commit()
  except BaseException:self.db.rollback();raise
 def held(self):return bool(self.db.execute('SELECT held FROM state').fetchone()[0])
 def recall(self,book,i):
  self.db.execute('BEGIN IMMEDIATE')
  try:
   h,s,held=self.db.execute('SELECT head,signatures,held FROM state').fetchone()
   if held or h is None:raise ValueError('HOLD or missing anchor')
   try:
    if book.stream!=self.stream or book.witnesses!=self.keys:raise ValueError('wrong book')
    result=book.checked_recall(i,json.loads(h),json.loads(s))
   except Exception as e:
    self.db.execute('UPDATE state SET held=1');self.db.execute('INSERT INTO incidents(reason) VALUES(?)',(type(e).__name__,));self.db.commit();raise ValueError('continuity failure: durable HOLD') from e
   self.db.commit();return result
  except BaseException:
   if self.db.in_transaction:self.db.rollback()
   raise
