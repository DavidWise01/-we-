// WAG-200 — continuous observational homeostasis .dlw
const Q=[8,32,128], H=[5000,15000,30000];
function initial(){return {c:[0,0,0],s:0,p:0,age:0,quiet:0,fresh:[],reacq:false,o:null,n:0}}
function step(old,d,mode='continuous'){
 const z={...old,c:[...old.c],fresh:[...old.fresh],n:old.n+1};
 if(d===null){z.reacq=true;z.fresh=[];z.o=null;return z}
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
 else if(mode==='continuous'||mode==='weighted'||mode==='latest'){let q=qualified;if(mode==='weighted'){const score=z.fresh.reduce((a,v,j)=>a+(z.s?z.s*v>=200:Math.abs(v)<200)*(j+1),0);q=z.fresh.length===8&&score>=30;}if(mode==='latest')q=qualified&&(z.s?z.s*d>=200:Math.abs(d)<200);z.o=q?z.s:null;z.reacq=!q}
 else z.o=z.s;
 if(![-1,0,1].includes(z.s)||z.age>64||z.quiet>=8)throw Error('state bounds');
 return z;
}
function fixture(seed){
 let x=seed>>>0;
 function rand(){x=(Math.imul(x,1664525)+1013904223)>>>0;return x}
 const sign=seed%2?1:-1, a=[];
 const sig=(n,s,name)=>{for(let i=0;i<n;i++)a.push([s*(700+rand()%401),s,name])};
 const quiet=(n,name)=>{for(let i=0;i<n;i++)a.push([Number(rand()%201)-100,0,name])};
 sig(96,sign,'initial');quiet(256,'quiet');sig(96,-sign,'restart');
 for(let i=0;i<64;i++)a.push([null,null,'missing']);
 sig(96,sign,'reverse_after_gap');
 for(let i=0;i<64;i++)a.push([i%2?900:-900,0,'alternating']);
 sig(96,-sign,'reverse_live');quiet(256,'final_quiet');
 return a;
}
function experiment(){
 const rows=[];let count=0,checks=0;
 for(const batch of [200,2010])for(const mode of ['continuous','weighted','latest']){
  const stats={correct:0,wrong:0,unknown:0,phases:{}};
  for(let seed=batch;seed<batch+32;seed++){
   let z=initial(),m=initial();
   for(const [d,target,name] of fixture(seed)){
    z=step(z,d,mode);m=step(m,d===null?null:-d,mode);count++;
    if(z.s!==-m.s||z.o!==(m.o===null?null:-m.o)||z.c.some((v,j)=>v!==-m.c[j]))throw Error('symmetry');
    if(d===null&&z.o!==null)throw Error('missing');
    checks++;
    const k=z.o===null?'unknown':z.o===target?'correct':'wrong';stats[k]++;
    const p=stats.phases[name]??={correct:0,wrong:0,unknown:0};p[k]++;
   }
  }
  rows.push({batch,mode,...stats});
 }
 return {count,checks,rows};
}
if(typeof module!=='undefined')module.exports={initial,step,fixture,experiment};
if(typeof require!=='undefined'&&typeof module!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment(),null,2));
