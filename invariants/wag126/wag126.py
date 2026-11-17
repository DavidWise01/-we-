from wag125 import enc, root, replay, inspect
from cryptography.exceptions import InvalidSignature

def statement(mesh,state):
    return ['WAG126-floor',mesh,state['g'],root(state)]

def issue(mesh,keys,chains,signer,previous=None):
    status,state=inspect(mesh,keys,chains)
    if status!='CURRENT': raise ValueError(status)
    if previous is not None:
        status,_=check(mesh,keys,chains,signer.public_key(),previous)
        if status!='CURRENT': raise ValueError(status)
    body=statement(mesh,state)
    return {'body':body,'signature':signer.sign(enc(body)).hex()}

def check(mesh,keys,chains,pub,floor):
    if floor is None:return 'HOLD_NO_FLOOR',None
    try:
        body=floor['body'];pub.verify(bytes.fromhex(floor['signature']),enc(body))
        tag,scope,g,h=body
        if tag!='WAG126-floor' or scope!=mesh or type(g)!=int or g<0:raise ValueError('scope')
    except (InvalidSignature,ValueError,TypeError,KeyError):return 'HOLD_INVALID_FLOOR',None
    status,state=inspect(mesh,keys,chains)
    if status!='CURRENT':return status,None
    if state['g']<g:return 'HOLD_ROLLBACK',None
    if root(replay(mesh,keys,chains[0][:g]))!=h:return 'HOLD_FLOOR_FORK',None
    return 'CURRENT',state
