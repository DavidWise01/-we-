import importlib.util,pathlib,tempfile,json,zipfile,os
P=pathlib.Path(__file__).parent
def load(n):
 s=importlib.util.spec_from_file_location(n,P/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=load('g99-store'); A=load('g98-adapter'); Q=M.Q; H=A.I.sha
results=[]
def record(name,kind,ok):
 assert ok,name
 results.append({'case':name,'classification':kind})
def rejects(fn):
 try:fn()
 except (ValueError,OSError):return True
 return False
S='a'*64; streams=dict.fromkeys(Q.TARGETS,'b'*64); clash=dict(streams,chromium='c'*64)
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d);h=M.publish(p,0,Q.ZERO,S,streams);h2=M.publish(p,1,h,S,clash);h3=M.publish(p,2,h2,S,streams)
 record('sticky quarantine','guard',Q.verify(M.recover(p,3,h3),h3)['blocked']==[S])
 record('new head rejects old prefix','guard',rejects(lambda:M.recover(p,1,h3)))
 record('stale supplied pin accepts old prefix','gap',len(M.recover(p,1,h))==1)
 (p/'0003.stage').write_bytes(b'partial')
 record('abandoned stage blocks retry','gap',rejects(lambda:M.publish(p,3,h3,S,streams)))
 record('stage and final share inode','gap',os.stat(p/'0000.stage').st_ino==os.stat(p/'0000.json').st_ino)
 (p/'0000.stage').write_text('{}')
 record('alias mutation detected on recovery','guard',rejects(lambda:M.recover(p,3,h3)))
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)/'a.zip';lock=b'fake lock';pin=H(lock);proc=H(b'procedure');sub=A.A.subject(H(A.I.REV.encode()),pin,proc);output=b'G75\0fake';roots=[H(bytes([i])) for i in range(1,4)];graph={r:[] for r in roots};ws=[dict(root=r,subject=sub,observation=H(r.encode()),result=H(output)) for r in roots]
 def make(change=lambda d:None):
  data={k:b'0' if k.endswith('.exit') or k=='current-suite-exit.txt' else b'placeholder' for k in A.I.REQUIRED};data.update({'source.txt':A.I.REV.encode(),'Cargo.lock':lock,'procedure.bin':b'procedure'});data.update({k+'.bin':output for k in A.R.TARGETS});data.update({k+'.exit':b'0' for k in A.R.TARGETS});change(data);data['SHA256SUMS']=''.join(H(v)+'  '+k+'\n' for k,v in sorted(data.items())).encode()
  with zipfile.ZipFile(p,'w') as z:
   for k,v in data.items():z.writestr(k,v)
 def run(g=graph):return A.ingest(p,pin,proc,[],Q.ZERO,g,ws)
 make();x=run();record('fabricated self-consistent evidence yields declared agreement','gap',x['witness']['state']=='DECLARED_AGREEMENT');record('authority remains held','guard',x['authority']=='HOLD')
 record('declared shared ancestry rejected','guard',run({roots[0]:[],roots[1]:[roots[0]],roots[2]:[]})['witness']['state']=='SHARED_ANCESTRY')
 make(lambda d:d.update({'chromium.bin':b'G75\0clash','chromium.exit':b'1'}));x=run();record('failed parity exit masks conflict','gap',not x['records'] and x['reconciliation']['state']=='EXECUTION_FAILURE_DECLARED')
 make(lambda d:d.update({'chromium.bin':b'G75\0clash','check.exit':b'1'}));record('native failure retains conflict','guard',run()['witness']['state']=='QUARANTINED')
 make(lambda d:d.update({'procedure.bin':b'changed'}));record('procedure substitution rejected','guard',rejects(run))
print(json.dumps({'generation':100,'cases':results,'guards':sum(x['classification']=='guard' for x in results),'gaps':sum(x['classification']=='gap' for x in results),'authority':'HOLD'},indent=2))
