"""WAG-120: three durable witness journals; single-process reference."""
import sqlite3,json,hashlib
from pathlib import Path
from contextlib import closing

def encode(x): return json.dumps(x,sort_keys=True,separators=(',',':'))
def digest(x): return hashlib.sha256(encode(x).encode()).hexdigest()
GENESIS={'seq':0,'balances':[156,0,0],'pending':{},'delivered':[]}
class Journal:
 def __init__(self,path):
  self.path=Path(path)
  with closing(self.open()) as c:
   c.execute('CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY, body TEXT NOT NULL)');c.commit()
 def open(self):
  c=sqlite3.connect(self.path);c.execute('PRAGMA synchronous=FULL');return c
 def read(self):
  with closing(self.open()) as c:return [json.loads(r[0]) for r in c.execute('SELECT body FROM events ORDER BY seq')]
 def append(self,e):
  with closing(self.open()) as c:
   c.execute('BEGIN IMMEDIATE'); rows=[json.loads(r[0]) for r in c.execute('SELECT body FROM events ORDER BY seq')]
   if len(rows)>=e['seq']:
    if rows[e['seq']-1]!=e:raise ValueError('fork')
    return
   if len(rows)!=e['seq']-1 or e['prev']!=digest(rows[-1] if rows else GENESIS):raise ValueError('gap')
   c.execute('INSERT INTO events VALUES (?,?)',(e['seq'],encode(e)));c.commit()

def apply(s,e):
 s=json.loads(encode(s));p=e['packet'];kind=e['kind']
 if e['seq']!=s['seq']+1:raise ValueError('sequence')
 if kind=='send':
  a,b,q=p['src'],p['dst'],p['q'];pid=p['id']
  if type(a)!=int or not 0<=a<3 or b!=(a+1)%3 or type(q)!=int or q<=0 or q>s['balances'][a] or pid in s['pending'] or pid in s['delivered']:raise ValueError('send')
  s['balances'][a]-=q;s['pending'][pid]=p
 elif kind=='receive':
  if s['pending'].get(p['id'])!=p:raise ValueError('receipt')
  s['balances'][p['dst']]+=p['q'];del s['pending'][p['id']];s['delivered'].append(p['id'])
 else:raise ValueError('kind')
 s['seq']=e['seq'];return s
class Mesh:
 def __init__(self,paths):
  if len(paths)!=3 or len({str(Path(p).resolve()) for p in paths})!=3:raise ValueError('distinct paths')
  self.j=[Journal(p) for p in paths]
 def inspect(self):
  logs=[j.read() for j in self.j];s=json.loads(encode(GENESIS));prev=digest(GENESIS)
  for es in zip(*logs):
   if not es[0]==es[1]==es[2]:raise ValueError('fork')
   e=es[0]
   if e['prev']!=prev:raise ValueError('chain')
   s=apply(s,e);prev=digest(e)
  if len({len(x) for x in logs})!=1:raise ValueError('partial publication')
  return s,prev
 def repair(self):
  logs=[j.read() for j in self.j];longest=max(logs,key=len);s=json.loads(encode(GENESIS));prev=digest(GENESIS)
  if any(x!=longest[:len(x)] for x in logs):raise ValueError('fork')
  # A partial suffix is not a commit. Explicit administrative replay only.
  for e in longest:
   if e['prev']!=prev:raise ValueError('chain')
   s=apply(s,e);prev=digest(e)
  for j,log in zip(self.j,logs):
   for e in longest[len(log):]:j.append(e)
  return self.inspect()[0]
 def submit(self,kind,packet,stop_after=3):
  s,prev=self.inspect();e={'seq':s['seq']+1,'prev':prev,'kind':kind,'packet':packet};apply(s,e)
  for j in self.j[:stop_after]:j.append(e)
  return 'COMMITTED' if stop_after==3 else 'HOLD_PARTIAL'
 def total(self):
  s,_=self.inspect();return sum(s['balances'])+sum(p['q'] for p in s['pending'].values())
