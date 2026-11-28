"""Cooperating Linux writers; no automatic promotion. .dlw"""
import os,fcntl,importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('recovery',Path(__file__).with_name('g107-recovery.py')); M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
T=M.T

def ingest(path,lp,pp,root,objects,ref,sig,key,pin,ledger,legacy_sig,graph,witnesses,roster,roster_pin):
    # Lock directory inode, not a replaceable lock file. All writers must cooperate.
    fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        fcntl.flock(fd,fcntl.LOCK_EX)
        T.recover(root,objects,ref,sig,key,pin,ledger)
        with open(path,'rb') as f: raw=f.read(T.S.LIMIT+1)
        if not 0<len(raw)<=T.S.LIMIT: raise ValueError('archive bound')
        archive=T.S.put(objects,raw)
        if (Path(root)/f"{ref['count']:04x}.json").exists():
            x=M.classify(root,objects,ref,sig,key,pin,ledger,archive,lp,pp)
            return dict(x,state='RETRY_COMPLETE' if x['state']=='COMPLETE_UNPINNED' else 'SUCCESSOR_OCCUPIED',archive=archive)
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'snapshot.zip';p.write_bytes(raw)
            x=T.ingest(p,lp,pp,root,objects,ref,sig,key,pin,ledger,legacy_sig,graph,witnesses,roster,roster_pin)
        return dict(x,state='PUBLISHED_UNPINNED' if x['candidate'] else 'NO_CANDIDATE',archive=archive)
    finally:
        os.close(fd)
