"""Local atomic ephemeral authority; logical time, not distributed consensus."""
import sqlite3,json,hashlib
from rsi007 import frame

def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'))
def digest(x): return hashlib.sha256(canonical(x).encode()).hexdigest()
class LeaseBook:
 def __init__(self,path):
  self.db=sqlite3.connect(path,isolation_level=None)
  self.db.executescript('CREATE TABLE IF NOT EXISTS frames(t INTEGER PRIMARY KEY, body TEXT NOT NULL, hash TEXT NOT NULL); CREATE TABLE IF NOT EXISTS experience(t INTEGER,i INTEGER,body TEXT NOT NULL,PRIMARY KEY(t,i));')
 def close(self): self.db.close()
 def advance(self,signals,prior,unavailable=()):
  self.db.execute('BEGIN IMMEDIATE')
  try:
   row=self.db.execute('SELECT t,hash FROM frames ORDER BY t DESC LIMIT 1').fetchone()
   t,prev=(row[0]+1,row[1]) if row else (0,'0'*64)
   f=frame(t,signals,prior,unavailable); f['previous']=prev
   # JSON normalization makes identity keys stable across restart.
   f=json.loads(canonical(f)); h=digest(f)
   self.db.execute('INSERT INTO frames VALUES(?,?,?)',(t,canonical(f),h));self.db.commit();return f
  except BaseException:self.db.rollback();raise
 def receipt(self,f,i):
  return {'tick':f['tick'],'identity':str(i),'assignment':f['roles'][str(i)],'frame_hash':digest(f)}
 def record(self,receipt,observation):
  self.db.execute('BEGIN IMMEDIATE')
  try:
   row=self.db.execute('SELECT t,body,hash FROM frames ORDER BY t DESC LIMIT 1').fetchone()
   if not row:raise ValueError('no authority')
   f=json.loads(row[1]);i=receipt['identity']
   if i not in f['roles'] or receipt!=self.receipt(f,i) or row[2]!=digest(f):raise ValueError('stale or mismatched authority')
   if f['roles'][i]['duty']!='UP':raise ValueError('not on watch')
   self.db.execute('INSERT INTO experience VALUES(?,?,?)',(row[0],int(i),canonical(observation)));self.db.commit()
  except BaseException:self.db.rollback();raise
 def verify(self):
  prev='0'*64
  for n,(t,body,h) in enumerate(self.db.execute('SELECT t,body,hash FROM frames ORDER BY t')):
   f=json.loads(body)
   if t!=n or f['tick']!=t or f['previous']!=prev or digest(f)!=h:return False
   prev=h
  return True
