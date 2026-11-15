"""WAG-074 repository reference: dual signed review and rotation."""
from dataclasses import dataclass
from hashlib import sha256
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def hashof(x):return sha256(enc(x)).hexdigest()
def verify(key,msg,sig):
    try:Ed25519PublicKey.from_public_bytes(key).verify(sig,enc(msg));return True
    except (InvalidSignature,ValueError,TypeError):return False

@dataclass(frozen=True)
class Witness:
    name:str
    root:str
    operator:str
    domain:str
    public:bytes
    @property
    def keyid(self):return sha256(self.public).hexdigest()

class ReviewerGate:
    def __init__(self,people,epoch=2,round_id='R7'):
        if len(people)!=3 or epoch<0 or not round_id:raise ValueError('invalid quorum')
        self._distinct(people)
        self.people={p.name:p for p in people};self.epoch=epoch;self.round=round_id
        self.certificate=None;self.quarantined=set();self.proposal=None;self.candidate=None
        self.reviews={};self.authorized=False;self.retired=set();self.used=set()
        self.ledger=[];self.log('genesis',{'names':sorted(self.people)})
    @staticmethod
    def _distinct(people):
        for field in ('name','root','operator','domain','keyid'):
            values=[getattr(w,field) for w in people]
            if len(values)!=len(set(values)) or any(not v for v in values):raise ValueError('shared '+field)
    def log(self,event,data):
        item={'n':len(self.ledger),'prev':self.ledger[-1]['hash'] if self.ledger else '0'*64,'event':event,'data':data}
        item['hash']=hashof(item);self.ledger.append(item)
    def valid_ledger(self):
        return all(item['n']==i and item['prev']==(self.ledger[i-1]['hash'] if i else '0'*64) and item['hash']==hashof({k:v for k,v in item.items() if k!='hash'}) for i,item in enumerate(self.ledger))
    def observation(self,name,state):
        return {'kind':'WAG074-observation','name':name,'state':state,'epoch':self.epoch,'round':self.round}
    def equivocation(self,name,a,sa,b,sb):
        if self.certificate or name not in self.people or a==b:raise ValueError('invalid conflict')
        key=self.people[name].public
        if not verify(key,self.observation(name,a),sa) or not verify(key,self.observation(name,b),sb):raise ValueError('invalid signature')
        self.certificate={'name':name,'a':a,'b':b,'signature_a':sa.hex(),'signature_b':sb.hex(),'epoch':self.epoch,'round':self.round}
        self.quarantined.add(name);self.log('equivocation',{'proof':self.certificate})
        return hashof(self.certificate)
    def propose(self,old,candidate,nonce,expires):
        if self.proposal or not self.certificate or old!=self.certificate['name'] or old not in self.quarantined:raise ValueError('no eligible offender')
        if candidate.name in self.people or not nonce or expires<=self.epoch:raise ValueError('invalid candidate/freshness')
        self._distinct([*self.people.values(),candidate])
        self.candidate=candidate
        self.proposal={'kind':'WAG074-rotation','old':old,'new':candidate.name,'candidate_key':candidate.keyid,
                       'evidence':hashof(self.certificate),'epoch':self.epoch,'round':self.round,'nonce':nonce,
                       'expires':expires,'roster':sorted(self.people)}
        self.log('proposal',{'hash':hashof(self.proposal)});return hashof(self.proposal)
    def review_payload(self,name,decision='approve'):
        if not self.proposal:raise ValueError('no proposal')
        return {'kind':'WAG074-review','reviewer':name,'decision':decision,'proposal_hash':hashof(self.proposal),'epoch':self.epoch,'round':self.round}
    def review(self,name,decision,signature,at_epoch=None):
        if not self.proposal or self.authorized or name not in self.people or name in self.quarantined or name in self.reviews:raise ValueError('reviewer ineligible')
        if decision not in ('approve','reject') or (at_epoch is not None and at_epoch!=self.epoch) or self.epoch>=self.proposal['expires']:raise ValueError('invalid review')
        payload=self.review_payload(name,decision)
        if not verify(self.people[name].public,payload,signature):raise ValueError('signature failure')
        self.reviews[name]=(decision,signature,payload);self.log('review',{'name':name,'decision':decision,'signature':signature.hex(),'payload':payload})
    def authorize(self):
        if not self.proposal or self.authorized:raise ValueError('proposal closed')
        expected=set(self.people)-{self.proposal['old']}
        if set(self.reviews)!=expected or len(expected)!=2:raise ValueError('two reviewers required')
        if any(self.reviews[n][0]!='approve' for n in expected):raise ValueError('veto')
        for n,(decision,sig,payload) in self.reviews.items():
            if not verify(self.people[n].public,payload,sig):raise ValueError('review changed')
        self._distinct([self.people[n] for n in expected]+[self.candidate])
        self.authorized=True;self.log('authorization',{'reviewers':sorted(expected),'proposal_hash':hashof(self.proposal)})
    def rotate(self):
        if not self.authorized or self.proposal['old'] in self.retired:raise ValueError('not authorized')
        old=self.proposal['old'];self.retired.add(old);del self.people[old]
        self.people[self.candidate.name]=self.candidate;self.epoch+=1
        self.log('rotation',{'old':old,'new':self.candidate.name,'epoch':self.epoch,'evidence':hashof(self.certificate)})
    def quorum_payload(self,name,snapshot,receipt):
        return {'kind':'WAG074-quorum','name':name,'snapshot':snapshot,'receipt':receipt,'epoch':self.epoch,'round':self.round}
    def recertify(self,reports):
        if not self.retired or len(reports)!=3 or {r[0] for r in reports}!=set(self.people):raise ValueError('missing quorum')
        if len({r[1] for r in reports})!=1:raise ValueError('snapshot disagreement')
        ids=[r[2] for r in reports]
        if any(not x for x in ids) or len(set(ids))!=3 or set(ids)&self.used:raise ValueError('receipt replay')
        for name,snapshot,receipt,signature in reports:
            if not verify(self.people[name].public,self.quorum_payload(name,snapshot,receipt),signature):raise ValueError('invalid quorum signature')
        self.used.update(ids)
        self.log('recertified',{'active':sorted(self.people),'snapshot':reports[0][1],'epoch':self.epoch})
        return 'LOCAL_DECLARED_QUORUM_RECERTIFIED'
