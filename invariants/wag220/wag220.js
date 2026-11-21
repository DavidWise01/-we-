// WAG-219 extends WAG-212 component persistence — .dlw; one observation ancestry
const PERIODS=[9,13,17,23];
function rng(seed){let x=seed>>>0;return ()=>{x=(Math.imul(x,1664525)+1013904223)>>>0;return x}}
function generate(p,kind,seed){const rand=rng(seed),q=kind==='harmonic'?p*2:p+4,g=Array(384).fill(0),truth={before:[p,q],after:[]};
 for(let i=3;i<384;i+=p)if(kind!=='dropA'||i<192)g[i]=1;
 for(let i=7%q;i<384;i+=q){if((kind==='dropB'||kind==='bothDrop')&&i>=192)continue;const j=kind==='shiftB'&&i>=192?i+3:kind==='jitterB'?i+((rand()>>>16)%3)-1:i;if(j>=0&&j<384)g[j]=1}
 if(kind==='bothDrop')for(let i=192;i<384;i++)g[i]=0;
 if(kind==='driftB'){for(let i=192;i<384;i++)g[i]=0;for(let i=3;i<384;i+=p)if(i>=192)g[i]=1;for(let i=7%q+q*Math.ceil((192-7%q)/q);i<384;i+=q+2)g[i]=1}
 if(['stable','harmonic','jitterB','shiftB'].includes(kind))truth.after=[p,q];
 if(kind==='dropB')truth.after=[p];if(kind==='dropA')truth.after=[q];if(kind==='bothDrop')truth.after=[];if(kind==='driftB')truth.after=[p,q+2];
 return {g,q,truth};
}
function events(g,a,b){const z=[];for(let i=a;i<b;i++)if(g[i])z.push(i);return z}
function forecast(c,a,b){const z=[];for(let i=a;i<b;i++)if(i%c.p===c.phase)z.push(i);return z}
function match(obs,prd,tol=1){let n=0;const used=Array(obs.length).fill(false);for(const x of prd){let best=-1,d=tol+1;for(let j=0;j<obs.length;j++)if(!used[j]&&Math.abs(obs[j]-x)<d){d=Math.abs(obs[j]-x);best=j}if(best>=0&&d<=tol){used[best]=true;n++}}const precision=prd.length?n/prd.length:0,recall=obs.length?n/obs.length:0;return {f1:precision+recall?2*precision*recall/(precision+recall):0,precision,recall,hits:n}}
function combo(obs,cs,a,b){return match(obs,[...new Set(cs.flatMap(c=>forecast(c,a,b)))].sort((x,y)=>x-y))}
function train(g){const obs=events(g,0,192),cs=[];for(let p=7;p<=46;p++){let best=null;for(let phase=0;phase<p;phase++){const v=combo(obs,[{p,phase}],0,192);if(!best||v.f1>best.f1)best={p,phase,f1:v.f1}}cs.push(best)}cs.sort((a,b)=>b.f1-a.f1);let pair=null;for(let i=0;i<cs.length;i++)for(let j=i+1;j<cs.length;j++){const a=cs[i],b=cs[j],v=combo(obs,[a,b],0,192);if(!pair||v.f1>pair.f1)pair={components:[a,b],f1:v.f1}}return pair&&pair.f1>=cs[0].f1+.1&&pair.f1>=.8?pair.components.sort((a,b)=>a.p-b.p):null}
function persist(g,policy='elastic'){const cs=train(g);if(!cs)return {components:[],state:'unknown',learned:[]};const obs=events(g,192,384);const learned=cs.map(c=>{const direct=match(obs,forecast(c,192,384)).precision;let score=direct,phase=c.phase;if(policy==='elastic')for(let shift=-3;shift<=3;shift++){const p=((c.phase+shift)%c.p+c.p)%c.p,v=match(obs,forecast({p:c.p,phase:p},192,384)).precision;if(v>score){score=v;phase=p}}return {p:c.p,phase,score,direct,retained:score>=.7}});const components=learned.filter(c=>c.retained).map(c=>c.p).sort((a,b)=>a-b);return {components,state:components.length?'partial_or_complete':'unknown',learned}}

function secondHalfModels(g){const h=g.slice(192),obs=events(h,0,192),cs=[];for(let p=7;p<=46;p++){let best=null;for(let phase=0;phase<p;phase++){const v=combo(obs,[{p,phase}],0,192);if(!best||v.f1>best.f1)best={p,phase,f1:v.f1}}cs.push(best)}
 cs.sort((a,b)=>b.f1-a.f1);const single=cs[0];let pair=null;for(let i=0;i<cs.length;i++)for(let j=i+1;j<cs.length;j++){const a=cs[i],b=cs[j],v=combo(obs,[a,b],0,192);if(!pair||v.f1>pair.f1)pair={components:[a,b],f1:v.f1}}
 return {single,pair};
}
function replace(g,policy='guard'){
 const prior=persist(g,'elastic'),old=prior.components;
 if(policy==='prior')return {components:old,status:'prior',old};
 const {single,pair}=secondHalfModels(g),bestPair=pair&&pair.f1>=single.f1+.1&&pair.f1>=.8;
 const trial=bestPair?pair.components.map(x=>x.p).sort((a,b)=>a-b):single.f1>=.85?[single.p]:[];
 if(policy==='retrain')return {components:trial,status:'relearned',old,singleF1:single.f1,pairF1:pair?.f1??0};
 let components;
 if(pair&&pair.f1>=.88&&pair.f1>=single.f1+.1)components=pair.components.map(x=>x.p).sort((a,b)=>a-b);
 else if(single.f1>=.9)components=[single.p];
 else components=old;
 return {components,status:'qualified',old,singleF1:single.f1,pairF1:pair?.f1??0};
}


function make214(p,kind,seed){
 const q=p+4,g=Array(576).fill(0),rand=rng(seed);
 function add(period,phase,start,end,jitter=false){for(let i=start;i<end;i++)if(((i-phase)%period+period)%period===0){const j=i+(jitter?((rand()>>>16)%3)-1:0);if(j>=start&&j<end)g[j]=1}}
 for(let w=0;w<3;w++){const a=w*192,b=a+192;
  if(kind!=='dropA'||w===0)add(p,3,a,b);
  if(!(kind==='dropB'&&w>0)&&!(kind==='ephemeral'&&w===2)&&!(kind==='bothDrop'&&w>0)){
   const bp=w>0&&['replace','ephemeral'].includes(kind)?q+2:q;
   add(bp,w>0&&kind==='shiftB'?10:7,a,b,kind==='jitterB');
  }
 }
 if(kind==='bothDrop')g.fill(0,192);
 if(kind==='mixedTransient'){g.fill(0);add(p,3,0,576);add(q,7,0,384);add(q+2,8,192,384)}
 if(kind==='harmonic'){g.fill(0);add(p,3,0,576);add(p*2,7,0,576)}
 const expected=({replace:[p,q+2],ephemeral:[p],mixedTransient:[p],dropA:[q],dropB:[p],bothDrop:[],harmonic:[p,p*2]})[kind]??[p,q];
 return {g,expected:expected.sort((a,b)=>a-b)};
}
function proposeWindow(g,a){
 const h=g.slice(a,a+192),{single,pair}=secondHalfModels([...Array(192).fill(0),...h]);
 let components=[];
 if(pair&&pair.f1>=.88&&pair.f1>=single.f1+.1)components=pair.components;
 else if(single.f1>=.9)components=[single];
 return {components:components.map(c=>({p:c.p,phase:(c.phase+a)%c.p})),f1:components.length===2?pair.f1:single.f1};
}
function qualify214(g,policy='verified'){
 const original=proposeWindow(g,0),candidate=proposeWindow(g,192);
 if(policy==='provisional')return {components:[...new Set(candidate.components.map(c=>c.p))].sort((a,b)=>a-b),original,candidate,qualified:[]};
 const obs=events(g,384,576),qualified=candidate.components.map(c=>({...c,precision:match(obs,forecast(c,384,576)).precision}));
 return {components:qualified.filter(c=>c.precision>=.65).map(x=>x.p).sort((a,b)=>a-b),original,candidate,qualified};
}


const WAG215_KINDS=['stable','jitterB','shiftB','replace','ephemeral','dropA','dropB','bothDrop','mixedTransient','harmonic'];
function registry215(g){
 const original=proposeWindow(g,0),candidate=proposeWindow(g,192),obs=events(g,384,576),log=[],states=new Map();
 const append=(type,id,window,details={})=>log.push({seq:log.length,type,id,window,details});
 for(const c of original.components){const id='o:'+c.p+':'+c.phase;states.set(id,{id,p:c.p,phase:c.phase,origin:0,state:'established',replaces:null});append('ESTABLISHED',id,0,{p:c.p,phase:c.phase})}
 for(const c of candidate.components){const current=[...states.values()].find(e=>e.p===c.p);
  if(current)append('REOBSERVED',current.id,1,{p:c.p,phase:c.phase});
  else{const old=[...states.values()].filter(e=>!candidate.components.some(x=>x.p===e.p));
   const replaces=old.length===1?old[0].id:null,id='c:'+c.p+':'+c.phase;
   states.set(id,{id,p:c.p,phase:c.phase,origin:1,state:'reserved',replaces});
   append('RESERVED',id,1,{p:c.p,phase:c.phase,replaces});}
 }
 if(!candidate.components.length)append('UNRESOLVED','environment',1,{reason:'no_model'});
 const retained=[];
 for(const c of candidate.components){const state=[...states.values()].find(e=>e.p===c.p),precision=match(obs,forecast(c,384,576)).precision,pass=precision>=.65;
  append(pass?'QUALIFIED':'EXPIRED',state.id,2,{precision,threshold:.65});state.state=pass?'qualified':'expired';if(pass)retained.push(state.p);
 }
 for(const state of states.values()){if(state.origin!==0||candidate.components.some(c=>c.p===state.p))continue;
  const precision=match(obs,forecast(state,384,576)).precision,pass=precision>=.65;
  append(pass?'PERSISTED':'RELEASED',state.id,2,{precision,threshold:.65});
  state.state=pass?'qualified':'released';if(pass)retained.push(state.p);
 }
 return {periods:[...new Set(retained)].sort((a,b)=>a-b),log,states:[...states.values()],original,candidate};
}
function replay215(log){
 const states=new Map();
 for(let i=0;i<log.length;i++){const e=log[i];if(e.seq!==i||![0,1,2].includes(e.window))throw Error('seq');
  if(i&&e.window<log[i-1].window)throw Error('non-monotone-window');
  let s=states.get(e.id);
  if(e.type==='ESTABLISHED'||e.type==='RESERVED'){if(s)throw Error('duplicate');states.set(e.id,{p:e.details.p,state:e.type==='RESERVED'?'reserved':'established'})}
  else if(e.type==='UNRESOLVED'){if(e.id!=='environment'||e.window!==1)throw Error('bad-unknown')}
  else{if(!s)throw Error('orphan');
   if(e.type==='REOBSERVED'){if(s.state!=='established'||e.window!==1)throw Error('reobserve')}
   else if(e.type==='QUALIFIED'||e.type==='PERSISTED'){if(!['established','reserved'].includes(s.state)||e.window!==2)throw Error('qualify');s.state='qualified'}
   else if(e.type==='EXPIRED'){if(!['established','reserved'].includes(s.state)||e.window!==2)throw Error('expire');s.state='expired'}
   else if(e.type==='RELEASED'){if(s.state!=='established'||e.window!==2)throw Error('release');s.state='released'}
   else throw Error('type');
  }
 }
 return [...states.values()].filter(s=>s.state==='qualified').map(s=>s.p).sort((a,b)=>a-b);
}


function make216(p,kind,seed){
 const a=make214(p,kind,seed),g=a.g.slice(),next=Array(192).fill(0),q=p+4;
 const add=(period,phase)=>{for(let t=576;t<768;t++)if(((t-phase)%period+period)%period===0)next[t-576]=1};
 if(!['dropA','bothDrop'].includes(kind))add(p,3);
 if(['stable','jitterB','shiftB','harmonic','dropA'].includes(kind))add(kind==='harmonic'?2*p:q,kind==='shiftB'?10:7);
 if(kind==='replace')add(q+2,7);
 if(kind==='mixedTransient'){next.fill(0);add(p,3)}
 if(kind==='harmonic'){next.fill(0);add(p,3);add(2*p,7)}
 if(kind==='jitterB'){next.fill(0);add(p,3);const rand=rng(seed+216);for(let t=576;t<768;t++)if(((t-7)%q+q)%q===0){const j=t-576+((rand()>>>16)%3)-1;if(j>=0&&j<192)next[j]=1}}
 return {g:[...g,...next],expected:a.expected};
}
function recover216(g){
 const first=registry215(g.slice(0,576)),log=first.log.map(e=>({...e})),states=first.states.map(e=>({...e})),obs=events(g,576,768);
 const append=(type,id,details={})=>log.push({seq:log.length,type,id,window:3,details});
 for(const s of states){
  let best=match(obs,forecast(s,576,768)).precision,phase=s.phase;
  for(let d=-3;d<=3;d++){const ph=((s.phase+d)%s.p+s.p)%s.p,v=match(obs,forecast({p:s.p,phase:ph},576,768)).precision;if(v>best){best=v;phase=ph}}
  if(['expired','released'].includes(s.state)){
   if(best>=.7){append('REOPENED',s.id,{previous:s.state,precision:best,phase});append('REQUALIFIED',s.id,{precision:best,phase});s.state='qualified';s.phase=phase}
   else append('RECHECK_FAILED',s.id,{state:s.state,precision:best});
  }else if(s.state==='qualified'){
   if(best<.55){append('LOST',s.id,{precision:best});s.state='released'}
   else append('CONTINUED',s.id,{precision:best});
  }
 }
 return {periods:states.filter(s=>s.state==='qualified').map(s=>s.p).sort((a,b)=>a-b),states,log,first};
}
function replay216(log){
 const old=log.filter(e=>e.window<=2),newEvents=log.filter(e=>e.window===3);
 replay215(old);
 if(old.length+newEvents.length!==log.length)throw Error('unsupported window');
 const states=new Map();
 for(const e of old){
  if(['ESTABLISHED','RESERVED'].includes(e.type))states.set(e.id,{p:e.details.p,state:e.type==='RESERVED'?'reserved':'established'});
  else if(['QUALIFIED','PERSISTED'].includes(e.type))states.get(e.id).state='qualified';
  else if(e.type==='EXPIRED')states.get(e.id).state='expired';
  else if(e.type==='RELEASED')states.get(e.id).state='released';
 }
 const pending=new Set();
 for(let i=0;i<newEvents.length;i++){const e=newEvents[i],s=states.get(e.id);
  if(e.seq!==old.length+i||!s)throw Error('out-of-order/orphan');
  if(e.type==='REOPENED'){if(!['expired','released'].includes(s.state)||pending.has(e.id))throw Error('invalid reopen');pending.add(e.id)}
  else if(e.type==='REQUALIFIED'){if(!pending.has(e.id))throw Error('unpaired requalification');s.state='qualified';pending.delete(e.id)}
  else if(e.type==='RECHECK_FAILED'){if(!['expired','released'].includes(s.state))throw Error('invalid failed recheck')}
  else if(e.type==='CONTINUED'){if(s.state!=='qualified')throw Error('invalid continuation')}
  else if(e.type==='LOST'){if(s.state!=='qualified')throw Error('invalid loss');s.state='released'}
  else throw Error('invalid event');
 }
 if(pending.size)throw Error('unclosed reopen');
 return [...states.values()].filter(s=>s.state==='qualified').map(s=>s.p).sort((a,b)=>a-b);
}


const TYPES217=['stable','jitterB','replace','ephemeral','flash_return','dropA','dropB','bothDrop','harmonic'];
function make217(p,kind,seed){
 const a=make216(p,kind==='flash_return'?'ephemeral':kind,seed),g=a.g.slice(),q=p+4;
 const add=(period,phase,start,end,jitter=null)=>{let random=jitter===null?null:rng(jitter);for(let t=start;t<end;t++)if(((t-phase)%period+period)%period===0){let j=t+(random?((random()>>>16)%3)-1:0);if(j>=start&&j<end)g[j]=1}};
 if(kind==='flash_return'){g.fill(0,576,768);add(p,3,576,768);add(q+2,7,576,768)}
 g.length=960;g.fill(0,768,960);
 if(!['dropA','bothDrop'].includes(kind))add(p,3,768,960);
 if(['stable','jitterB','harmonic','dropA'].includes(kind))add(kind==='harmonic'?2*p:q,7,768,960,kind==='jitterB'?seed+217:null);
 if(kind==='replace')add(q+2,7,768,960);
 if(kind==='harmonic'){g.fill(0,768,960);add(p,3,768,960);add(2*p,7,768,960)}
 return {g,expected:kind==='flash_return'?[p]:a.expected};
}
function precision217(obs,s){let best=match(obs,forecast(s,768,960)).precision;for(let d=-3;d<=3;d++){let phase=((s.phase+d)%s.p+s.p)%s.p;best=Math.max(best,match(obs,forecast({p:s.p,phase},768,960)).precision)}return best}
function qualify217(g){
 const previous=recover216(g.slice(0,768)),states=previous.states.map(s=>({...s})),log=previous.log.map(e=>({...e,details:{...e.details}}));
 const reopened=new Set(log.filter(e=>e.type==='REOPENED').map(e=>e.id));
 for(const e of log)if(e.type==='REQUALIFIED'&&reopened.has(e.id)){e.type='PROBATION';states.find(s=>s.id===e.id).state='probation'}
 const obs=events(g,768,960),append=(type,id,details={})=>log.push({seq:log.length,window:4,type,id,details});
 for(const s of states){
  const precision=precision217(obs,s);
  if(s.state==='probation'){if(precision>=.7){append('REQUALIFIED',s.id,{precision,from:'probation'});s.state='qualified'}else{append('PROBATION_FAILED',s.id,{precision});s.state='expired'}}
  else if(s.state==='qualified'){if(precision>=.55)append('CONTINUED',s.id,{precision});else{append('LOST',s.id,{precision});s.state='released'}}
  else if(['expired','released'].includes(s.state))append('RECHECK_FAILED',s.id,{precision});
 }
 return {periods:states.filter(s=>s.state==='qualified').map(s=>s.p).sort((a,b)=>a-b),states,log,previous};
}
function replay217(log){
 const earlier=log.filter(e=>e.window<=3),last=log.filter(e=>e.window===4);
 replay216(earlier.map(e=>e.type==='PROBATION'?{...e,type:'REQUALIFIED'}:e));
 const states=new Map(),pending=new Set();
 for(const e of earlier){
  if(['ESTABLISHED','RESERVED'].includes(e.type))states.set(e.id,{p:e.details.p,state:e.type==='RESERVED'?'reserved':'established'});
  else if(['QUALIFIED','PERSISTED'].includes(e.type))states.get(e.id).state='qualified';
  else if(e.type==='EXPIRED')states.get(e.id).state='expired';
  else if(e.type==='RELEASED')states.get(e.id).state='released';
  else if(e.type==='REOPENED')pending.add(e.id);
  else if(e.type==='PROBATION'){if(!pending.has(e.id))throw Error('unpaired probation');states.get(e.id).state='probation';pending.delete(e.id)}
  else if(e.type==='REQUALIFIED'){if(!pending.has(e.id))throw Error('unpaired recovery');states.get(e.id).state='qualified';pending.delete(e.id)}
  else if(e.type==='LOST')states.get(e.id).state='released';
 }
 if(pending.size)throw Error('unclosed reopening');
 for(let i=0;i<last.length;i++){const e=last[i],s=states.get(e.id);
  if(e.seq!==earlier.length+i||!s)throw Error('sequence or orphan');
  if(e.type==='REQUALIFIED'){if(s.state!=='probation'||e.details.from!=='probation')throw Error('invalid recovery');s.state='qualified'}
  else if(e.type==='PROBATION_FAILED'){if(s.state!=='probation')throw Error('invalid probation');s.state='expired'}
  else if(e.type==='CONTINUED'){if(s.state!=='qualified')throw Error('invalid continue')}
  else if(e.type==='LOST'){if(s.state!=='qualified')throw Error('invalid loss');s.state='released'}
  else if(e.type==='RECHECK_FAILED'){if(!['expired','released'].includes(s.state))throw Error('invalid recheck')}
  else throw Error('invalid event');
 }
 return [...states.values()].filter(s=>s.state==='qualified').map(s=>s.p).sort((a,b)=>a-b);
}


const KINDS218=['stable','jitterB','dropB','ephemeral','flash_return','harmonic'],MASKS218=['visible','missing','first_half','alternate'];
function make218(p,kind,seed,mask){
 const x=make217(p,kind,seed),g=x.g.slice();
 for(let i=768;i<960;i++)if(mask==='missing'||mask==='first_half'&&i>=864||mask==='alternate'&&(i-768)%2===1)g[i]=null;
 return {...x,g};
}
function score218(g,c){
 const covered=[];for(let i=768;i<960;i++)if(g[i]!==null)covered.push(i);
 const actual=covered.filter(i=>g[i]===1);
 let best={precision:0,opportunities:0,phase:c.phase};
 for(let d=-3;d<=3;d++){
  const phase=((c.phase+d)%c.p+c.p)%c.p,forecasted=forecast({p:c.p,phase},768,960).filter(i=>g[i]!==null),precision=match(actual,forecasted).precision;
  if(precision>best.precision||precision===best.precision&&forecasted.length>best.opportunities)best={precision,opportunities:forecasted.length,phase};
 }
 return {...best,coverage:covered.length/192};
}
function qualify218(g,policy='censor'){
 if(policy==='blind'){
  const r=qualify217(g.map(v=>v===null?0:v));return {periods:r.periods,log:r.log,states:r.states,unverified:[]};
 }
 const previous=recover216(g.slice(0,768)),log=previous.log.map(e=>({...e,details:{...e.details}})),states=previous.states.map(s=>({...s}));
 const reopened=new Set(log.filter(e=>e.type==='REOPENED').map(e=>e.id));
 for(const e of log)if(e.type==='REQUALIFIED'&&reopened.has(e.id)){e.type='PROBATION';states.find(s=>s.id===e.id).state='probation'}
 const append=(type,id,details={})=>log.push({seq:log.length,type,id,window:4,details}),unverified=[];
 for(const s of states){
  const metric=score218(g,s);
  if(metric.coverage<.5||metric.opportunities<4){
   append('CENSORED',s.id,{coverage:metric.coverage,opportunities:metric.opportunities,previous:s.state});
   unverified.push(s.id);continue;
  }
  const v=metric.precision;
  if(s.state==='probation'){if(v>=.7){append('REQUALIFIED',s.id,{precision:v,from:'probation'});s.state='qualified'}else{append('PROBATION_FAILED',s.id,{precision:v});s.state='expired'}}
  else if(s.state==='qualified'){if(v>=.55)append('CONTINUED',s.id,{precision:v});else{append('LOST',s.id,{precision:v});s.state='released'}}
  else if(['expired','released'].includes(s.state))append('RECHECK_FAILED',s.id,{precision:v});
 }
 return {periods:states.filter(s=>s.state==='qualified').map(s=>s.p).sort((a,b)=>a-b),log,states,unverified};
}
function replay218(log){
 const prefix=log.filter(e=>e.window<=3),tail=log.filter(e=>e.window===4);replay217(prefix);
 if(prefix.length+tail.length!==log.length)throw Error('window corruption');
 const states=new Map(),pending=new Set();
 for(const e of prefix){
  if(['ESTABLISHED','RESERVED'].includes(e.type))states.set(e.id,{p:e.details.p,state:e.type==='RESERVED'?'reserved':'established'});
  else if(['QUALIFIED','PERSISTED'].includes(e.type))states.get(e.id).state='qualified';
  else if(e.type==='EXPIRED')states.get(e.id).state='expired';
  else if(e.type==='RELEASED')states.get(e.id).state='released';
  else if(e.type==='REOPENED')pending.add(e.id);
  else if(e.type==='PROBATION'){if(!pending.has(e.id))throw Error('unpaired probation');states.get(e.id).state='probation';pending.delete(e.id)}
  else if(e.type==='REQUALIFIED'){if(!pending.has(e.id))throw Error('unpaired requalification');states.get(e.id).state='qualified';pending.delete(e.id)}
  else if(e.type==='LOST')states.get(e.id).state='released';
 }
 if(pending.size)throw Error('open recovery');
 for(let j=0;j<tail.length;j++){
  const e=tail[j],s=states.get(e.id);if(e.seq!==prefix.length+j||!s)throw Error('invalid order or orphan');
  if(e.type==='CENSORED'){if(e.details.previous!==s.state)throw Error('censor state mismatch')}
  else if(e.type==='REQUALIFIED'){if(s.state!=='probation'||e.details.from!=='probation')throw Error('illegal requalification');s.state='qualified'}
  else if(e.type==='PROBATION_FAILED'){if(s.state!=='probation')throw Error('illegal probation failure');s.state='expired'}
  else if(e.type==='CONTINUED'){if(s.state!=='qualified')throw Error('illegal continuation')}
  else if(e.type==='LOST'){if(s.state!=='qualified')throw Error('illegal loss');s.state='released'}
  else if(e.type==='RECHECK_FAILED'){if(!['expired','released'].includes(s.state))throw Error('illegal failed recheck')}
  else throw Error('invalid event type');
 }
 return [...states.values()].filter(s=>s.state==='qualified').map(s=>s.p).sort((a,b)=>a-b);
}


// WAG-219 · provenance-aware censoring with probation lineage .dlw
const KINDS219=['stable','jitterB','dropB','flash_return'];
const MASKS219=['visible','random_half','burst','event_targeted','phase_targeted','anti_event'],SEEDS219=[215,221];
function fixture219(p,kind,seed,mask){
 const x=make217(p,kind,seed),g=x.g.slice(),rand=rng(seed*17+219);let missing=0;
 for(let i=768;i<960;i++){
  const hide=mask==='random_half'?((rand()>>>16)%2===0):
   mask==='burst'?(i>=816&&i<912):
   mask==='event_targeted'?g[i]===1:
   mask==='phase_targeted'?(((i-3)%p+p)%p===0):
   mask==='anti_event'?(g[i]===0&&(rand()>>>16)%4!==0):false;
  if(hide){g[i]=null;missing++}
 }
 return {g,expected:x.expected,provenance:{source:'synthetic:'+kind+':'+p+':'+seed,mask,
  missingSlots:missing,coverage:1-missing/192,eventCorrelated:['event_targeted','phase_targeted','anti_event'].includes(mask),
  origin:'fixture-provided sensor diagnostic, NOT inferred by agent'}};
}
function prior219(g){
 const prior=recover216(g.slice(0,768)),reopened=new Set(prior.log.filter(e=>e.type==='REOPENED').map(e=>e.id));
 return {states:prior.states.map(s=>({...s,state:reopened.has(s.id)&&s.state==='qualified'?'probation':s.state})),prior,reopened};
}
function evidence219(g,s,policy){
 const obs=[];for(let i=768;i<960;i++)if(g[i]===1)obs.push(i);
 let best=0,opportunities=0;
 for(let d=-3;d<=3;d++){
  const phase=((s.phase+d)%s.p+s.p)%s.p,pred=forecast({p:s.p,phase},768,960).filter(i=>policy==='blind'||g[i]!==null);
  const score=match(obs,pred).precision;
  if(score>best||score===best&&pred.length>opportunities){best=score;opportunities=pred.length}
 }
 return {precision:best,opportunities};
}
function classify219(g,prov,prior,policy='provenance'){
 const qualified=[],unverified=[],details=[];
 for(const s of prior.states){
  const m=evidence219(g,s,policy),censor=(policy==='provenance'&&prov.eventCorrelated)||
   (policy!=='blind'&&(prov.coverage<.5||m.opportunities<4));
  let next=s.state;
  if(censor){unverified.push(s.id);details.push({id:s.id,state:s.state,next,action:'SENSOR_CENSORED',precision:m.precision});}
  else if(['qualified','probation'].includes(s.state)){
   const threshold=s.state==='probation'?.7:.55;
   next=m.precision>=threshold?'qualified':s.state==='probation'?'expired':'released';
   details.push({id:s.id,state:s.state,next,action:'OBSERVED_RECHECK',precision:m.precision});
  }else details.push({id:s.id,state:s.state,next,action:'NOT_REOPENED',precision:m.precision});
  if(next==='qualified')qualified.push(s.p);
 }
 return {periods:qualified.sort((a,b)=>a-b),unverified,details};
}


const ATTACKS220=['truthful','false_coverage','stale','omitted','false_visible','consistent_forgery'],FAMILIES220=['stable','jitterB','dropB','flash_return'],MASKS220=['visible','burst','event_targeted'];
function claim220(x,attack){
 const actual=x.provenance,base={sensor:'s1',source:actual.source,window:4,observedSlots:192-actual.missingSlots,mask:actual.mask,reportedBias:actual.eventCorrelated};
 if(attack==='omitted')return null;
 if(attack==='false_coverage')base.observedSlots=Math.min(192,base.observedSlots+1);
 if(attack==='stale')base.window=3;
 if(attack==='false_visible')base.mask='visible';
 if(attack==='consistent_forgery'){base.mask='random_half';base.reportedBias=false}
 return base;
}
function audit220(g,report,expectedSource){
 const observedSlots=g.slice(768,960).filter(v=>v!==null).length,errors=[];
 if(!report)errors.push('MISSING_REPORT');
 else {
  if(report.window!==4)errors.push('STALE_WINDOW');
  if(report.source!==expectedSource)errors.push('SOURCE_ID_MISMATCH');
  if(report.observedSlots!==observedSlots)errors.push('COVERAGE_CONTRADICTION');
  if(report.mask==='visible'&&observedSlots!==192)errors.push('MASK_CONTRADICTION');
  if(!Number.isInteger(report.observedSlots)||report.observedSlots<0||report.observedSlots>192)errors.push('INVALID_COUNT');
 }
 return {status:errors.length?'QUARANTINE':'ACCEPT_UNVERIFIED',errors,observedSlots,reportedSlots:report?.observedSlots??null,scope:'internal metadata consistency only'};
}
function decide220(g,report,source,prior,mode='audit'){
 const audit=audit220(g,report,source);let decision;
 if(mode==='trust')decision=classify219(g,{coverage:(report?.observedSlots??0)/192,eventCorrelated:report?.reportedBias??false},prior,'provenance');
 else if(audit.status==='QUARANTINE'){
  decision={periods:prior.states.filter(s=>s.state==='qualified').map(s=>s.p).sort((a,b)=>a-b),unverified:prior.states.map(s=>s.id),details:prior.states.map(s=>({id:s.id,action:'QUARANTINE_SUSPENDED',next:s.state}))};
 }else decision=classify219(g,{coverage:audit.observedSlots/192,eventCorrelated:report.reportedBias},prior,'provenance');
 return {audit,...decision};
}
function experiment220(){
 const rows=[],examples=[],counterexamples=[];let cases=0,quarantines=0,undetectableForgeries=0,probationPromotions=0;
 for(const attack of ATTACKS220)for(const mask of MASKS220){
  let accepted=0,quarantined=0,modelMismatch=0,trustMismatch=0,forgeriesAccepted=0;
  for(const kind of FAMILIES220)for(const p of [9,23])for(const seed of [215,221]){
   const x=fixture219(p,kind,seed,mask),report=claim220(x,attack),prior=prior219(x.g);
   const audited=decide220(x.g,report,x.provenance.source,prior),trusted=decide220(x.g,report,x.provenance.source,prior,'trust');cases++;
   if(audited.audit.status==='QUARANTINE'){quarantined++;quarantines++}else accepted++;
   if(JSON.stringify(audited.periods)!==JSON.stringify(x.expected))modelMismatch++;
   if(JSON.stringify(trusted.periods)!==JSON.stringify(x.expected))trustMismatch++;
   if(attack==='consistent_forgery'&&audited.audit.status==='ACCEPT_UNVERIFIED'){forgeriesAccepted++;undetectableForgeries++}
   const pending=prior.states.filter(s=>s.state==='probation');
   if(audited.audit.status==='QUARANTINE'&&pending.some(s=>audited.periods.includes(s.p)))throw Error('probation promotion during quarantine');
   probationPromotions+=pending.filter(s=>audited.periods.includes(s.p)&&audited.audit.status==='QUARANTINE').length;
   if(audited.audit.status==='ACCEPT_UNVERIFIED'&&attack!=='truthful'&&examples.length<16)examples.push({kind,mask,p,seed,attack,report,audit:audited.audit,expected:x.expected,reported:audited.periods,observationWindow:x.g.slice(768)});
   if(JSON.stringify(audited.periods)!==JSON.stringify(x.expected)&&counterexamples.length<24)counterexamples.push({kind,mask,p,seed,attack,report,audit:audited.audit,expected:x.expected,reported:audited.periods,prior:prior.states.map(s=>({p:s.p,state:s.state})),observationWindow:x.g.slice(768)});
  }
  rows.push({attack,mask,runs:16,accepted,quarantined,modelMismatch,trustMismatch,forgeriesAccepted});
 }
 return {cases,quarantines,undetectableForgeries,probationPromotions,rows,examples,counterexamples};
}
if(typeof module!=='undefined')module.exports={claim220,audit220,decide220,experiment220};
if(typeof require!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment220(),null,2));
