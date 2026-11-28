"""G122 append-only inventory transition; observation only. .dlw"""
import hashlib,json,re,importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('manifest',Path(__file__).with_name('g121-manifest.py')); M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
def validate(m):
    if type(m) is not dict or set(m)!={'ledger','objects'}: raise ValueError('schema')
    if not isinstance(m['ledger'],str) or not re.fullmatch('[0-9a-f]{64}',m['ledger']) or m['ledger']=='0'*64: raise ValueError('ledger')
    rows=m['objects']
    if type(rows) is not list or len(rows)>M.MAX_FILES: raise ValueError('count')
    last='';total=0
    for row in rows:
        if type(row) is not list or len(row)!=2: raise ValueError('row')
        h,n=row
        if not isinstance(h,str) or not re.fullmatch('[0-9a-f]{64}',h) or h<=last or type(n) is not int or not 0<n<=M.LIMIT: raise ValueError('entry')
        last=h;total+=n
        if total>M.MAX_BYTES: raise ValueError('bytes')
    return dict(rows)
def advance(root,prior,pin):
    old=validate(prior)
    if M.fingerprint(prior)!=pin: raise ValueError('predecessor pin')
    current=M.snapshot(root,prior['ledger']); new=validate(current)
    if any(new.get(h)!=n for h,n in old.items()): raise ValueError('historical omission')
    claim={'ledger':prior['ledger'],'previous':pin,'current':M.fingerprint(current),'added':[[h,n] for h,n in new.items() if h not in old]}
    digest=hashlib.sha256(b'G122\0'+json.dumps(claim,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return dict(claim=claim,manifest=current,transition=digest,authority='HOLD')
