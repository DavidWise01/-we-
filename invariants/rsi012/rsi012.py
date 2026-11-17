"""RSI-012: authenticated prefix preservation using a complete verified snapshot."""
import json
from rsi011 import Anchor,canonical

class Lineage(Anchor):
 def publish(self,h,s,book):
  self.authenticate(h,s)
  self.db.execute('BEGIN IMMEDIATE')
  try:
   old,held=self.db.execute('SELECT head,held FROM state').fetchone()
   if held:raise ValueError('HOLD')
   if book.stream!=self.stream or book.witnesses!=self.keys:raise ValueError('wrong book')
   book.db.execute('BEGIN')
   try:
    if not book.verify() or book.head()!=h:raise ValueError('invalid proposed history')
    if old:
     o=json.loads(old)
     if h['keys']!=o['keys']:raise ValueError('key change')
     for key,table,col in [('frames','frames','t'),('experience','signed','seq')]:
      n,hash_=o[key]
      if h[key][0]<n:raise ValueError('rollback')
      if n>=0:
       row=book.db.execute(f'SELECT hash FROM {table} WHERE {col}=?',(n,)).fetchone()
       if row!=(hash_,):raise ValueError('prefix fork')
    self.db.execute('UPDATE state SET head=?,signatures=?',(canonical(h),canonical(s)))
    self.db.commit()
   finally:book.db.rollback()
  except BaseException:
   if self.db.in_transaction:self.db.rollback()
   raise
