"""G105 content-addressed raw bytes; trusted directory, no authority. .dlw"""
import hashlib, os, re, stat, tempfile
from pathlib import Path
LIMIT=64*1024*1024

def digest(raw): return hashlib.sha256(raw).hexdigest()
def recover(root,key):
    if not isinstance(key,str) or not re.fullmatch('[0-9a-f]{64}',key): raise ValueError('digest')
    fd=os.open(Path(root)/key,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode): raise ValueError('not regular')
        raw=f.read(LIMIT+1)
    if len(raw)>LIMIT or digest(raw)!=key: raise ValueError('content mismatch')
    return raw

def put(root,raw):
    if not isinstance(raw,bytes) or not 0<len(raw)<=LIMIT: raise ValueError('size/type')
    root=Path(root); key=digest(raw); final=root/key
    fd,stage=tempfile.mkstemp(prefix='.g105-',dir=root)
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(raw); f.flush(); os.fsync(f.fileno())
        try: os.link(stage,final)
        except FileExistsError:
            if recover(root,key)!=raw: raise ValueError('collision')
    finally: os.unlink(stage)
    d=os.open(root,os.O_RDONLY|os.O_DIRECTORY)
    try: os.fsync(d)
    finally: os.close(d)
    return key

def binding(record_digest,archive_digest):
    for x in (record_digest,archive_digest):
        if not isinstance(x,str) or not re.fullmatch('[0-9a-f]{64}',x): raise ValueError('digest')
    return digest(b'G105\0'+bytes.fromhex(record_digest)+bytes.fromhex(archive_digest))
