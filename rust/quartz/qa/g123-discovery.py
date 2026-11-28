"""G123 signed competing-index discovery, observation only. .dlw"""
import hashlib,json,re,os,importlib.util
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
s=importlib.util.spec_from_file_location('manifest',Path(__file__).with_name('g121-manifest.py')); M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def message(claim):return b'G123\0'+canonical(claim)
def fingerprint(claim,sig):return hashlib.sha256(message(claim)+sig).hexdigest()
def hex64(x):return isinstance(x,str) and re.fullmatch('[0-9a-f]{64}',x) is not None
def verify(root,ledger,claim,sig,key,pin):
    if type(claim) is not dict or set(claim)!={'ledger','inventory','indexes'} or claim['ledger']!=ledger or not hex64(claim['inventory']):raise ValueError('claim')
    indexes=claim['indexes']
    if type(indexes) is not list or len(indexes)>4096 or not all(hex64(h) for h in indexes) or indexes!=sorted(set(indexes)):raise ValueError('indexes')
    if type(sig) is not bytes or len(sig)!=64 or type(key) is not bytes or len(key)!=32 or fingerprint(claim,sig)!=pin:raise ValueError('signature binding')
    Ed25519PublicKey.from_public_bytes(key).verify(sig,message(claim))
    inventory=M.verify(root,ledger,claim['inventory'])['manifest']; rows=dict(inventory['objects']); found=[]
    for h in indexes:
        if not 0<rows.get(h,0)<=8192:raise ValueError('missing or oversized index')
        with os.fdopen(os.open(Path(root)/h,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as f:b=f.read(8193)
        if len(b)!=rows[h] or hashlib.sha256(b).hexdigest()!=h:raise ValueError('index bytes')
        e=json.loads(b)
        if type(e) is not dict or set(e)!={'kind','ledger','index','previous','winner','incoming','archive','lock','procedure','conflict','authority'} or e['kind']!='G117_COMPETING' or e['ledger']!=ledger or e['authority']!='HOLD' or type(e['conflict']) is not bool or type(e['index']) is not int or not 0<=e['index']<256 or not all(hex64(e[k]) for k in ('previous','winner','archive','lock','procedure')) or type(e['incoming']) is not dict:raise ValueError('index schema')
        if e['archive'] not in rows:raise ValueError('missing raw archive')
        found.append({'index':h,'archive':e['archive'],'conflict':e['conflict']})
    return dict(discovered=found,authority='HOLD')
