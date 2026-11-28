"""G98 procedure-bound submission adapter; no authorization. .dlw"""
import hashlib, importlib.util, io, tempfile, zipfile, copy
from pathlib import Path

def load(name):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name+'.py'))
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
I,R,Q,A=map(load,('g92-import','g93-reconcile','g94-quarantine','g95-ancestry'))
def ingest(path,lock_pin,procedure_pin,records,head,graph,witnesses):
    Q.verify(records,head)
    if not A.h(lock_pin) or not A.h(procedure_pin): raise ValueError('missing trusted pin')
    with open(path,'rb') as f: raw=f.read(I.LIMIT+1)
    if len(raw)>I.LIMIT: raise ValueError('archive bound')
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'snapshot.zip'; p.write_bytes(raw); imported=I.inspect(p,lock_pin)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        outputs={k:z.read(k+'.bin') for k in R.TARGETS if k+'.bin' in z.namelist()}
        exits={k:int(z.read(k+'.exit').strip()) for k in R.TARGETS if k+'.exit' in z.namelist()}
        lock=z.read('Cargo.lock')
        if 'procedure.bin' not in z.namelist() or I.sha(z.read('procedure.bin'))!=procedure_pin: raise ValueError('procedure pin mismatch')
    subject=A.subject(hashlib.sha256(I.REV.encode()).hexdigest(),lock_pin,procedure_pin)
    rec=R.reconcile(I.REV,lock,lock_pin,outputs,exits)
    new=copy.deepcopy(records); new_head=head
    if 'sha256' in rec: new,new_head=Q.append(new,head,subject,rec['sha256'])
    blocked=Q.verify(new,new_head)['blocked']
    witness={'state':'NOT_EVALUATED','authority':'HOLD'}
    if rec['state'] in ('CONSISTENT_SUBMISSION','CONTRADICTORY'):
        if subject in blocked: witness={'state':'QUARANTINED','authority':'HOLD'}
        elif any(imported['declared_exits'].values()): witness={'state':'NATIVE_FAILURE_DECLARED','authority':'HOLD'}
        elif any(w.get('result')!=rec['sha256']['native'] for w in witnesses): witness={'state':'RESULT_MISMATCH','authority':'HOLD'}
        else: witness=A.adjudicate(subject,graph,witnesses,blocked)
    return {'subject':subject,'import':imported,'reconciliation':rec,'witness':witness,'records':new,'head':new_head,'authority':'HOLD','archive_sha256':I.sha(raw)}
