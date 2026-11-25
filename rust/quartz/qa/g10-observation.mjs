import {chromium} from 'playwright';
import assert from 'node:assert/strict';
const browser=await chromium.launch();
try{
 const page=await browser.newPage();
 await page.goto('http://127.0.0.1:8765/');
 const result=await page.evaluate(async()=>{
  const {default:init,Quartz}=await import('/pkg/quartz_kernel.js');await init();
  const q=new Quartz(100,100,100);q.shock(0,40);q.recover();
  const f=q.observation(),v=new DataView(f.buffer,f.byteOffset,f.byteLength);
  const layout=[f.length,f[0],f[62],v.getUint32(125,true),v.getUint32(129,true),v.getUint32(133,true),Number(v.getBigUint64(137,true))];
  f[62]=0;const isolated=q.observation()[62]===100;
  const iterations=100000;
  function bench(fn){let sum=0;const start=performance.now();for(let i=0;i<iterations;i++)sum+=fn();return {ms:performance.now()-start,checksum:sum};}
  const separate=()=>q.health()[0]+q.energy()[0];
  const packed=()=>{let b=q.observation();return b[0]+new DataView(b.buffer,b.byteOffset,b.byteLength).getUint32(125,true);};
  bench(separate);bench(packed);
  const samples=Array.from({length:5},(_,i)=>{let a,b;if(i%2){b=bench(packed);a=bench(separate);}else{a=bench(separate);b=bench(packed);}return {separate:a,packed:b};});
  const oversized=q.replay('QJ1 100 100 100\n'+'R\n'.repeat(2049));
  q.free();return {layout,isolated,oversized,iterations,samples};
 });
 assert.deepEqual(result.layout,[145,84,100,92,92,92,1]);
 assert.equal(result.isolated,true);assert.equal(result.oversized,false);
 for(const s of result.samples)assert.equal(s.separate.checksum,s.packed.checksum);
 console.log(JSON.stringify(result,null,2));
}finally{await browser.close();}
