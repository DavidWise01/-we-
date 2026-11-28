"""Bounded logical-byte admission for cooperating writers. .dlw"""
import os, re, fcntl, stat, importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('store',Path(__file__).with_name('g105-store.py')); S=importlib.util.module_from_spec(s);s.loader.exec_module(S)
def inventory(root):
    total=0; count=0
    for p in Path(root).iterdir():
        st=p.lstat()
        if not stat.S_ISREG(st.st_mode): raise ValueError('unexpected file type')
        if not (re.fullmatch('[0-9a-f]{64}',p.name) or p.name.startswith('.g105-')): raise ValueError('unexpected name')
        total+=st.st_size; count+=1
    return total,count

def admit(root,raw,budget,max_files):
    if type(budget) is not int or budget<0 or type(max_files) is not int or max_files<1: raise ValueError('budget')
    if not isinstance(raw,bytes) or not 0<len(raw)<=S.LIMIT: raise ValueError('object bound')
    fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        fcntl.flock(fd,fcntl.LOCK_EX)
        used,count=inventory(root); key=S.digest(raw)
        def out(state): return dict(state=state,used=used,count=count,digest=key,authority='HOLD')
        if (Path(root)/key).exists():
            if S.recover(root,key)!=raw: raise ValueError('collision')
            return out('DEDUPLICATED')
        if used+len(raw)>budget or count+1>max_files:return out('CAPACITY_HOLD')
        S.put(root,raw)
        used,count=inventory(root)
        return out('STORED')
    finally:os.close(fd)
