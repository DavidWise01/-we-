"""WAG-084: simulated durable signed anchor delivery; not real off-host delivery."""
import os, json, hashlib, tempfile
from pathlib import Path
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(x): return hashlib.sha256(canonical(x)).hexdigest()
def payload(epoch,root,challenge,host):
    return {'kind':'WAG084_DURABLE_ACK_V1','epoch':epoch,'root':root,'challenge':challenge,'host':host}

@dataclass(frozen=True)
class Remote:
    name:str
    domain:str
    key:object
    directory:Path
    def store(self,epoch,root,challenge,*,ack_only=False):
        p=payload(epoch,root,challenge,self.name)
        if not ack_only:
            self.directory.mkdir(parents=True,exist_ok=True)
            dest=self.directory/'checkpoint.json'
            fd,tmp=tempfile.mkstemp(dir=self.directory,prefix='.tmp')
            try:
                with os.fdopen(fd,'wb') as f:
                    f.write(canonical(p)); f.flush();os.fsync(f.fileno())
                os.replace(tmp,dest)
                dfd=os.open(self.directory,os.O_RDONLY)
                try:os.fsync(dfd)
                finally:os.close(dfd)
            finally:
                if os.path.exists(tmp):os.unlink(tmp)
        return {'payload':p,'signature':self.key.sign(canonical(p)).hex()}

class DeliveryGate:
    def __init__(self,remotes,epoch,root,challenge):
        self.remotes=tuple(remotes);self.epoch=epoch;self.root=root;self.challenge=challenge
        if len(self.remotes)!=3 or len({r.name for r in remotes})!=3 or len({r.domain for r in remotes})!=3 or any(not r.name or not r.domain for r in remotes):raise ValueError('three distinct declared hosts')
        self.used=set();self.log=[]
    def decision(self,acks,*,consume=False):
        if len(acks)!=3:return self._record('HOLD_MISSING_ACK')
        expected={r.name for r in self.remotes}
        if {a.get('payload',{}).get('host') for a in acks}!=expected:return self._record('HOLD_HOST_SET')
        for r in self.remotes:
            a=next(x for x in acks if x['payload']['host']==r.name)
            p=a['payload']
            if p!=payload(self.epoch,self.root,self.challenge,r.name):return self._record('HOLD_CONTEXT')
            try:r.key.public_key().verify(bytes.fromhex(a['signature']),canonical(p))
            except (ValueError,InvalidSignature,KeyError,TypeError):return self._record('HOLD_BAD_SIGNATURE')
            path=r.directory/'checkpoint.json'
            try:stored=json.loads(path.read_bytes())
            except (OSError,ValueError):return self._record('HOLD_NOT_DURABLE')
            if stored!=p:return self._record('HOLD_STORAGE_MISMATCH')
        receipt=digest(sorted((x['payload']['host'],x['signature']) for x in acks))
        if receipt in self.used:return self._record('HOLD_REPLAY')
        if consume:self.used.add(receipt)
        return self._record('LOCAL_DURABLE_ACK_QUORUM')
    def _record(self,result):
        r={'index':len(self.log),'prior':self.log[-1]['hash'] if self.log else '0'*64,'decision':result}
        r['hash']=digest(r);self.log.append(r);return result
    def audit_ok(self):
        return all(r['index']==i and r['prior']==(self.log[i-1]['hash'] if i else '0'*64) and r['hash']==digest({k:v for k,v in r.items() if k!='hash'}) for i,r in enumerate(self.log))
    def advance(self,epoch,root,challenge):
        if epoch<=self.epoch or challenge==self.challenge:raise ValueError('must advance epoch and challenge')
        self.epoch,self.root,self.challenge=epoch,root,challenge

def setup(base):
    return DeliveryGate([Remote('host-'+x,'domain-'+x,Ed25519PrivateKey.generate(),Path(base)/('host-'+x)) for x in 'ABC'],83,'root-83','challenge-83')

def demo(base):
    g=setup(base)
    a=[r.store(g.epoch,g.root,g.challenge) for r in g.remotes]
    ok=g.decision(a,consume=True)
    replay=g.decision(a)
    (g.remotes[2].directory/'checkpoint.json').unlink()
    lost=g.decision(a)
    return {'accepted':ok,'replayed':replay,'storage_deleted':lost,'audit_ok':g.audit_ok(),'events':len(g.log)}
if __name__=='__main__':
    with tempfile.TemporaryDirectory() as d:print(json.dumps(demo(d),indent=2))
