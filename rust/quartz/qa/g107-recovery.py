"""G107 read-only candidate classification, never promotes custody. .dlw"""
import io,json,zipfile,tempfile,importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('transaction',Path(__file__).with_name('g106-transaction.py')); T=importlib.util.module_from_spec(s);s.loader.exec_module(T)
Q=T.Q; S=T.S; A=T.A; W=T.W; C=T.C

def classify(root,objects,ref,sig,key,pin,ledger,archive,lp,pp):
    rows=T.recover(root,objects,ref,sig,key,pin,ledger)
    def out(state, candidate=None): return {'state':state,'candidate':candidate,'authority':'HOLD','trusted_count':len(rows)}
    if len(rows)>=Q.MAX:return out('CAPACITY')
    final=Path(root)/f"{len(rows):04x}.json"
    try: raw=S.recover(objects,archive)
    except FileNotFoundError: return out('RAW_MISSING')
    except (ValueError,OSError): return out('RAW_INVALID')
    try:
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'archive.zip';p.write_bytes(raw)
            imp=A.ingest(p,lp,pp,rows,ref['head'],{},[])
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            outputs={k:z.read(k+'.bin') for k in A.R.TARGETS if k+'.bin' in z.namelist()}
            exits={k:int(z.read(k+'.exit').strip()) for k in A.R.TARGETS if k+'.exit' in z.namelist()}
            obs=W.observe(A.I.REV,z.read('Cargo.lock'),lp,outputs,exits,imp['subject'],rows,ref['head'])
        if len(obs['records'])!=len(rows)+1:return out('NO_RECORD_EXPECTED')
        head=obs['head']
        try: actual=C.M.recover(root,len(rows)+1,head)
        except FileNotFoundError:return out('RECORD_MISSING')
        if actual!=obs['records']:return out('RECORD_INVALID')
        link={'previous':ref['evidence'],'record':head,'archive':archive,'binding':S.binding(head,archive),'lock':lp,'procedure':pp}
        encoded=C.canonical(link); evidence=S.digest(encoded)
        try: stored=S.recover(objects,evidence)
        except FileNotFoundError:return out('LINK_MISSING')
        if stored!=encoded:return out('LINK_INVALID')
        return out('COMPLETE_UNPINNED',dict(ledger=ledger,count=len(rows)+1,head=head,evidence=evidence))
    except (ValueError,OSError,KeyError,TypeError,zipfile.BadZipFile):return out('CANDIDATE_INVALID')
