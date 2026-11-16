"""WAG-083: signed multi-store anchor quorum and fork-safe recovery.
Three directories emulate hosts; they do NOT establish off-host isolation.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
import json, os

def canon(obj): return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
def digest(obj): return sha256(canon(obj)).hexdigest()

@dataclass(frozen=True)
class AnchorHost:
    name:str
    domain:str
    ancestor:str
    public_key:Ed25519PublicKey
    path:Path

@dataclass(frozen=True)
class Decision:
    status:str
    details:tuple[str,...]

class AnchorGate:
    def __init__(self,hosts,local,epoch,root):
        self.hosts=tuple(hosts);self.local=Path(local);self.epoch=epoch;self.root=root
        if len(self.hosts)!=3:raise ValueError('need exactly three hosts')
        for f in ('name','domain','ancestor','path'):
            vals=[str(getattr(h,f)) for h in hosts]
            if len(set(vals))!=3 or any(not x for x in vals):raise ValueError('duplicate identity/domain/storage')
        if not isinstance(epoch,int) or epoch<0 or not isinstance(root,str) or len(root)!=64 or any(c not in '0123456789abcdef' for c in root):raise ValueError('checkpoint')
        self.audit=[]
        self.record('init',{'epoch':epoch,'root':root})
    def record(self,kind,details):
        row={'seq':len(self.audit),'prev':self.audit[-1]['hash'] if self.audit else '0'*64,'kind':kind,'details':details}
        row['hash']=digest(row);self.audit.append(row)
    def verify_audit(self):
        return all(r['seq']==i and r['prev']==(self.audit[i-1]['hash'] if i else '0'*64) and r['hash']==digest({k:v for k,v in r.items() if k!='hash'}) for i,r in enumerate(self.audit))
    def _inspect(self,host):
        try:
            obj=json.loads(host.path.read_text())
            if set(obj)!={'record','signature'}:return ('malformed',None)
            body=obj['record']
            if set(body)!={'host','domain','ancestor','epoch','root','challenge'}:return ('malformed',None)
            if (body['host'],body['domain'],body['ancestor'])!=(host.name,host.domain,host.ancestor):return ('identity',None)
            signature=bytes.fromhex(obj['signature'])
            host.public_key.verify(signature,b'WAG083:ANCHOR:v1:'+canon(body))
            if not isinstance(body['epoch'],int) or body['epoch']<0 or not isinstance(body['root'],str) or len(body['root'])!=64 or any(c not in '0123456789abcdef' for c in body['root']):return ('malformed',None)
            if not isinstance(body['challenge'],str) or not body['challenge']:return ('malformed',None)
            return ('valid',body)
        except FileNotFoundError:return ('missing',None)
        except (ValueError,TypeError,KeyError,UnicodeDecodeError,json.JSONDecodeError):return ('malformed',None)
        except InvalidSignature:return ('forged',None)
        except OSError:return ('unreadable',None)
    def evaluate(self,challenge):
        if not isinstance(challenge,str) or not challenge:raise ValueError('challenge')
        observations=[(h,self._inspect(h)) for h in self.hosts]
        valid=[(h,b) for h,(status,b) in observations if status=='valid']
        bad=[f'{h.name}:{s}' for h,(s,_) in observations if s!='valid']
        if bad:
            out=Decision('HOLD_ANCHOR_INCOMPLETE',tuple(sorted(bad)))
        else:
            states={(b['epoch'],b['root']) for _,b in valid}
            if len(states)!=1:
                out=Decision('QUARANTINE_CONFLICT',tuple(sorted(f'{h.name}:{b["epoch"]}:{b["root"][:12]}' for h,b in valid)))
            elif any(b['challenge']!=challenge for _,b in valid):
                out=Decision('HOLD_STALE_CHALLENGE',tuple(sorted(h.name for h,b in valid if b['challenge']!=challenge)))
            elif next(iter(states))!=(self.epoch,self.root):
                state=next(iter(states))
                if state[0]>self.epoch:status='HOLD_ANCHOR_AHEAD'
                elif state[0]<self.epoch:status='HOLD_LOCAL_AHEAD'
                else:status='QUARANTINE_ROOT_FORK'
                out=Decision(status,(f'anchor_epoch={state[0]}',f'local_epoch={self.epoch}'))
            else:out=Decision('LOCAL_RECOVERY_ELIGIBLE',('all_three_signatures_valid','three_distinct_declared_domains'))
        self.record('evaluate',{'challenge':challenge,'decision':out.status,'details':out.details})
        return out

def write_anchor(host,private_key,epoch,root,challenge):
    body={'host':host.name,'domain':host.domain,'ancestor':host.ancestor,'epoch':epoch,'root':root,'challenge':challenge}
    obj={'record':body,'signature':private_key.sign(b'WAG083:ANCHOR:v1:'+canon(body)).hex()}
    host.path.parent.mkdir(parents=True,exist_ok=True)
    tmp=host.path.with_suffix('.tmp')
    with tmp.open('w') as f:
        f.write(json.dumps(obj,sort_keys=True));f.flush();os.fsync(f.fileno())
    os.replace(tmp,host.path)

def demo(rootdir):
    base=Path(rootdir);base.mkdir(parents=True,exist_ok=True)
    keys=[Ed25519PrivateKey.generate() for _ in range(3)]
    hosts=[AnchorHost(f'W{i+1}',f'domain-{i+1}',f'ancestor-{i+1}',keys[i].public_key(),base/f'host-{i+1}'/'anchor.json') for i in range(3)]
    root=sha256(b'checkpoint-083').hexdigest(); challenge='round-083'
    gate=AnchorGate(hosts,base/'local.db',83,root)
    for i in range(3):write_anchor(hosts[i],keys[i],83,root,challenge)
    initial=gate.evaluate(challenge)
    write_anchor(hosts[2],keys[2],83,sha256(b'fork').hexdigest(),challenge)
    conflict=gate.evaluate(challenge)
    write_anchor(hosts[2],keys[2],83,root,challenge)
    restored=gate.evaluate(challenge)
    return gate,initial,conflict,restored

if __name__=='__main__':
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        g,a,b,c=demo(d)
        print(json.dumps({'initial':a.status,'conflict':b.status,'recovery':c.status,'audit_rows':len(g.audit),'audit_verified':g.verify_audit()},indent=2))
