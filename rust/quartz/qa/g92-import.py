import argparse, hashlib, json, re, stat, zipfile
from pathlib import Path
REV='8b7bca2810ca1fa6901c7120ac0cd4d41e91aaa0'
LIMIT=64*1024*1024
SUITES=('lib','g64_integrated','g77_reference','g82_reconciled')
REQUIRED={'source.txt','source-tree.txt','platform.txt','Cargo.lock','check.log','check.exit','rustc.log','cargo.log','metadata.log','resolve.log','current-suite-exit.txt'}
REQUIRED.update({s+ext for s in SUITES for ext in ('.log','.exit')})
def sha(b): return hashlib.sha256(b).hexdigest()
def inspect(path, lock_pin=None):
 if Path(path).stat().st_size>LIMIT: raise ValueError('archive bound')
 with zipfile.ZipFile(path) as z:
  infos=z.infolist(); names=[i.filename for i in infos]
  if len(names)>64 or len(set(names))!=len(names): raise ValueError('member count or duplicate')
  if sum(i.file_size for i in infos)>LIMIT: raise ValueError('expanded size bound')
  for i in infos:
   if not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',i.filename) or i.filename in ('.','..') or stat.S_IFMT(i.external_attr>>16) not in (0,stat.S_IFREG) or i.flag_bits&1: raise ValueError('unsafe member')
  if not REQUIRED|{'SHA256SUMS'} <= set(names): raise ValueError('missing evidence')
  data={i.filename:z.read(i) for i in infos}
 manifest={}
 for line in data['SHA256SUMS'].decode('ascii').splitlines():
  m=re.fullmatch(r'([a-f0-9]{64}) [ *](?:\./)?([A-Za-z0-9_.-]+)',line)
  if not m or m[2] in manifest: raise ValueError('invalid checksum manifest')
  manifest[m[2]]=m[1]
 if set(manifest)!=set(data)-{'SHA256SUMS'}: raise ValueError('checksum coverage')
 if any(sha(data[n])!=h for n,h in manifest.items()): raise ValueError('checksum mismatch')
 if data['source.txt'].strip()!=REV.encode(): raise ValueError('source revision mismatch')
 lock=sha(data['Cargo.lock'])
 if lock_pin is not None and lock!=lock_pin: raise ValueError('lock pin mismatch')
 exits={s:int(data[s+'.exit'].strip()) for s in ('check',)+SUITES}
 if any(not 0<=v<=255 for v in exits.values()): raise ValueError('exit range')
 if int(data['current-suite-exit.txt'].strip())!=int(any(exits[s]!=0 for s in SUITES)): raise ValueError('suite exit inconsistency')
 return {'integrity':'consistent submitted bytes','lock_sha256':lock,'lock_pin_matched':lock_pin is not None,'declared_exits':exits,'authority':'HOLD'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('archive');p.add_argument('--lock-pin');a=p.parse_args();print(json.dumps(inspect(a.archive,a.lock_pin),indent=2))
