"""WAG-089: cryptographically evidenced sampling, conditional sequential bound.
This is a synthetic local gate, not an authentication of independent machines.
"""
import hashlib, json, math, sqlite3
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
from sys import path as syspath
syspath.insert(0,str(Path(__file__).resolve().parents[1]/'wag086'))
from wag086 import merkle, proof, verify, challenge_indices

def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def hashhex(x): return hashlib.sha256(canonical(x)).hexdigest()
@dataclass(frozen=True)
class Witness:
    name:str
    ancestor:str
    domain:str
    key:Ed25519PrivateKey

class EvidenceGate:
    def __init__(self, db, witnesses, root, count, sample_size=3, missing_threshold=3, alpha=Fraction(1,20), epoch=89):
        self.witnesses=tuple(witnesses);self.root=bytes(root);self.count=count;self.k=sample_size;self.m=missing_threshold;self.alpha=Fraction(alpha);self.epoch=epoch
        if len(self.root)!=32 or not isinstance(count,int) or not isinstance(sample_size,int) or not 0<sample_size<=count:raise ValueError('sample configuration')
        if not 1<=missing_threshold<=count or not 0<self.alpha<1:raise ValueError('risk parameters')
        if len(witnesses)!=3 or any(len(set(getattr(w,p) for w in witnesses))!=3 for p in ('name','ancestor','domain')):raise ValueError('three distinct declared witnesses')
        if any(not all((w.name,w.ancestor,w.domain)) for w in witnesses):raise ValueError('empty witness declaration')
        self.conn=sqlite3.connect(str(db),isolation_level=None,timeout=5)
        self.conn.execute('create table if not exists rounds(round integer primary key, nonce text unique, positions text, digest text)')
        self.conn.execute('create table if not exists ledger(seq integer primary key, kind text, payload text, previous text, digest text)')
        self.conn.execute('create table if not exists used_receipts(receipt text primary key)')
        self.conn.execute('create table if not exists settings(name text primary key,value text not null)')
        setting=hashhex({'root':root.hex(),'count':count,'k':sample_size,'m':missing_threshold,'alpha':[self.alpha.numerator,self.alpha.denominator],'epoch':epoch,'witnesses':[(w.name,w.ancestor,w.domain) for w in witnesses]})
        old=self.conn.execute('select value from settings where name="configuration"').fetchone()
        if old and old[0]!=setting:self.close();raise ValueError('frozen policy mismatch')
        self.conn.execute('insert or ignore into settings values (?,?)',('configuration',setting))
    def close(self):self.conn.close()
    def _audit(self,kind,payload):
        prior=self.conn.execute('select digest from ledger order by seq desc limit 1').fetchone()
        seq=self.conn.execute('select count(*) from ledger').fetchone()[0]
        prev=prior[0] if prior else '0'*64
        ph=canonical(payload).decode()
        d=hashhex([seq,kind,ph,prev]);self.conn.execute('insert into ledger values (?,?,?,?,?)',(seq,kind,ph,prev,d))
    def verify_audit(self):
        prev='0'*64
        for i,row in enumerate(self.conn.execute('select seq,kind,payload,previous,digest from ledger order by seq')):
            seq,kind,payload,prior,d=row
            if seq!=i or prior!=prev or d!=hashhex([seq,kind,payload,prior]):return False
            prev=d
        return True
    def signed_observation(self,witness,chunks,nonce,round_no):
        if len(chunks)!=self.count:raise ValueError('chunk count')
        indices=challenge_indices(nonce,self.count,self.k)
        computed,layers=merkle(chunks)
        body={'protocol':'WAG-089-OBS-v1','epoch':self.epoch,'round':round_no,'nonce':nonce.hex(),'root':self.root.hex(),'count':self.count,'witness':witness.name,'indices':list(indices),
              'samples':[{'i':i,'chunk':chunks[i].hex(),'path':proof(layers,i)} for i in indices]}
        return {'body':body,'signature':witness.key.sign(canonical(body)).hex()}
    def one_round_miss(self):
        return Fraction(math.comb(self.count-self.m,self.k),math.comb(self.count,self.k)) if self.count-self.m>=self.k else Fraction(0)
    def threshold(self,t): return self.alpha/Fraction(t*(t+1))
    def miss_bound(self,t):return self.one_round_miss()**t
    def rounds(self):return self.conn.execute('select count(*) from rounds').fetchone()[0]
    def unique_coverage(self):
        positions=set()
        for (p,) in self.conn.execute('select positions from rounds'):
            positions.update(json.loads(p))
        return tuple(sorted(positions))
    def accept_round(self,responses,nonce,round_no):
        if not isinstance(nonce,bytes) or len(nonce)<16 or not isinstance(round_no,int) or round_no<1:raise ValueError('nonce/round')
        if len(responses)!=3:raise ValueError('three responses required')
        indices=challenge_indices(nonce,self.count,self.k);seen=set();receipts=[]
        self.conn.execute('begin immediate')
        try:
            if round_no!=self.rounds()+1:raise ValueError('nonsequential round')
            if self.conn.execute('select 1 from rounds where nonce=?',(nonce.hex(),)).fetchone():raise ValueError('replayed nonce')
            for resp in responses:
                body=resp['body'];name=body['witness']
                if name in seen:raise ValueError('duplicate witness')
                who=next((w for w in self.witnesses if w.name==name),None)
                if who is None:raise ValueError('unknown witness')
                try:who.key.public_key().verify(bytes.fromhex(resp['signature']),canonical(body))
                except (InvalidSignature,ValueError,TypeError):raise ValueError('invalid signature')
                if any((body.get('protocol')!='WAG-089-OBS-v1',body.get('epoch')!=self.epoch,body.get('round')!=round_no,body.get('nonce')!=nonce.hex(),body.get('root')!=self.root.hex(),body.get('count')!=self.count,body.get('indices')!=list(indices))):raise ValueError('mismatched observation scope')
                samples=body['samples']
                if [s['i'] for s in samples]!=list(indices):raise ValueError('incorrect sample positions')
                for sample in samples:
                    try:chunk=bytes.fromhex(sample['chunk']);ok=verify(chunk,sample['i'],self.count,sample['path'],self.root)
                    except (ValueError,TypeError,KeyError):ok=False
                    if not ok:raise ValueError('invalid Merkle inclusion')
                receipt=hashhex(resp)
                if self.conn.execute('select 1 from used_receipts where receipt=?',(receipt,)).fetchone():raise ValueError('replayed receipt')
                receipts.append(receipt);seen.add(name)
            if seen!={w.name for w in self.witnesses}:raise ValueError('missing witness')
            for receipt in receipts:self.conn.execute('insert into used_receipts values (?)',(receipt,))
            summary={'epoch':self.epoch,'round':round_no,'nonce':nonce.hex(),'indices':indices,'witnesses':sorted(seen),'receipts':sorted(receipts)}
            self.conn.execute('insert into rounds values (?,?,?,?)',(round_no,nonce.hex(),json.dumps(indices),hashhex(summary)))
            t=self.rounds();passed=self.miss_bound(t)<=self.threshold(t)
            decision='LOCAL_CONDITIONAL_BOUND_MET' if passed else 'HOLD_INSUFFICIENT_EVIDENCE'
            self._audit('authenticated_round',dict(summary,decision=decision,bound=str(self.miss_bound(t)),allocated_alpha=str(self.threshold(t))))
            self.conn.commit()
            return {'decision':decision,'round':t,'positions':indices,'unique_coverage':len(self.unique_coverage()),'miss_bound':self.miss_bound(t),'alpha_t':self.threshold(t)}
        except Exception:
            self.conn.rollback();raise

def demo(db=':memory:'):
    chunks=[f'WAG089-block-{i:02d}'.encode() for i in range(17)]
    root,_=merkle(chunks)
    witnesses=[Witness(f'W{i}',f'ancestor-{i}',f'domain-{i}',Ed25519PrivateKey.generate()) for i in range(1,4)]
    gate=EvidenceGate(db,witnesses,root,len(chunks),3,3)
    try:
        out=[]
        for t in range(1,15):
            nonce=f'WAG089-fresh-round-{t:04d}'.encode()
            responses=[gate.signed_observation(w,chunks,nonce,t) for w in witnesses]
            out.append(gate.accept_round(responses,nonce,t))
        try:gate.accept_round(responses,nonce,14);replay='ACCEPTED_ERROR'
        except ValueError:replay='REJECTED'
        return {'first_qualifying_round':next((r['round'] for r in out if r['decision']=='LOCAL_CONDITIONAL_BOUND_MET'),None),'rounds':gate.rounds(),'coverage':len(gate.unique_coverage()),'replay':replay,'audit_ok':gate.verify_audit(),'events':gate.conn.execute('select count(*) from ledger').fetchone()[0]}
    finally:gate.close()
if __name__=='__main__':print(demo())
