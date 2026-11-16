"""WAG-081 GitHub compact reference. Full 34-test local artifact accompanies conversation.
Uses sibling wag079.py range-frontier proof verifier, SQLite writer serialization.
"""
import sys,sqlite3,json,hashlib
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"wag079"))
from wag079 import verify_proof,ConsistencyProof
def C(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def H(x):return hashlib.sha256(C(x)).hexdigest()
def proof_hash(p):return H(dict(old=p.old_size,new=p.new_size,old_blocks=[vars(b) for b in p.old_blocks],appended=[vars(b) for b in p.appended_blocks]))
class Hold(Exception):pass
class AtomicGate:
 def __init__(self,path,public_keys,old_size=None,old_root=None,challenge=None):
  self.path=str(path);self.keys=public_keys
  if len(public_keys)!=3:raise Hold('THREE_WITNESSES_REQUIRED')
  with sqlite3.connect(self.path) as db:
   db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA synchronous=FULL')
   db.execute('CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY CHECK(id=1),epoch INTEGER,size INTEGER,root TEXT,challenge TEXT)')
   db.execute('CREATE TABLE IF NOT EXISTS used(id TEXT PRIMARY KEY)')
   db.execute('CREATE TABLE IF NOT EXISTS journal(seq INTEGER PRIMARY KEY,prior TEXT,event TEXT,digest TEXT)')
   if not db.execute('SELECT 1 FROM state').fetchone():
    if not(old_size and old_root and challenge):raise Hold('MISSING_GENESIS')
    db.execute('INSERT INTO state VALUES(1,0,?,?,?)',(old_size,old_root,challenge))
    self.event(db,dict(kind='genesis',root=old_root,size=old_size))
 def event(self,db,data):
  row=db.execute('SELECT seq,digest FROM journal ORDER BY seq DESC LIMIT 1').fetchone()
  seq=row[0]+1 if row else 0;prior=row[1] if row else '0'*64
  db.execute('INSERT INTO journal VALUES(?,?,?,?)',(seq,prior,C(data).decode(),H(dict(seq=seq,prior=prior,event=data))))
 def state(self):
  with sqlite3.connect(self.path) as db:
   e,s,r,c=db.execute('SELECT epoch,size,root,challenge FROM state WHERE id=1').fetchone()
   return dict(epoch=e,size=s,root=r,challenge=c)
 @staticmethod
 def signable(epoch,challenge,old_size,old_root,proof,new_root):
  return b'WAG-081.atomic.v1\x00'+C(dict(epoch=epoch,challenge=challenge,old_size=old_size,old_root=old_root,new_size=proof.new_size,new_root=new_root,proof_hash=proof_hash(proof)))
 def advance(self,proof,new_root,votes,expected):
  """votes: (identity, unique_receipt_id, Ed25519_signature)"""
  db=sqlite3.connect(self.path,timeout=3,isolation_level=None)
  try:
   db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA synchronous=FULL');db.execute('BEGIN IMMEDIATE')
   epoch,size,root,challenge=db.execute('SELECT epoch,size,root,challenge FROM state').fetchone()
   if (epoch,size,root,challenge)!=expected:raise Hold('STALE_CHECKPOINT')
   if not isinstance(proof,ConsistencyProof) or proof.old_size!=size or proof.new_size<=size or not verify_proof(proof,root,new_root):raise Hold('INVALID_MERKLE_PREFIX')
   if len(votes)!=3 or {v[0] for v in votes}!=set(self.keys):raise Hold('BAD_QUORUM')
   ids=[v[1] for v in votes]
   if any(not isinstance(x,str) or not x for x in ids) or len(set(ids))!=3:raise Hold('BAD_RECEIPT_IDS')
   if db.execute('SELECT id FROM used WHERE id IN (?,?,?)',ids).fetchone():raise Hold('REPLAYED_RECEIPT')
   payload=self.signable(epoch,challenge,size,root,proof,new_root)
   for name,_,sig in votes:
    try:Ed25519PublicKey.from_public_bytes(self.keys[name]).verify(sig,payload)
    except (InvalidSignature,ValueError,TypeError):raise Hold('BAD_SIGNATURE') from None
   for rid in ids:db.execute('INSERT INTO used VALUES(?)',(rid,))
   nxt=H(dict(domain='WAG081.rotate',epoch=epoch+1,prev=challenge,root=new_root))
   db.execute('UPDATE state SET epoch=?,size=?,root=?,challenge=?',(epoch+1,proof.new_size,new_root,nxt))
   self.event(db,dict(kind='advance',epoch=epoch+1,root=new_root,receipt_ids=sorted(ids)))
   db.execute('COMMIT');return 'LOCAL_ATOMIC_ADVANCED'
  except BaseException:
   if db.in_transaction:db.execute('ROLLBACK')
   raise
  finally:db.close()
