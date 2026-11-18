import sqlite3,json,secrets
from contextlib import closing
from wag137 import enc,root,check

class Anchor:
    def __init__(self,path,g,keeper_pub,key,initialize=False):
        self.path,self.g,self.pub,self.key=path,g,keeper_pub,key
        with closing(self.open()) as c:
            if initialize:
                c.execute('CREATE TABLE receipts(n INTEGER PRIMARY KEY, receipt TEXT NOT NULL)');c.commit()
            c.execute('SELECT n FROM receipts LIMIT 1').fetchone()
    def open(self):
        c=sqlite3.connect(self.path);c.execute('PRAGMA synchronous=FULL');return c
    def head(self,c):
        row=c.execute('SELECT receipt FROM receipts ORDER BY n DESC LIMIT 1').fetchone()
        return json.loads(row[0]) if row else None
    def retain(self,events,cert):
        check(self.g,events,cert,self.pub)
        if len(events)!=cert[0][2]:raise ValueError('exact bound')
        with closing(self.open()) as c:
            c.execute('BEGIN IMMEDIATE');old=self.head(c)
            if old:
                check(self.g,events,old[0][3],self.pub)
                if old[0][3]==cert:return old
            body=['WAG139-anchor',root(self.g),len(events),cert];r=[body,self.key.sign(enc(body)).hex()]
            c.execute('INSERT INTO receipts VALUES(?,?)',(len(events),enc(r).decode()));c.commit();return r
    def respond(self,nonce):
        with closing(self.open()) as c:r=self.head(c)
        if r is None:raise ValueError('uninitialized')
        b=['WAG139-live',root(self.g),nonce,r];return [b,self.key.sign(enc(b)).hex()]

class Audit:
    def __init__(self,g):self.g=g;self.nonce=secrets.token_hex(32);self.used=False
    def verify(self,events,keeper_pub,anchor_pub,kr,ar):
        if self.used:raise ValueError('used')
        self.used=True
        if kr is None or ar is None:raise ValueError('unavailable')
        kb,ks=kr;ab,az=ar
        keeper_pub.verify(bytes.fromhex(ks),enc(kb));anchor_pub.verify(bytes.fromhex(az),enc(ab))
        if kb[:3]!=['WAG138',root(self.g),self.nonce] or ab[:3]!=['WAG139-live',root(self.g),self.nonce]:raise ValueError('scope')
        r,sig=ab[3];anchor_pub.verify(bytes.fromhex(sig),enc(r))
        if r[:3]!=['WAG139-anchor',root(self.g),r[3][0][2]]:raise ValueError('receipt scope')
        if kb[3]!=r[3]:raise ValueError('keeper anchor disagreement')
        if len(events)!=r[2]:raise ValueError('extent')
        return check(self.g,events,kb[3],keeper_pub)
