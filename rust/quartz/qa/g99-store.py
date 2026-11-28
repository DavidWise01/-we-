"""Single trusted writer, externally pinned prefix; no automatic promotion. .dlw"""
import importlib.util,json,os,stat
from pathlib import Path
s=importlib.util.spec_from_file_location('q',Path(__file__).with_name('g94-quarantine.py')); Q=importlib.util.module_from_spec(s);s.loader.exec_module(Q)
def syncdir(root):
    fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
def recover(root,count,head):
    if type(count) is not int or not 0<=count<=Q.MAX: raise ValueError('count')
    rows=[]
    for i in range(count):
        p=Path(root)/f'{i:04x}.json'
        fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        with os.fdopen(fd,'rb') as f:
            if not stat.S_ISREG(os.fstat(f.fileno()).st_mode): raise ValueError('file type')
            b=f.read(8193)
        if len(b)>8192: raise ValueError('size')
        rows.append(json.loads(b))
    Q.verify(rows,head);return rows

def publish(root,count,head,subject,streams):
    root=Path(root); rows=recover(root,count,head)
    new,candidate=Q.append(rows,head,subject,streams)
    b=json.dumps(new[-1],sort_keys=True,separators=(',',':')).encode()+b'\n'
    stage=root/f'{count:04x}.stage'; final=root/f'{count:04x}.json'
    with stage.open('xb') as f: f.write(b);f.flush();os.fsync(f.fileno())
    os.link(stage,final);syncdir(root)
    # Stage retained; trusted writer must not modify either hard-link alias.
    return candidate
