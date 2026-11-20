// WAG-203 — continuous observational homeostasis .dlw
const Q=[8,32,128], H=[5000,15000,30000];
function initial(){return {c:[0,0,0],s:0,p:0,age:0,quiet:0,fresh:[],reacq:false,o:null,n:0,noise:0,prev:null}}
function step(old,d,mode='continuous'){
 const z={...old,c:[...old.c],fresh:[...old.fresh],n:old.n+1};
 if(d===null){z.reacq=true;z.fresh=[];z.o=null;z.prev=null;return z}
 const cls=v=>v===null?null:v>=200?1:v<=-200?-1:0;
 const a=cls(old.prev),b=cls(d);
 // Estimate change frequency, independently of committed state; use the prior estimate for selection.
 z.noise=a===null?old.noise:Math.floor((63*old.noise+(a!==b?1024:0))/64);
 z.prev=d;
 z.c=z.c.map((v,j)=>Math.trunc(v*(Q[j]-1)/Q[j])+d);
 if(z.s){
  z.quiet=z.c.every((v,j)=>2*z.s*v<H[j])?z.quiet+1:0;
  if(z.quiet>=8)z.s=z.quiet=0;
 }
 if(!z.s){
  if(!z.p){let j=z.c.findIndex((v,j)=>Math.abs(v)>=H[j]);if(j>=0){z.p=Math.sign(z.c[j]);z.age=0}}
  if(z.p){
   if(z.age>=3&&z.c.filter((v,j)=>z.p*v>=H[j]).length>=2){z.s=z.p;z.p=z.age=z.quiet=0}
   else if(z.age>=64||z.p*z.c[0]<0)z.p=z.age=0;
   else z.age++;
  }
 }
 z.fresh=[...z.fresh,d].slice(-8);
 const qualified=z.fresh.length===8&&(z.s?z.fresh.filter(v=>z.s*v>=200).length>=6:z.fresh.every(v=>Math.abs(v)<200));
 if(mode==='outage'){if(z.reacq&&qualified)z.reacq=false;z.o=z.reacq?null:z.s}
 else if(mode==='continuous'||mode==='weighted'||mode==='latest'||mode==='robust'||mode==='adaptive'){let q=qualified;if(mode==='weighted'){const score=z.fresh.reduce((a,v,j)=>a+(z.s?z.s*v>=200:Math.abs(v)<200)*(j+1),0);q=z.fresh.length===8&&score>=30;}if(mode==='robust'){const support=z.fresh.map(v=>z.s?z.s*v>=200:Math.abs(v)<200);q=support.length===8&&support.filter(Boolean).length>=6&&support.slice(-3).filter(Boolean).length>=2;}if(mode==='adaptive'){const support=z.fresh.map(v=>z.s?z.s*v>=200:Math.abs(v)<200);const noisy=old.noise>=64;q=support.length===8&&(noisy?support.filter(Boolean).length>=6&&support.slice(-3).filter(Boolean).length>=2:support.reduce((a,v,j)=>a+(v?j+1:0),0)>=30);}if(mode==='latest')q=qualified&&(z.s?z.s*d>=200:Math.abs(d)<200);z.o=q?z.s:null;z.reacq=!q}
 else z.o=z.s;
 if(![-1,0,1].includes(z.s)||z.age>64||z.quiet>=8)throw Error('state bounds');
 return z;
}
function experiment(){
const rows=[];let count=0;
for(const mode of ['weighted','robust','adaptive']){
 let stats={};
 for(let seed=203;seed<267;seed++){
 let x=seed,sign=seed%2?1:-1;
 const rand=()=>{x=(Math.imul(x,1664525)+1013904223)>>>0;return x};
 let z=initial(),m=initial();
 function obs(d,target,phase){z=step(z,d,mode);m=step(m,d===null?null:-d,mode);count++;if(z.s!==-m.s||z.o!==(m.o===null?null:-m.o)||z.noise!==m.noise||z.c.some((v,j)=>v!==-m.c[j]))throw Error('symmetry');if(d===null&&z.o!==null)throw Error('missing');if(!phase)return;let r=stats[phase]??={correct:0,wrong:0,unknown:0,noisy:0};r[z.o===null?'unknown':z.o===target?'correct':'wrong']++;r.noisy+=z.noise>=64?1:0}
 const sig=s=>s*(700+rand()%401);
 for(let i=0;i<128;i++)obs(sig(sign),sign,null);
 for(let i=0;i<256;i++)obs(sig(i%17===8?-sign:sign),sign,'isolated');
 for(let i=0;i<256;i++)obs(sig(i%23===8||i%23===9?-sign:sign),sign,'paired');
 for(let i=0;i<192;i++)obs(sig(sign),sign,'clean');
 for(let i=0;i<128;i++)obs(sig(-sign),-sign,'reversal');
 for(let i=0;i<256;i++)obs(i%17===8?sig(sign):0,0,'quiet');
 for(let i=0;i<64;i++)obs(null,null,'missing');
 }
 rows.push({mode,stats});
}
return {count,mirroredChecks:count,rows};
}
if(typeof module!=='undefined')module.exports={initial,step,experiment};
if(typeof require!=='undefined'&&typeof module!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment(),null,2));
