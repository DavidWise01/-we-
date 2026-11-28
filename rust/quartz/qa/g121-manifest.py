"""G121 pinned addressed-object inventory; observation only. .dlw"""
import os, re, stat, hashlib, json, fcntl
MAX_FILES=65536
MAX_BYTES=16*1024**3
LIMIT=64*1024**2

def snapshot(root,ledger):
    if not isinstance(ledger,str) or not re.fullmatch('[0-9a-f]{64}',ledger) or ledger=='0'*64: raise ValueError('ledger')
    fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        fcntl.flock(fd,fcntl.LOCK_SH)
        rows=[]; count=total=0
        with os.scandir(fd) as entries:
            for e in entries:
                count+=1
                if count>MAX_FILES: raise ValueError('entry bound')
                addressed=re.fullmatch('[0-9a-f]{64}',e.name) is not None
                if not addressed and not e.name.startswith('.g105-'): raise ValueError('name')
                with os.fdopen(os.open(e.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd),'rb') as f:
                    st=os.fstat(f.fileno())
                    if not stat.S_ISREG(st.st_mode) or st.st_size>LIMIT: raise ValueError('type or size')
                    total+=st.st_size
                    if total>MAX_BYTES: raise ValueError('scan bound')
                    if not addressed: continue
                    h=hashlib.sha256(); n=0
                    while chunk:=f.read(1024**2):
                        n+=len(chunk)
                        if n>st.st_size: raise ValueError('size changed')
                        h.update(chunk)
                    if n!=st.st_size or not n or h.hexdigest()!=e.name: raise ValueError('content mismatch')
                    rows.append([e.name,n])
        return {'ledger':ledger,'objects':sorted(rows)}
    finally:os.close(fd)

def fingerprint(manifest):
    return hashlib.sha256(b'G121\0'+json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def verify(root,ledger,pin):
    if not isinstance(pin,str) or not re.fullmatch('[0-9a-f]{64}',pin): raise ValueError('pin')
    m=snapshot(root,ledger)
    if fingerprint(m)!=pin: raise ValueError('inventory commitment mismatch')
    return {'manifest':m,'authority':'HOLD'}
