import {chromium} from 'playwright';
import {createServer} from 'node:http';
import {readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
const dir=resolve(process.argv[2]??'evidence/web');
const files={'/':'text/html','/quartz_kernel.js':'text/javascript','/quartz_kernel_bg.wasm':'application/wasm'};
const server=createServer(async(req,res)=>{try{const path=req.url;if(!Object.hasOwn(files,path)){res.writeHead(404).end();return;}const data=path==='/'?Buffer.from('<!doctype html><title>G84 parity</title>'):await readFile(resolve(dir,path.slice(1)));res.writeHead(200,{'Content-Type':files[path]});res.end(data);}catch{res.writeHead(500).end();}});
await new Promise((ok,fail)=>{server.once('error',fail);server.listen(0,'127.0.0.1',ok);});
let browser;
try{
 browser=await chromium.launch({headless:true});
 const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://127.0.0.1:'+server.address().port);
 const data=await page.evaluate(async()=>{const m=await import('/quartz_kernel.js');await m.default();return [Array.from(m.g75_fixture()),Array.from(m.g75_fixture())];});
 if(errors.length)throw Error(errors.join('\n'));
 for(let i=0;i<2;i++){const b=Buffer.from(data[i]);if(b.length<5||b.subarray(0,4).toString('hex')!=='47373500')throw Error('Invalid G75 output');await writeFile('evidence/chromium'+(i?'-repeat':'')+'.bin',b);}
 console.log('Chromium '+browser.version()+' emitted two G75 fixtures');
}finally{try{await browser?.close();}finally{await new Promise(ok=>server.close(ok));}}
