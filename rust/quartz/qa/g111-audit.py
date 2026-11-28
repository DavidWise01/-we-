"""G111 adversarial diagnostics; guards and gaps are distinct. .dlw"""
import importlib.util, tempfile, pathlib, json, multiprocessing as mp, os
P=pathlib.Path(__file__).parent
def load(n):
    s=importlib.util.spec_from_file_location(n,P/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
B=load('g110-budget')
def worker(root,raw,barrier,q):
    barrier.wait(timeout=10)
    q.put(B.admit(root,raw,8,2)['state'])
def audit():
    results=[]
    def check(name,kind,ok):
        assert ok,name
        results.append(dict(case=name,classification=kind))
    def reject(fn):
        try:fn()
        except (ValueError,OSError):return True
        return False
    with tempfile.TemporaryDirectory() as d:
        ctx=mp.get_context('spawn');barrier=ctx.Barrier(2);q=ctx.Queue()
        ps=[ctx.Process(target=worker,args=(d,b'aaaaa',barrier,q)),ctx.Process(target=worker,args=(d,b'bbbbb',barrier,q))]
        for p in ps:p.start()
        for p in ps:p.join(20)
        assert all(p.exitcode==0 for p in ps)
        states=sorted(q.get(timeout=2) for _ in ps)
        check('concurrent admission respects shared budget','guard',states==['CAPACITY_HOLD','STORED'] and B.inventory(d)==(5,1))
        key=next(pathlib.Path(d).iterdir()).name;raw=B.S.recover(d,key)
        check('historical bytes survive rejected competitor','guard',raw in (b'aaaaa',b'bbbbb'))
        check('duplicate at capacity','guard',B.admit(d,raw,5,1)['state']=='DEDUPLICATED')
        B.S.put(d,b'outside')
        check('direct store bypasses admission','gap',B.inventory(d)[0]>8)
        check('caller can enlarge unsigned budget','gap',B.admit(d,b'new',100,10)['state']=='STORED')
        (pathlib.Path(d)/key).write_bytes(b'xxxxx')
        check('inventory does not authenticate stored contents','gap',B.inventory(d)[0]>0)
        check('corrupt object recovery rejected','guard',reject(lambda:B.S.recover(d,key)))
        check('corrupt object cannot be overwritten by duplicate','guard',reject(lambda:B.admit(d,raw,100,10)))
    with tempfile.TemporaryDirectory() as d:
        p=pathlib.Path(d);key=B.S.put(d,b'abc')
        os.link(p/key,p/'.g105-abandoned')
        check('hard-link alias double counted as logical bytes','gap',B.inventory(d)==(6,2))
        check('abandoned alias pressure blocks new object','guard',B.admit(d,b'x',6,3)['state']=='CAPACITY_HOLD')
        check('admission does not remove abandoned alias','guard',(p/'.g105-abandoned').exists())
    return dict(generation=111,results=results,guards=sum(x['classification']=='guard' for x in results),gaps=sum(x['classification']=='gap' for x in results),authority='HOLD')
if __name__=='__main__':print(json.dumps(audit(),indent=2))
