"""Signed reference against separately retained current digest; trusted directory. .dlw"""
import hashlib,json,os,tempfile,importlib.util
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
s=importlib.util.spec_from_file_location('store',Path(__file__).with_name('g99-store.py')); M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
Q=M.Q
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def message(ref): return b'G102\0'+canonical(ref)
def fingerprint(ref,sig): return hashlib.sha256(message(ref)+sig).hexdigest()
def recover(root,ref,sig,key,expected,ledger):
    if set(ref)!={'ledger','count','head'} or ref['ledger']!=ledger or not Q.valid_hash(ledger): raise ValueError('ledger')
    if fingerprint(ref,sig)!=expected: raise ValueError('reference pin mismatch')
    Ed25519PublicKey.from_public_bytes(key).verify(sig,message(ref))
    return M.recover(root,ref['count'],ref['head'])
def publish(root,ref,sig,key,expected,ledger,subject,streams):
    rows=recover(root,ref,sig,key,expected,ledger)
    new,head=Q.append(rows,ref['head'],subject,streams)
    root=Path(root); final=root/f"{ref['count']:04x}.json"
    b=canonical(new[-1])+b'\n'
    fd,stage=tempfile.mkstemp(prefix='.g102-',dir=root)
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(b);f.flush();os.fsync(f.fileno())
        os.link(stage,final)
    finally:
        os.unlink(stage)
    M.syncdir(root)
    return {'ledger':ledger,'count':ref['count']+1,'head':head}
