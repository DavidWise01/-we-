"""G103 integrated candidate publication; never advances custody. .dlw"""
import io,tempfile,zipfile
from pathlib import Path
import importlib.util

def load(n):
    s=importlib.util.spec_from_file_location(n,Path(__file__).with_name(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
A=load('g98-adapter'); W=load('g101-auth'); C=load('g102-custody')
def ingest(path,lock_pin,procedure_pin,root,ref,sig,key,expected,ledger,graph,witnesses,roster,roster_pin):
    rows=C.recover(root,ref,sig,key,expected,ledger)
    with open(path,'rb') as f: raw=f.read(A.I.LIMIT+1)
    if len(raw)>A.I.LIMIT: raise ValueError('archive bound')
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'snapshot.zip';p.write_bytes(raw)
        imported=A.ingest(p,lock_pin,procedure_pin,rows,ref['head'],{},[])
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        outputs={k:z.read(k+'.bin') for k in A.R.TARGETS if k+'.bin' in z.namelist()}
        exits={k:int(z.read(k+'.exit').strip()) for k in A.R.TARGETS if k+'.exit' in z.namelist()}
        lock=z.read('Cargo.lock')
    subject=imported['subject']
    observed=W.observe(A.I.REV,lock,lock_pin,outputs,exits,subject,rows,ref['head'])
    candidate=None
    if len(observed['records'])>len(rows):
        candidate=C.publish(root,ref,sig,key,expected,ledger,subject,observed['records'][-1]['streams'])
        if candidate['head']!=observed['head']: raise ValueError('candidate mismatch')
    state='NOT_EVALUATED'
    if subject in observed['blocked']: state='QUARANTINED'
    elif any(imported['import']['declared_exits'].values()): state='NATIVE_FAILURE_DECLARED'
    elif observed['execution']=='CONSISTENT_SUBMISSION':
        state=W.authenticate(subject,graph,witnesses,roster,roster_pin,observed['blocked'],A.I.sha(outputs['native']))['state']
    return {'subject':subject,'execution':observed['execution'],'comparison':observed['comparison'],'witness':state,'candidate':candidate,'authority':'HOLD','archive_sha256':A.I.sha(raw)}
