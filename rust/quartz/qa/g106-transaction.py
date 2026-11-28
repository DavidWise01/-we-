"""G106 signed composite reference, evidence-first candidate publication. .dlw"""
import io,json,tempfile,zipfile,importlib.util
from pathlib import Path

def load(n):
    s=importlib.util.spec_from_file_location(n,Path(__file__).with_name(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
P=load('g103-pipeline'); S=load('g105-store'); C=P.C; Q=C.Q; A=P.A; W=P.W

def message(ref): return b'G106\0'+C.canonical(ref)
def fingerprint(ref,sig): return S.digest(message(ref)+sig)
def recover(root,objects,ref,sig,key,pin,ledger):
    if set(ref)!={'ledger','count','head','evidence'} or ref['ledger']!=ledger or not Q.valid_hash(ledger): raise ValueError('reference')
    if fingerprint(ref,sig)!=pin: raise ValueError('pin')
    C.Ed25519PublicKey.from_public_bytes(key).verify(sig,message(ref))
    rows=C.M.recover(root,ref['count'],ref['head']); h=ref['evidence']; links=[]
    for row in reversed(rows):
        link=json.loads(S.recover(objects,h))
        if set(link)!={'previous','record','archive','binding','lock','procedure'} or link['record']!=row['digest'] or link['binding']!=S.binding(row['digest'],link['archive']): raise ValueError('binding')
        links.append(link); h=link['previous']
    if h!=Q.ZERO: raise ValueError('genesis')
    links.reverse()
    for i,link in enumerate(links):
        raw=S.recover(objects,link['archive'])
        prev=rows[i-1]['digest'] if i else Q.ZERO
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'archive.zip';p.write_bytes(raw)
            imported=A.ingest(p,link['lock'],link['procedure'],rows[:i],prev,{},[])
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            outputs={k:z.read(k+'.bin') for k in A.R.TARGETS if k+'.bin' in z.namelist()}
            exits={k:int(z.read(k+'.exit').strip()) for k in A.R.TARGETS if k+'.exit' in z.namelist()}
            obs=W.observe(A.I.REV,z.read('Cargo.lock'),link['lock'],outputs,exits,imported['subject'],rows[:i],prev)
        if len(obs['records'])!=i+1 or obs['records'][-1]!=rows[i]: raise ValueError('replay mismatch')
    return rows

def ingest(path,lp,pp,root,objects,ref,sig,key,pin,ledger,legacy_sig,graph,witnesses,roster,roster_pin):
    recover(root,objects,ref,sig,key,pin,ledger)
    legacy={k:ref[k] for k in ('ledger','count','head')}
    legacy_pin=C.fingerprint(legacy,legacy_sig)
    C.recover(root,legacy,legacy_sig,key,legacy_pin,ledger)
    with open(path,'rb') as f: raw=f.read(S.LIMIT+1)
    archive=S.put(objects,raw)
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'archive.zip';p.write_bytes(raw)
        out=P.ingest(p,lp,pp,root,legacy,legacy_sig,key,legacy_pin,ledger,graph,witnesses,roster,roster_pin)
    if out['archive_sha256']!=archive: raise ValueError('archive mismatch')
    candidate=out['candidate']
    if candidate is not None:
        link={'previous':ref['evidence'],'record':candidate['head'],'archive':archive,'binding':S.binding(candidate['head'],archive),'lock':lp,'procedure':pp}
        out['candidate']=dict(candidate,evidence=S.put(objects,C.canonical(link)))
    return out
