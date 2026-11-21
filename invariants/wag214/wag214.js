// WAG-214 extends WAG-212 component persistence — .dlw; one observation ancestry
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
function experiment214(){
 let checks=0;const rows=[],counterexamples=[];
 for(const kind of ['stable','jitterB','shiftB','replace','ephemeral','dropA','dropB','bothDrop','mixedTransient','harmonic'])for(const policy of ['provisional','verified']){
 let correct=0,wrong=0,unknown=0,proposalBirth=0;
 for(const p of PERIODS)for(let seed=214;seed<230;seed++){
  const {g,expected}=make214(p,kind,seed),r=qualify214(g,policy);checks+=g.length;
  if(r.candidate.components.some(c=>!r.original.components.some(o=>o.p===c.p)))proposalBirth++;
  if(JSON.stringify(r.components)===JSON.stringify(expected))correct++;
  else if(!r.components.length)unknown++;
  else{wrong++;if(counterexamples.length<48)counterexamples.push({kind,policy,p,seed,expected,reported:r.components,original:r.original.components,candidate:r.candidate.components,qualified:r.qualified,eventPositions:events(g,0,576),binary:g.join('')})}
 }
 rows.push({kind,policy,runs:64,correct,wrong,unknown,proposalBirth});
 }
 return {observationSlots:checks,rows,counterexamples};
}
if(typeof module!=='undefined')module.exports={make214,proposeWindow,qualify214,experiment214};
if(typeof require!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment214(),null,2));
