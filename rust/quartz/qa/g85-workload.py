import hashlib,time,json,platform,statistics
from playwright.sync_api import sync_playwright
rows=[]
for n in (8,32,128,256,1024,4095):
 raw=[hashlib.shake_256(i.to_bytes(4,'big')).digest(264) for i in range(n)]
 def full():
  for k in range(1,n+1):
   h=hashlib.sha256();h.update(b''.join(raw[:k]));h.digest()
 def rolling():
  h=bytes(32)
  for p in raw:h=hashlib.sha256(h+p).digest()
  return h
 def copy():
  for k in range(1,n+1):bytearray(b''.join(raw[:k]))
 for trial in range(3):
  row={'n':n,'trial':trial}
  for name,fn in ([('full',full),('rolling',rolling)] if trial%2==0 else [('rolling',rolling),('full',full)])+[('copy',copy)]:
   t=time.perf_counter_ns();fn();row[name+'_ns']=time.perf_counter_ns()-t
  rows.append(row)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page();browser=page.evaluate('''async()=>{const w=await WebAssembly.instantiate(Uint8Array.from([0,97,115,109,1,0,0,0,1,5,1,96,0,1,127,3,2,1,0,7,7,1,3,114,117,110,0,0,10,6,1,4,0,65,42,11]));const results=[];for(let j=0;j<5;j++){let sum=0;const t=performance.now();for(let i=0;i<1000000;i++)sum+=w.instance.exports.run();results.push({ms:performance.now()-t,sum});}return results}''');version=b.version;b.close()
result={'generation':85,'platform':platform.platform(),'python':platform.python_version(),'chromium':version,'scope':'Python SHA256 and buffer-copy proxies; browser constant WASM call loop, not Quartz Rust','rows':rows,'browser':browser,'quartz_rust_executed':False}
print(json.dumps(result,indent=2))
