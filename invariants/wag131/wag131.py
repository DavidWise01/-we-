import sqlite3,json,secrets,time
from contextlib import closing
from cryptography.exceptions import InvalidSignature
from wag129 import replay
from wag130 import enc,root,membership,issue,check

class Retainer:
    def __init__(self,path,mesh,name,key,keys,gate,initialize=False):
        self.path,self.mesh,self.name,self.key,self.keys,self.gate=path,mesh,name,key,keys,gate
        with closing(sqlite3.connect(path)) as c:
            if initialize:
                c.execute('CREATE TABLE retained(id INTEGER PRIMARY KEY, body TEXT)')
                c.execute('INSERT INTO retained VALUES(1,NULL)');c.commit()
            c.execute('SELECT body FROM retained WHERE id=1').fetchone()
    def audit(self,events):return replay(self.mesh,self.keys,self.gate,events)
    def retain(self,events,bound):
        if check(self.mesh,events,self.keys,bound,self.audit)!='COMPLETE_THROUGH_BOUND':raise ValueError('bound')
        if bound[0][2]!=len(events):raise ValueError('exact head required')
        with closing(sqlite3.connect(self.path)) as c:
            c.execute('BEGIN IMMEDIATE');old=c.execute('SELECT body FROM retained WHERE id=1').fetchone()[0]
            if old and check(self.mesh,events,self.keys,json.loads(old),self.audit)!='COMPLETE_THROUGH_BOUND':raise ValueError('regression or fork')
            c.execute('UPDATE retained SET body=? WHERE id=1',(enc(bound).decode(),));c.commit()
    def respond(self,nonce):
        with closing(sqlite3.connect(self.path)) as c:raw=c.execute('SELECT body FROM retained WHERE id=1').fetchone()[0]
        if raw is None:raise ValueError('uninitialized')
        body=['WAG131',self.mesh,self.name,nonce,json.loads(raw)]
        return [body,self.key.sign(enc(body)).hex()]

class Challenge:
    def __init__(self,mesh,clock=time.monotonic,ttl=5):
        self.mesh,self.clock=mesh,clock;self.nonce=secrets.token_hex(32);self.deadline=clock()+ttl;self.used=False
    def verify(self,events,keys,gate,responses):
        if self.used:return 'HOLD_USED'
        self.used=True
        if self.clock()>self.deadline:return 'HOLD_EXPIRED'
        if not membership(keys) or set(responses)!=set(keys):return 'HOLD_MISSING'
        bounds=[]
        try:
            for name,key in keys.items():
                body,sig=responses[name];key.verify(bytes.fromhex(sig),enc(body))
                if body[:4]!=['WAG131',self.mesh,name,self.nonce] or len(body)!=5:raise ValueError('scope')
                bounds.append(body[4])
        except (InvalidSignature,ValueError,TypeError,KeyError):return 'HOLD_RESPONSE'
        audit=lambda e:replay(self.mesh,keys,gate,e)
        for b in bounds:
            status=check(self.mesh,events,keys,b,audit)
            if status!='COMPLETE_THROUGH_BOUND':return status
        if any(b!=bounds[0] for b in bounds):return 'HOLD_DISAGREEMENT'
        if len(events)!=bounds[0][0][2]:return 'HOLD_UNRETAINED_EXTENSION'
        return 'VERIFIED_THROUGH_LIVE_BOUND'
