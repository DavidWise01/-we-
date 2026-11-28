"""Signed admission for composite candidates; cooperating writers only. .dlw"""
import os,fcntl,io,zipfile,tempfile,importlib.util
from pathlib import Path

def load(n):
    s=importlib.util.spec_from_file_location(n,Path(__file__).with_name(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
T=load('g106-transaction'); B=load('g110-budget'); K=load('g113-policy')
S,Q,A,W,C=T.S,T.Q,T.A,T.W,T.C

def ingest(path,lp,pp,root,objects,ref,sig,key,pin,ledger,legacy_sig,graph,witnesses,roster,roster_pin,policy,policy_sig,policy_key,policy_pin,minimum):
    cfg=K.verify(policy,policy_sig,policy_key,policy_pin,ledger,minimum)
    if Path(root).resolve()==Path(objects).resolve(): raise ValueError('distinct directories required')
    fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        fcntl.flock(fd,fcntl.LOCK_EX)
        od=os.open(objects,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            fcntl.flock(od,fcntl.LOCK_EX)
            rows=T.recover(root,objects,ref,sig,key,pin,ledger)
            legacy={k:ref[k] for k in ('ledger','count','head')}; legacy_pin=C.fingerprint(legacy,legacy_sig)
            C.recover(root,legacy,legacy_sig,key,legacy_pin,ledger)
            with open(path,'rb') as f: raw=f.read(S.LIMIT+1)
            if not 0<len(raw)<=S.LIMIT: raise ValueError('archive bound')
            archive=S.digest(raw)
            with tempfile.TemporaryDirectory() as d:
                p=Path(d)/'archive.zip';p.write_bytes(raw)
                imp=A.ingest(p,lp,pp,rows,ref['head'],{},[])
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                outputs={k:z.read(k+'.bin') for k in A.R.TARGETS if k+'.bin' in z.namelist()}
                exits={k:int(z.read(k+'.exit').strip()) for k in A.R.TARGETS if k+'.exit' in z.namelist()}
                obs=W.observe(A.I.REV,z.read('Cargo.lock'),lp,outputs,exits,imp['subject'],rows,ref['head'])
            state='NOT_EVALUATED'; candidate=None; pending={archive:raw}
            if imp['subject'] in obs['blocked']: state='QUARANTINED'
            elif any(imp['import']['declared_exits'].values()): state='NATIVE_FAILURE_DECLARED'
            elif obs['execution']=='CONSISTENT_SUBMISSION': state=W.authenticate(imp['subject'],graph,witnesses,roster,roster_pin,obs['blocked'],S.digest(outputs['native']))['state']
            if len(obs['records'])>len(rows):
                head=obs['head']; link=C.canonical(dict(previous=ref['evidence'],record=head,archive=archive,binding=S.binding(head,archive),lock=lp,procedure=pp)); evidence=S.digest(link);pending[evidence]=link
                if (Path(root)/f"{ref['count']:04x}.json").exists(): raise ValueError('occupied successor')
            used,count=B.inventory(objects); extra=[]
            for h,b in pending.items():
                if (Path(objects)/h).exists():
                    if S.recover(objects,h)!=b: raise ValueError('collision')
                else: extra.append(b)
            if extra and (used+sum(map(len,extra))>cfg['bytes'] or count+len(extra)>cfg['files']):
                return dict(state='CAPACITY_HOLD',candidate=None,archive_sha256=archive,authority='HOLD')
            for b in extra:S.put(objects,b)
            if len(obs['records'])>len(rows):
                candidate=C.publish(root,legacy,legacy_sig,key,legacy_pin,ledger,imp['subject'],obs['records'][-1]['streams'])
                if candidate['head']!=head:raise ValueError('candidate mismatch')
                candidate=dict(candidate,evidence=evidence)
            return dict(state='STORED',candidate=candidate,witness=state,execution=obs['execution'],comparison=obs['comparison'],archive_sha256=archive,authority='HOLD')
        finally: os.close(od)
    finally: os.close(fd)
