"""G116 account unique inode bytes and verify every addressed object under the cooperative admission lock. .dlw"""
import hashlib, os, re, stat
from pathlib import Path
LIMIT=64*1024*1024
MAX_FILES=65536
MAX_BYTES=16*1024**3

def inventory(root):
    total=count=0
    seen={}
    for p in Path(root).iterdir():
        count+=1
        if count>MAX_FILES: raise ValueError('inventory count bound')
        addressed=re.fullmatch('[0-9a-f]{64}',p.name) is not None
        if not addressed and not p.name.startswith('.g105-'): raise ValueError('unexpected name')
        fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        with os.fdopen(fd,'rb') as f:
            st=os.fstat(f.fileno())
            if not stat.S_ISREG(st.st_mode) or st.st_size>LIMIT: raise ValueError('object type or size')
            identity=(st.st_dev,st.st_ino)
            if identity in seen and seen[identity]!=st.st_size: raise ValueError('inode size changed')
            if identity not in seen:
                seen[identity]=st.st_size
                total+=st.st_size
            if total>MAX_BYTES: raise ValueError('inventory byte bound')
            if addressed:
                h=hashlib.sha256(); n=0
                while chunk:=f.read(1024*1024):
                    n+=len(chunk)
                    if n>LIMIT: raise ValueError('object bound')
                    h.update(chunk)
                if n!=st.st_size or n==0 or h.hexdigest()!=p.name: raise ValueError('inventory content mismatch')
    return total,count
