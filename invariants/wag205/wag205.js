// WAG-205 — continuous observational homeostasis .dlw
const Q=[8,32,128], H=[5000,15000,30000];
function initial(){return {c:[0,0,0],s:0,p:0,age:0,quiet:0,fresh:[],reacq:false,o:null,n:0,noise:0,fast:0,gate:'weighted',prev:null}}
function step(old,d,mode='continuous'){
 const z={...old,c:[...old.c],fresh:[...old.fresh],n:old.n+1};
 if(d===null){z.reacq=true;z.fresh=[];z.o=null;z.prev=null;return z}
 const cls=v=>v===null?null:v>=200?1:v<=-200?-1:0;
 const a=cls(old.prev),b=cls(d);
 // Estimate change frequency, independently of committed state; use the prior estimate for selection.
 z.noise=a===null?old.noise:Math.floor((63*old.noise+(a!==b?1024:0))/64);
 z.fast=a===null?old.fast:Math.floor((7*old.fast+(a!==b?1024:0))/8);
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
 else if(mode==='continuous'||mode==='weighted'||mode==='latest'||mode==='robust'||mode==='adaptive'||mode==='second'){let q=qualified;if(mode==='weighted'){const score=z.fresh.reduce((a,v,j)=>a+(z.s?z.s*v>=200:Math.abs(v)<200)*(j+1),0);q=z.fresh.length===8&&score>=30;}if(mode==='robust'){const support=z.fresh.map(v=>z.s?z.s*v>=200:Math.abs(v)<200);q=support.length===8&&support.filter(Boolean).length>=6&&support.slice(-3).filter(Boolean).length>=2;}if(mode==='adaptive'||mode==='second'){const support=z.fresh.map(v=>z.s?z.s*v>=200:Math.abs(v)<200);const noisy=mode==='second'?(old.noise>=64||old.fast-old.noise>=128):old.noise>=64;z.gate=noisy?'robust':'weighted';q=support.length===8&&(noisy?support.filter(Boolean).length>=6&&support.slice(-3).filter(Boolean).length>=2:support.reduce((a,v,j)=>a+(v?j+1:0),0)>=30);}if(mode==='latest')q=qualified&&(z.s?z.s*d>=200:Math.abs(d)<200);z.o=q?z.s:null;z.reacq=!q}
 else z.o=z.s;
 if(![-1,0,1].includes(z.s)||z.age>64||z.quiet>=8)throw Error('state bounds');
 return z;
}

 // Recurrence uses transition events, not agreement of mostly-zero samples.
function resonance(bits){
 if(bits.length<128)return {period:null,score:0};
 let best={period:null,score:0};
 for(let lag=4;lag<=32;lag++){
 let union=0,both=0;
 for(let i=lag;i<bits.length;i++){union+=bits[i]||bits[i-lag]?1:0;both+=bits[i]&&bits[i-lag]?1:0}
 if(union<8)continue;
 const score=both/union;
 if(score>best.score)best={period:lag,score};
 }
 return best.score>=0.8?best:{period:null,score:best.score};
}
function observer(){return {kernel:initial(),bits:[],prev:null,lock:null,score:0}}
function observe(o,d){
 const k=step(o.kernel,d,'second');
 if(d===null)return {kernel:k,bits:[],prev:null,lock:null,score:0};
 const cls=d>=200?1:d<=-200?-1:0;
 const bits=o.prev===null?[]:[...o.bits,Number(cls!==o.prev)].slice(-128);
 const r=resonance(bits);
 return {kernel:k,bits,prev:cls,lock:r.period,score:r.score};
}
function experiment(){
 const rows=[];let count=0,missing=0,predicted=0,actual=0,tp=0;
 for(const period of [9,13,17,23]){
 for(const kind of ['periodic','shuffled','jittered']){
 let locks=0,exact=0,latencies=[],finalScores=[];
 for(let seed=205;seed<269;seed++){
 let x=seed,sign=seed%2?1:-1;const rand=()=>{x=(Math.imul(x,1664525)+1013904223)>>>0;return x};
 const glitch=Array.from({length:384},(_,i)=>i%period===3?1:0);
 if(kind==='shuffled'){for(let i=glitch.length-1;i>0;i--){let j=rand()%(i+1);[glitch[i],glitch[j]]=[glitch[j],glitch[i]]}}
 if(kind==='jittered'){for(let i=3;i<383;i+=period){let j=i+(rand()%3)-1;glitch[i]=0;glitch[j]=1}}
 let o=observer(),m=observer(),first=null;
 for(let i=0;i<glitch.length;i++){
 const d=sign*(glitch[i]?-900:900);
 const pred=o.lock!==null&&o.bits.length>=o.lock?o.bits[o.bits.length-o.lock]:0;
 const bit=o.prev!==null?Number((d>0?1:-1)!==o.prev):0;
 if(kind==='periodic'&&i>=256){predicted+=pred;actual+=bit;tp+=pred&&bit?1:0}
 o=observe(o,d);m=observe(m,-d);count++;
 if(o.lock!==m.lock||o.score!==m.score||o.kernel.s!==-m.kernel.s||o.kernel.o!==(m.kernel.o===null?null:-m.kernel.o))throw Error('mirror');
 if(first===null&&o.lock!==null)first=i+1;
 }
 locks+=o.lock!==null;exact+=o.lock===period;finalScores.push(o.score);if(first!==null)latencies.push(first);
 o=observe(o,null);count++;missing++;if(o.lock!==null||o.bits.length||o.kernel.o!==null)throw Error('missing reset');
 }
 rows.push({period,kind,runs:64,locks,exact,meanScore:finalScores.reduce((a,b)=>a+b,0)/64,firstLockMedian:latencies.length?latencies.sort((a,b)=>a-b)[Math.floor(latencies.length/2)]:null});
 }}
 return {count,missing,mirroredChecks:count-missing,prediction:{predicted,actual,tp},rows};
}
if(typeof module!=='undefined')module.exports={observer,observe,resonance,experiment};
if(typeof require!=='undefined'&&typeof module!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment(),null,2));
