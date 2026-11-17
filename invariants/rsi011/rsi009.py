"""Identity-bound signed experience; local reference, not distributed consensus."""
from rsi008 import LeaseBook, canonical, digest
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

class ExperienceBook(LeaseBook):
 def __init__(self,path,keys):
  if set(keys)!=set(map(str,range(9))) or len(set(keys.values()))!=9:raise ValueError('nine distinct keys required')
  self.keys=dict(keys); super().__init__(path)
  self.db.executescript('CREATE TABLE IF NOT EXISTS config(id INTEGER PRIMARY KEY CHECK(id=1), keys TEXT); CREATE TABLE IF NOT EXISTS signed(seq INTEGER PRIMARY KEY, t INTEGER, i TEXT, body TEXT, sig TEXT, hash TEXT, UNIQUE(t,i));')
  pin=canonical({i:k.hex() for i,k in keys.items()})
  self.db.execute('INSERT OR IGNORE INTO config VALUES(1,?)',(pin,))
  if self.db.execute('SELECT keys FROM config').fetchone()[0]!=pin:self.close();raise ValueError('key pin mismatch')
 def record(self,*args):raise ValueError('signed record required')
 def payload(self,f,i,observation):
  return {'domain':'RSI009','receipt':self.receipt(f,i),'observation':observation}
 def check(self,p,sig,f):
  r=p['receipt'];i=r['identity']
  if p['domain']!='RSI009' or r!=self.receipt(f,i) or r['assignment']['duty']!='UP':raise ValueError('invalid authority')
  Ed25519PublicKey.from_public_bytes(self.keys[i]).verify(bytes.fromhex(sig),canonical(p).encode())
 def append(self,p,sig):
  self.db.execute('BEGIN IMMEDIATE')
  try:
   t,body,h=self.db.execute('SELECT t,body,hash FROM frames ORDER BY t DESC LIMIT 1').fetchone()
   f=json.loads(body)
   if digest(f)!=h:raise ValueError('frame tamper')
   self.check(p,sig,f);i=p['receipt']['identity']
   row=self.db.execute('SELECT seq,hash FROM signed ORDER BY seq DESC LIMIT 1').fetchone()
   seq,prev=(row[0]+1,row[1]) if row else (0,'0'*64)
   h=digest([prev,p,sig]);self.db.execute('INSERT INTO signed VALUES(?,?,?,?,?,?)',(seq,t,i,canonical(p),sig,h));self.db.commit()
  except BaseException:self.db.rollback();raise
 def verify(self):
  try:
   if not super().verify():return False
   prev='0'*64
   for n,(seq,t,i,body,sig,h) in enumerate(self.db.execute('SELECT * FROM signed ORDER BY seq')):
    p=json.loads(body); f=json.loads(self.db.execute('SELECT body FROM frames WHERE t=?',(t,)).fetchone()[0]);self.check(p,sig,f)
    if seq!=n or i!=p['receipt']['identity'] or h!=digest([prev,p,sig]):return False
    prev=h
   return True
  except Exception:return False
 def recall(self,i):
  if not self.verify():raise ValueError('invalid history')
  return [json.loads(b[0]) for b in self.db.execute('SELECT body FROM signed WHERE i=? ORDER BY seq',(str(i),))]
