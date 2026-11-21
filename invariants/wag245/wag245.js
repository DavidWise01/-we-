// WAG-234 cloned state paired rollouts; synthetic only; .dlw
const TRAIN234=[1001,1002,1003,1004,1005,1006],TEST234=[1101,1102,1103,1104,1105,1106,1107,1108],CAP234=[5,8,13,21],FAM234=['chirp','scar','famine','friction','combined','phaseflip','bursts'];
function clamp234(x){return Math.max(0,Math.min(1,x))}
function rng234(seed){let n=seed>>>0;return ()=>((n=(Math.imul(n,1664525)+1013904223)>>>0)/4294967296)}
function forcing234(family,seed){const random=rng234(seed),phase=random()*Math.PI*2;return Array.from({length:240},(_,t)=>{let p=.24;
if(family==='chirp')p=.49+.36*Math.sin(phase+.07*t+.001*t*t);
if(family==='scar')p=.25+(t>=55&&t<100?.70:0)+(t>=164&&t<195?.56:0);
if(family==='famine')p=.4+.22*Math.sin(phase+t*.14);
if(family==='friction')p=.42+.25*Math.sin(phase+t*.19);
if(family==='combined')p=.46+.31*Math.sin(phase+.07*t+.001*t*t)+(t>96&&t<135?.25:0);
if(family==='phaseflip')p=.5+.32*Math.sin(phase+.19*t+(t>=100?Math.PI:0));
if(family==='bursts')p=.19+((t%57)<9?.74:0)+.11*Math.sin(phase+.12*t);
p=clamp234(p);return {pressure:p,observed:clamp234(p+(random()-.5)*.09)}})}
function init234(){return {energy:.78,integrity:.91,ceiling:1,stress:0,protection:0,history:[],lastObserved:0,area:0,alive:0,reserve:0,trace:[],transitions:0,lastBand:'REST'}}
function clone234(s){return {...s,history:[...s.history],trace:[]}}
function shield234(cap){return cap>=13?.64:cap>=8?.46:.22}
function choices234(s,obs,cap){const hist=[...s.history,obs],eight=hist.slice(-8),mu=eight.reduce((a,b)=>a+b,0)/eight.length,v=eight.reduce((a,b)=>a+(b-mu)**2,0)/eight.length,jump=Math.abs(obs-(s.history.at(-1)??obs)),m=jump>.16||v>.035?3:v<.006?Math.min(21,cap):8,h=hist.slice(-m),stress=clamp234(.75*s.stress+.25*h.reduce((a,b)=>a+b,0)/h.length);
const danger=clamp234(.64*obs+.36*stress+Math.max(0,obs-s.lastObserved)*.30),urgency=clamp234((danger-.27)/.62),fragility=clamp234((.78-s.integrity)/.6),reserve=clamp234((.43-s.energy)/.43),risk=clamp234((.96-s.ceiling)*2),max=shield234(cap),desired=max*clamp234(.06+.83*urgency+.22*fragility+.12*risk-.30*reserve*(1-urgency)),emergency=danger>.79||s.integrity<.32,step=emergency?.22:.095,target=emergency?Math.max(desired,max*.65):desired,limit=x=>Math.max(0,Math.min(max,Math.max(s.protection-step,Math.min(s.protection+step,x))));
return {history:hist.slice(-21),stress,emergency,baseline:limit(target),alternative:limit(target*.45)}}
function tick234(s,forcing,t,cap,family,alternate=false){const {pressure,observed}=forcing[t],choice=choices234(s,observed,cap),p=alternate&&!choice.emergency?choice.alternative:choice.baseline,scarcity=family==='famine'||family==='combined',friction=family==='friction'||family==='combined',fee=(friction?.003+(.020*(1-s.energy))**2:.003)+(s.integrity<.55?.007:0),runCost=.0015+.029*Math.pow(p/.64,1.7),mod=fee*Math.abs(p-s.protection)/.64,raw=pressure*(1-p),gen=(.016+.0005*Math.min(cap,13)-.012*pressure)*(scarcity?(t>=62?.24:.75):1),damage=Math.max(0,raw-.31)*.034+(s.energy<.14?.012:0),repairBase=cap>=21?.02:cap>=13?.015:cap>=8?.012:.009,repair=Math.min(Math.max(0,s.ceiling-s.integrity),repairBase*Math.max(.22,s.energy)*(scarcity?.42:1)),scar=(family==='scar'||family==='combined')?.26:0;
s.ceiling=clamp234(s.ceiling-damage*scar);s.energy=clamp234(s.energy+gen-runCost-.011*raw-repair*.35-mod);s.integrity=Math.min(s.ceiling,clamp234(s.integrity-damage+repair));s.protection=p;s.history=choice.history;s.stress=choice.stress;s.lastObserved=observed;const band=p<.12?'REST':p<.4?'GUARD':'DEFEND';if(band!==s.lastBand)s.transitions++;s.lastBand=band;s.area+=s.integrity;const alive=s.integrity>.15&&s.energy>.08;if(alive)s.alive++;if(s.energy>.25&&s.integrity>.30)s.reserve++;
s.trace.push({t,pressure:+pressure.toFixed(5),energy:+s.energy.toFixed(5),integrity:+s.integrity.toFixed(5),protection:+p.toFixed(5),action:band,alternate:alternate&&!choice.emergency,alive});
if(s.energy<0||s.energy>1||s.integrity<0||s.integrity>s.ceiling+1e-10||p>shield234(cap)+1e-10)throw Error('state violation');return choice}
function bin234(s,obs){return (s.energy<.23?0:s.energy<.43?1:2)*3+(obs<.4?0:obs<.68?1:2)}


const TRAIN235=[1201,1202,1203,1204,1205,1206,1207,1208],TEST235=[1301,1302,1303,1304,1305,1306,1307,1308];
const FAMTRAIN235=['chirp','scar','famine','friction','combined'],FAMTEST235=['phaseflip','bursts'],ACT235=['conserve','hold','boost'];
function choice235(s,c,cap,a){if(c.emergency&&a!=='boost')return c.baseline;if(a==='conserve')return c.alternative;if(a==='hold')return s.protection;if(a==='boost')return Math.min(shield234(cap),c.baseline+.095);return c.baseline}
function step235(s,f,t,cap,family,a='baseline'){
const {pressure,observed}=f[t],c=choices234(s,observed,cap),p=choice235(s,c,cap,a),scarcity=family==='famine'||family==='combined',friction=family==='friction'||family==='combined',fee=(friction?.003+(.020*(1-s.energy))**2:.003)+(s.integrity<.55?.007:0),cost=.0015+.029*Math.pow(p/.64,1.7),mod=fee*Math.abs(p-s.protection)/.64,raw=pressure*(1-p),gen=(.016+.0005*Math.min(cap,13)-.012*pressure)*(scarcity?(t>=62?.24:.75):1),damage=Math.max(0,raw-.31)*.034+(s.energy<.14?.012:0),rbase=cap>=21?.02:cap>=13?.015:cap>=8?.012:.009,repair=Math.min(Math.max(0,s.ceiling-s.integrity),rbase*Math.max(.22,s.energy)*(scarcity?.42:1)),scar=(family==='scar'||family==='combined')?.26:0;
s.ceiling=clamp234(s.ceiling-damage*scar);s.energy=clamp234(s.energy+gen-cost-.011*raw-repair*.35-mod);s.integrity=Math.min(s.ceiling,clamp234(s.integrity-damage+repair));s.protection=p;s.history=c.history;s.stress=c.stress;s.lastObserved=observed;s.area+=s.integrity;const alive=s.integrity>.15&&s.energy>.08;if(alive)s.alive++;if(s.energy>.25&&s.integrity>.30)s.reserve++;const band=p<.12?'REST':p<.4?'GUARD':'DEFEND';if(band!==s.lastBand)s.transitions++;s.lastBand=band;s.trace.push({t,pressure:+pressure.toFixed(5),energy:+s.energy.toFixed(5),integrity:+s.integrity.toFixed(5),protection:+p.toFixed(5),action:a,alive});if(s.energy<0||s.energy>1||s.integrity<0||s.integrity>s.ceiling+1e-10||p>shield234(cap)+1e-10)throw Error('bounds');return cost+.011*raw+repair*.35+mod}
function branch235(s,f,t,cap,family,a){const x=clone234(s),y=clone234(s),end=Math.min(240,t+12);for(let k=t;k<end;k++){step235(x,f,k,cap,family);step235(y,f,k,cap,family,k===t?a:'baseline')}return (y.area-x.area)/(end-t)+.08*(y.energy-x.energy)+.006*(y.alive-x.alive)}
function train235(){const cells=Array.from({length:4},()=>Array.from({length:9},()=>Object.fromEntries(ACT235.map(a=>[a,{n:0,mean:0,m2:0}]))));let pairs=0;
for(let ci=0;ci<4;ci++)for(const family of FAMTRAIN235)for(const seed of TRAIN235){const cap=CAP234[ci],f=forcing234(family,seed),s=init234();for(let t=0;t<240;t++){if(t>=20&&t<=228&&t%5===0){const d=choices234(s,f[t].observed,cap),bin=bin234(s,f[t].observed);for(const a of ACT235){if(d.emergency&&a!=='boost')continue;if(Math.abs(choice235(s,d,cap,a)-d.baseline)<.004)continue;const v=branch235(s,f,t,cap,family,a),c=cells[ci][bin][a];c.n++;const diff=v-c.mean;c.mean+=diff/c.n;c.m2+=diff*(v-c.mean);pairs++}}step235(s,f,t,cap,family)}}
const table=cells.map((bands,i)=>bands.map((items,j)=>{const candidates=ACT235.map(a=>{const c=items[a],sd=c.n>1?Math.sqrt(c.m2/(c.n-1)):0,lower=c.n>1?c.mean-1.96*sd/Math.sqrt(c.n):null;return {action:a,n:c.n,mean:+c.mean.toFixed(8),lower:lower===null?null:+lower.toFixed(8)}});const best=candidates.filter(x=>x.n>=16&&x.lower>.00012).sort((x,y)=>y.lower-x.lower)[0];return {capacity:CAP234[i],bin:j,choice:best?.action??'baseline',candidates}}));return {trainingSeeds:TRAIN235,trainingFamilies:FAMTRAIN235,pairs,approved:table.flat().filter(x=>x.choice!=='baseline').length,table}}
function simulate235(cap,family,seed,mode,model){const f=forcing234(family,seed),s=init234(),ci=CAP234.indexOf(cap),choices={baseline:0,conserve:0,hold:0,boost:0};for(let t=0;t<240;t++){let a='baseline';if(mode==='learned'){const d=choices234(s,f[t].observed,cap);if(!d.emergency){a=model.table[ci][bin234(s,f[t].observed)].choice;if(Math.abs(choice235(s,d,cap,a)-d.baseline)<.004)a='baseline'}}choices[a]++;step235(s,f,t,cap,family,a)}return {capacity:cap,scenario:family,seed,mode,meanIntegrity:+(s.area/240).toFixed(6),finalEnergy:+s.energy.toFixed(6),aliveTicks:s.alive,reserveTicks:s.reserve,choices,trace:s.trace}}
function simulate236(cap,family,seed,mode,model){const f=forcing234(family,seed),s=init234(),ci=CAP234.indexOf(cap),choices={baseline:0,conserve:0,hold:0,boost:0};let blocked=0;const historyDelta=[];for(let t=0;t<240;t++){let a='baseline';if(mode==='viability'||mode==='learned'){const d=choices234(s,f[t].observed,cap);if(!d.emergency){a=model.table[ci][bin234(s,f[t].observed)].choice;if(Math.abs(choice235(s,d,cap,a)-d.baseline)<.004)a='baseline';
   if(mode==='viability'&&a==='boost'){
    const recent=historyDelta.slice(-8),rate=recent.length?recent.reduce((x,y)=>x+y,0)/recent.length:0;
    const projected=s.energy+12*Math.min(0,rate);
    const floor=.35+Math.min(.2,Math.max(0,-rate)*14);
    if(s.energy<floor||projected<.28){a='baseline';blocked++}
   }}}const previous=s.energy;choices[a]++;step235(s,f,t,cap,family,a);historyDelta.push(s.energy-previous)}return {capacity:cap,scenario:family,seed,mode,meanIntegrity:+(s.area/240).toFixed(6),finalEnergy:+s.energy.toFixed(6),aliveTicks:s.alive,reserveTicks:s.reserve,choices,blocked,trace:s.trace}}
function simulate237(cap,family,seed,mode,model){const f=forcing234(family,seed),s=init234(),ci=CAP234.indexOf(cap),choices={baseline:0,conserve:0,hold:0,boost:0};let blocked=0,early=0,late=0,minimum=1,underSafety=0;const historyDelta=[],pressureHistory=[];for(let t=0;t<240;t++){let a='baseline';if(mode==='survival'||mode==='viability'||mode==='learned'){const d=choices234(s,f[t].observed,cap);if(!d.emergency){a=model.table[ci][bin234(s,f[t].observed)].choice;if(Math.abs(choice235(s,d,cap,a)-d.baseline)<.004)a='baseline';
   if(mode==='survival'&&a==='boost'){
 const recent=historyDelta.slice(-12),rate=recent.length?recent.reduce((x,y)=>x+y,0)/recent.length:0;
 const vol=pressureHistory.length?Math.sqrt(pressureHistory.slice(-12).reduce((v,x)=>v+(x-f[t].observed)**2,0)/Math.min(12,pressureHistory.length)):0;
 const boost=choice235(s,d,cap,'boost'),extra=Math.max(0,.029*(Math.pow(boost/.64,1.7)-Math.pow(d.baseline/.64,1.7)));
 const estimate=s.energy+24*(Math.min(0,rate)-extra-.003-.009*Math.min(1,vol));
 if(estimate<.27+(s.integrity<.55?.08:0)||s.energy<.36){a='baseline';blocked++;if(s.energy>.36)early++;else late++}
 }
 if(mode==='viability'&&a==='boost'){
    const recent=historyDelta.slice(-8),rate=recent.length?recent.reduce((x,y)=>x+y,0)/recent.length:0;
    const projected=s.energy+12*Math.min(0,rate);
    const floor=.35+Math.min(.2,Math.max(0,-rate)*14);
    if(s.energy<floor||projected<.28){a='baseline';blocked++}
   }}}const previous=s.energy;choices[a]++;step235(s,f,t,cap,family,a);historyDelta.push(s.energy-previous);pressureHistory.push(f[t].observed);minimum=Math.min(minimum,s.energy);if(s.energy<.27)underSafety++}return {capacity:cap,scenario:family,seed,mode,meanIntegrity:+(s.area/240).toFixed(6),finalEnergy:+s.energy.toFixed(6),aliveTicks:s.alive,reserveTicks:s.reserve,choices,blocked,early,late,minEnergy:+minimum.toFixed(6),underSafety,trace:s.trace}}

const TEST238=[1601,1602,1603,1604,1605,1606,1607,1608];
function simulate238(cap,family,seed,mode,model){
 if(mode==='survival')return simulate237(cap,family,seed,'survival',model);
 if(mode==='viability')return simulate236(cap,family,seed,'viability',model);
 if(mode==='learned')return simulate235(cap,family,seed,'learned',model);
 if(mode==='graded')return simulate235(cap,family,seed,'graded',model);
 const f=forcing234(family,seed),s=init234(),ci=CAP234.indexOf(cap);
 const history=[],choices={baseline:0,conserve:0,hold:0,boost:0},classificationCounts={insufficient:0,temporary:0,sufficient:0,unknown:0};
 let blocked=0,minimum=1,underSafety=0,forecastErrors=0,errorN=0;
 const pending=[];
 for(let t=0;t<240;t++){
  const current=f[t],decision=choices234(s,current.observed,cap);
  let action=decision.emergency?'baseline':model.table[ci][bin234(s,current.observed)].choice;
  if(action!=='baseline'&&Math.abs(choice235(s,decision,cap,action)-decision.baseline)<.004)action='baseline';
  // Observed source generation is reconstructed from measured changes and
  // bookkeeping of actuator/repair costs, never from hidden scenario identity.
  // Previous receipts with energy saturation are censored.
  const receipt=history.filter(v=>v.valid);
  const short=receipt.slice(-10),long=receipt.slice(-24);
  const avg=x=>x.length?x.reduce((a,b)=>a+b,0)/x.length:0;
  const minimumCost=.0015+.011*current.observed+0.001;
  const shortNet=avg(short.map(x=>x.generation))-minimumCost;
  const longNet=avg(long.map(x=>x.generation))-minimumCost;
  let status='unknown';
  if(long.length>=12&&short.length>=6){
   if(shortNet<-.001&&longNet<-.001)status='insufficient';
   else if(shortNet<-.001)status='temporary';
   else status='sufficient';
  }
  classificationCounts[status]++;
  if(action==='boost'&&(status==='insufficient'||(status==='temporary'&&s.energy<.55))){
    action='baseline';blocked++;
  }
  // Keep emergency defense from graded WAG-230. The controller does not assume
  // a negative budget can be repaired without additional resource generation.
  const energyBefore=s.energy;
  choices[action]++;
  // Instrumented actuator reports its completed, realized operating outlay.
  // The controller does not inspect the hidden environment family.
  const cost=step235(s,f,t,cap,family,action);
  const delta=s.energy-energyBefore;
  const valid=energyBefore>.02&&s.energy>.02&&energyBefore<.98&&s.energy<.98;
  const reconstructed=valid?delta+cost:null;
  history.push({valid,generation:reconstructed});
  minimum=Math.min(minimum,s.energy);if(s.energy<.27)underSafety++;
  pending.push({due:t+12,forecast:Math.max(0,Math.min(1,energyBefore+12*shortNet))});
  if(t>=12){const p=pending[t-12];if(p&&p.due===t){forecastErrors+=Math.abs(s.energy-p.forecast);errorN++}}
  s.trace[s.trace.length-1].resourceState=status;
  s.trace[s.trace.length-1].observedBudget=+shortNet.toFixed(6);
  s.trace[s.trace.length-1].receiptValid=valid;
 }
 return {capacity:cap,scenario:family,seed,mode:'sufficiency',meanIntegrity:+(s.area/240).toFixed(6),finalEnergy:+s.energy.toFixed(6),aliveTicks:s.alive,reserveTicks:s.reserve,choices,classificationCounts,blocked,minEnergy:+minimum.toFixed(6),underSafety,forecastMAE:errorN?+(forecastErrors/errorN).toFixed(6):null,validReceipts:history.filter(x=>x.valid).length,trace:s.trace};
}
function step239(s,f,t,cap,family,a='baseline',demand=false){
const {pressure,observed}=f[t],c=choices234(s,observed,cap),p=choice235(s,c,cap,a)*(demand?.87:1),scarcity=family==='famine'||family==='combined',friction=family==='friction'||family==='combined',fee=(friction?.003+(.020*(1-s.energy))**2:.003)+(s.integrity<.55?.007:0),cost=(.0015+.029*Math.pow(p/.64,1.7))*(demand?.72:1),mod=fee*Math.abs(p-s.protection)/.64,raw=pressure*(1-p),gen=(.016+.0005*Math.min(cap,13)-.012*pressure)*(scarcity?(t>=62?.24:.75):1),damage=Math.max(0,raw-.31)*.034+(s.energy<.14?.012:0),rbase=cap>=21?.02:cap>=13?.015:cap>=8?.012:.009,repair=Math.min(Math.max(0,s.ceiling-s.integrity),rbase*Math.max(.22,s.energy)*(scarcity?.42:1)),scar=(family==='scar'||family==='combined')?.26:0;
s.ceiling=clamp234(s.ceiling-damage*scar);s.energy=clamp234(s.energy+gen-cost-.011*raw-repair*.35-mod);s.integrity=Math.min(s.ceiling,clamp234(s.integrity-damage+repair));s.protection=p;s.history=c.history;s.stress=c.stress;s.lastObserved=observed;s.area+=s.integrity;const alive=s.integrity>.15&&s.energy>.08;if(alive)s.alive++;if(s.energy>.25&&s.integrity>.30)s.reserve++;const band=p<.12?'REST':p<.4?'GUARD':'DEFEND';if(band!==s.lastBand)s.transitions++;s.lastBand=band;s.trace.push({t,pressure:+pressure.toFixed(5),energy:+s.energy.toFixed(5),integrity:+s.integrity.toFixed(5),protection:+p.toFixed(5),action:a,alive});if(s.energy<0||s.energy>1||s.integrity<0||s.integrity>s.ceiling+1e-10||p>shield234(cap)+1e-10)throw Error('bounds');return cost+.011*raw+repair*.35+mod}


const SEEDS240=[1801,1802,1803,1804],DURATIONS240=[240,480,960,1920],MODES240=['renewable','finite','passive'];
function forcing240(family,seed,duration){const result=[];for(let b=0;b<Math.ceil(duration/240);b++)result.push(...forcing234(family,seed+b*7919));return result.slice(0,duration)}
function supply240(t,phase){return .0018+.0075*Math.max(0,Math.sin(2*Math.PI*t/96+phase))}

/* WAG-244 · cloned-state maintenance action rollouts · deterministic synthetic evidence · .dlw */
const TRAIN244=[2201,2202,2203,2204],TEST244=[2301,2302,2303,2304],DUR244=[240,480,960,1920];
const FAMILIES_TRAIN244=['chirp','scar','famine','friction','combined'],FAMILIES_HOLD244=['phaseflip','bursts'],ACTIONS244=['prevent','rebuild','abstain'];
function start244(cap,family,seed,duration){
 return {cap,family,seed,duration,t:0,f:forcing240(family,seed,duration),s:init234(),material:.2,materialIn:0,materialWaste:0,materialSpent:0,cache:.2,energyIn:0,energyWaste:0,energyFlux:0,energyWithdrawn:0,energyDelivered:0,transferLost:0,fees:0,energyOverflow:0,queue:[],history:[],scarMean:0,previousCeiling:1,choices:{prevent:0,rebuild:0,abstain:0},samples:0};
}
function clone244(x){
 return {...x,s:{...x.s,history:[...x.s.history],trace:[]},f:x.f,queue:x.queue.map(y=>({...y})),history:x.history.map(y=>({...y})),choices:{...x.choices}};
}
function bin244(x){
 const obs=x.f[x.t].observed,energy=x.s.energy,scar=1-x.s.ceiling;
 return (energy<.43?0:1)*6+(obs<.4?0:obs<.68?1:2)*2+(scar<.04?0:1);
}
function step244(x,repair='abstain'){
 const t=x.t,{s,cap,family,seed}=x,f=x.f;
 const flux=supply240(t,(seed%29)*Math.PI/29);x.energyFlux+=flux;
 const addMaterial=Math.min(.0009,Math.max(0,.5-x.material));
 x.material+=addMaterial;x.materialIn+=addMaterial;x.materialWaste+=.0009-addMaterial;
 const harvest=Math.min(flux,Math.max(0,.45-x.cache));x.cache+=harvest;x.energyIn+=harvest;x.energyWaste+=flux-harvest;
 const arriving=x.queue.filter(z=>z.due===t).reduce((a,b)=>a+b.amount*.84,0);x.energyDelivered+=arriving;
 const before=s.energy,valid=x.history.filter(z=>z.valid),last10=valid.slice(-10),last24=valid.slice(-24);
 const avg=arr=>arr.length?arr.reduce((a,b)=>a+b,0)/arr.length:0;
 const shortNet=avg(last10.map(z=>z.generated))-(.0025+.011*f[t].observed);
 const longNet=avg(last24.map(z=>z.generated))-(.0025+.011*f[t].observed);
 const status=last24.length<12?'unknown':shortNet<-.001?(longNet<-.001?'insufficient':'temporary'):'sufficient';
 const trend=avg(x.history.slice(-8).map(z=>z.delta));
 const decision=choices234(s,f[t].observed,cap);
 let action='baseline';
 if(!decision.emergency){action=x.modelTable[CAP234.indexOf(cap)][bin234(s,f[t].observed)].choice;if(Math.abs(choice235(s,decision,cap,action)-decision.baseline)<.004)action='baseline'}
 const low=before<.49||status==='insufficient'||status==='temporary';
 if(low&&!decision.emergency&&action==='boost')action='baseline';
 let requested=false;
 if(x.cache>=.002&&before<.68&&(status==='insufficient'||status==='temporary'||before+12*Math.min(0,trend)<.36)){
  const q=Math.min(x.cache,.012);x.cache-=q;x.energyWithdrawn+=q;x.transferLost+=q*.16;x.queue.push({due:t+3,amount:q});requested=true;x.fees+=.001;
 }
 const eligible=before>.14&&s.integrity>.15;
 const canPrevent=eligible&&f[t].observed>.55&&x.material>=.0015;
 const canRebuild=eligible&&s.ceiling<.995&&x.material>=.0035&&before>.35;
 const applied=repair==='prevent'&&canPrevent?'prevent':repair==='rebuild'&&canRebuild?'rebuild':'abstain';
 const ceilingBefore=s.ceiling;
 const actualExtra=applied==='prevent'?.0012:applied==='rebuild'?.004:0;
 const materialCost=applied==='prevent'?.0015:applied==='rebuild'?.0035:0;
 x.material-=materialCost;x.materialSpent+=materialCost;x.choices[applied]++;
 const baseCost=step239(s,f,t,cap,family,action,low&&!decision.emergency);
 if(applied==='prevent')s.ceiling=clamp234(s.ceiling+.72*Math.max(0,ceilingBefore-s.ceiling));
 if(applied==='rebuild'){const built=Math.min(.0025,1-s.ceiling);s.ceiling=clamp234(s.ceiling+built);s.integrity=Math.min(s.ceiling,s.integrity+Math.min(.0012,built))}
 s.area+=s.integrity-s.trace.at(-1).integrity;
 s.energy=clamp234(s.energy-actualExtra);
 const gross=s.energy+arriving-(requested?.001:0);
 if(gross>1)x.energyOverflow+=gross-1;
 s.energy=clamp234(gross);
 const isValid=before>.02&&before<.98&&s.energy>.02&&s.energy<.98&&!requested&&arriving===0;
 x.history.push({valid:isValid,generated:isValid?s.energy-before+baseCost+actualExtra:null,delta:s.energy-before});
 x.scarMean=.93*x.scarMean+.07*Math.max(0,x.previousCeiling-s.ceiling);
 x.previousCeiling=s.ceiling;
 const trace=s.trace.at(-1);trace.energy=+s.energy.toFixed(5);trace.integrity=+s.integrity.toFixed(5);trace.ceiling=+s.ceiling.toFixed(5);trace.material=+x.material.toFixed(5);trace.cache=+x.cache.toFixed(5);trace.maintenance=applied;trace.resourceClass=status;
 x.t++;
}
function simulate244(cap,family,seed,duration,mode,model){
 const x=start244(cap,family,seed,duration);x.modelTable=model.table;
 let opportunities=0,approved=0;
 while(x.t<duration){
  const t=x.t,d=choices234(x.s,x.f[t].observed,cap);
  let a='abstain';
  if(mode==='trained'){
    a=model.table244[CAP234.indexOf(cap)][bin244(x)].action;
    if(a!=='abstain')approved++;
  }else if(mode==='priority'){
    const scar=1-x.s.ceiling,energy=x.s.energy,pressure=x.f[t].observed;
    // Reproduction of WAG-243's observed value ranking in simplified engine.
    if(energy>.43&&scar>.012&&x.material>.025)a='rebuild';
  }else if(mode==='hybrid'){
    if(x.f[t].observed>.55&&x.s.energy>.12)a='prevent';
    else if(x.s.ceiling<.995&&x.s.energy>.35)a='rebuild';
  }
  if(x.s.energy>.4&&x.material>.02)opportunities++;
  step244(x,a);
 }
 const pending=x.queue.filter(z=>z.due>=duration).reduce((sum,z)=>sum+z.amount,0);
 const energyError=Math.max(Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),Math.abs(x.energyFlux-x.energyIn-x.energyWaste),Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84));
 const materialError=Math.max(Math.abs(.2+x.materialIn-x.materialSpent-x.material),Math.abs(duration*.0009-x.materialIn-x.materialWaste));
 if(energyError>1e-8||materialError>1e-8)throw Error('WAG-244 conservation failed '+energyError+'/'+materialError);
 const alive=x.s.trace.filter(z=>z.energy>.08&&z.integrity>.15).length,reserve=x.s.trace.filter(z=>z.energy>.25&&z.integrity>.30).length;
 return {capacity:cap,scenario:family,seed,duration,mode,meanIntegrity:+(x.s.area/duration).toFixed(6),finalEnergy:+x.s.energy.toFixed(6),finalIntegrity:+x.s.integrity.toFixed(6),recoverableCeiling:+x.s.ceiling.toFixed(6),aliveTicks:alive,reserveTicks:reserve,materialUsed:+x.materialSpent.toFixed(6),materialLeft:+x.material.toFixed(6),harvested:+x.energyIn.toFixed(6),transferLost:+x.transferLost.toFixed(6),maintenance:x.choices,approved,opportunities,energyError,materialError,trace:x.s.trace};
}
function branch244(x,action,horizon=12){
 const c=clone244(x);const start=c.t,end=Math.min(start+horizon,c.duration);
 const firstAction=action;
 while(c.t<end)step244(c,c.t===start?firstAction:'abstain');
 const n=end-start;
 return {score:c.s.area/n+.22*c.s.energy+.028*c.s.alive+.035*c.material,energy:c.s.energy,material:c.material,integrity:c.s.area/n,alive:c.s.alive};
}
function train244(){
 const source=train235(),cells=CAP234.map(()=>Array.from({length:12},()=>Object.fromEntries(['prevent','rebuild'].map(a=>[a,{n:0,mean:0,m2:0,wins:0,losses:0}]))));
 let pairs=0,sampled=0;
 for(const cap of CAP234)for(const family of FAMILIES_TRAIN244)for(const seed of TRAIN244){
  const x=start244(cap,family,seed,240);x.modelTable=source.table;
  while(x.t<240){
   if(x.t>=24&&x.t<=228&&x.t%9===0){
    const i=CAP234.indexOf(cap),bin=bin244(x),base=branch244(x,'abstain');
    for(const action of ['prevent','rebuild']){
     const d=choices234(x.s,x.f[x.t].observed,cap);
     const eligible=action==='prevent'?x.f[x.t].observed>.55&&x.s.energy>.14&&x.material>=.0015:x.s.ceiling<.995&&x.s.energy>.35&&x.material>=.0035&&x.s.integrity>.15;
     if(!eligible)continue;
     const val=branch244(x,action).score-base.score,c=cells[i][bin][action];
     c.n++;const dx=val-c.mean;c.mean+=dx/c.n;c.m2+=dx*(val-c.mean);if(val>0)c.wins++;else if(val<0)c.losses++;pairs++;
    }
    sampled++;
   }
   step244(x,'abstain');
  }
 }
 const table244=cells.map((bins,i)=>bins.map((cell,bin)=>{
  const estimates=['prevent','rebuild'].map(action=>{const c=cell[action],sd=c.n>1?Math.sqrt(c.m2/(c.n-1)):0,lower=c.n>1?c.mean-1.64*sd/Math.sqrt(c.n):null;return {action,n:c.n,mean:+c.mean.toFixed(7),lower:lower===null?null:+lower.toFixed(7),wins:c.wins,losses:c.losses}});
  const choices=estimates.filter(z=>z.n>=10&&z.lower>.00008).sort((a,b)=>b.lower-a.lower);
  return {capacity:CAP234[i],bin,action:choices[0]?.action??'abstain',estimates};
 }));
 return {table:source.table,table244,pairs,sampled,trainSeeds:TRAIN244,trainingFamilies:FAMILIES_TRAIN244,selected:table244.flat().reduce((a,x)=>(a[x.action]=(a[x.action]||0)+1,a),{})};
}
function simulate245(cap,family,seed,duration,mode,model){
 const x=start244(cap,family,seed,duration);x.modelTable=model.table;
 let opportunities=0,approved=0;
 while(x.t<duration){
  const t=x.t,d=choices234(x.s,x.f[t].observed,cap);
  let a='abstain';
  if(mode==='long'){
    a=model.table245[CAP234.indexOf(cap)][bin244(x)].action;
    if(a!=='abstain')approved++;
  }else if(mode==='priority'){
    const scar=1-x.s.ceiling,energy=x.s.energy,pressure=x.f[t].observed;
    // Reproduction of WAG-243's observed value ranking in simplified engine.
    if(energy>.43&&scar>.012&&x.material>.025)a='rebuild';
  }else if(mode==='hybrid'){
    if(x.f[t].observed>.55&&x.s.energy>.12)a='prevent';
    else if(x.s.ceiling<.995&&x.s.energy>.35)a='rebuild';
  }
  if(x.s.energy>.4&&x.material>.02)opportunities++;
  step244(x,a);
 }
 const pending=x.queue.filter(z=>z.due>=duration).reduce((sum,z)=>sum+z.amount,0);
 const energyError=Math.max(Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),Math.abs(x.energyFlux-x.energyIn-x.energyWaste),Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84));
 const materialError=Math.max(Math.abs(.2+x.materialIn-x.materialSpent-x.material),Math.abs(duration*.0009-x.materialIn-x.materialWaste));
 if(energyError>1e-8||materialError>1e-8)throw Error('WAG-244 conservation failed '+energyError+'/'+materialError);
 const alive=x.s.trace.filter(z=>z.energy>.08&&z.integrity>.15).length,reserve=x.s.trace.filter(z=>z.energy>.25&&z.integrity>.30).length;
 return {capacity:cap,scenario:family,seed,duration,mode,meanIntegrity:+(x.s.area/duration).toFixed(6),finalEnergy:+x.s.energy.toFixed(6),finalIntegrity:+x.s.integrity.toFixed(6),recoverableCeiling:+x.s.ceiling.toFixed(6),aliveTicks:alive,reserveTicks:reserve,materialUsed:+x.materialSpent.toFixed(6),materialLeft:+x.material.toFixed(6),harvested:+x.energyIn.toFixed(6),transferLost:+x.transferLost.toFixed(6),maintenance:x.choices,approved,opportunities,energyError,materialError,trace:x.s.trace};
}

const TRAIN245=[2401,2402,2403,2404],TEST245=[2501,2502,2503,2504],HORIZONS245=[12,48,192],DUR245=[240,480,960,1920];
function branchMetrics245(x,action,horizon){
 const y=clone244(x),end=Math.min(y.duration,y.t+horizon),start=y.t;
 let integralEnergy=0,reserve=0,alive=0,minimum=1;
 while(y.t<end){
  step244(y,y.t===start?action:'abstain');
  integralEnergy+=y.s.energy;
  if(y.s.energy>.25&&y.s.integrity>.30)reserve++;
  if(y.s.energy>.08&&y.s.integrity>.15)alive++;
  minimum=Math.min(minimum,y.s.energy);
 }
 return {meanIntegrity:(y.s.area-x.s.area)/(end-start),meanEnergy:integralEnergy/(end-start),finalEnergy:y.s.energy,integralReserve:reserve,integralAlive:alive,minimumEnergy:minimum,finalMaterial:y.material,finalCeiling:y.s.ceiling};
}
function train245(){
 const orig=train235(),cells=CAP234.map(()=>Array.from({length:12},()=>Object.fromEntries(['prevent','rebuild'].map(a=>[a,Object.fromEntries(HORIZONS245.map(h=>[h,{n:0,mean:0,m2:0,meanReserve:0,meanAlive:0,meanFinalEnergy:0,meanMaterial:0,positive:0,negative:0}]))]))));
 let snapshots=0,pairs=0;
 for(const cap of CAP234)for(const family of FAMILIES_TRAIN244)for(const seed of TRAIN245){
  const x=start244(cap,family,seed,240);x.modelTable=orig.table;
  while(x.t<240){
   if(x.t>=24&&x.t<=48&&x.t%12===0){
    const ci=CAP234.indexOf(cap),bin=bin244(x);
    const baselines=Object.fromEntries(HORIZONS245.map(h=>[h,branchMetrics245(x,'abstain',h)]));
    for(const action of ['prevent','rebuild']){
     const qualified=action==='prevent'?x.f[x.t].observed>.55&&x.s.energy>.14&&x.material>=.0015:x.s.ceiling<.995&&x.s.energy>.35&&x.material>=.0035&&x.s.integrity>.15;
     if(!qualified)continue;
     for(const h of HORIZONS245){
      const a=branchMetrics245(x,action,h),b=baselines[h],z=cells[ci][bin][action][h],n=h;
      const deltaIntegrity=a.meanIntegrity-b.meanIntegrity;
      const deltaReserve=(a.integralReserve-b.integralReserve)/n;
      const deltaAlive=(a.integralAlive-b.integralAlive)/n;
      const deltaFinalEnergy=a.finalEnergy-b.finalEnergy;
      const deltaMaterial=a.finalMaterial-b.finalMaterial;
      // High priority: future survival and reserve, not only repair integrity.
      const value=deltaIntegrity+.25*deltaReserve+.5*deltaAlive+.18*deltaFinalEnergy+.04*deltaMaterial;
      z.n++;const change=value-z.mean;z.mean+=change/z.n;z.m2+=change*(value-z.mean);
      z.meanReserve+=(deltaReserve-z.meanReserve)/z.n;
      z.meanAlive+=(deltaAlive-z.meanAlive)/z.n;
      z.meanFinalEnergy+=(deltaFinalEnergy-z.meanFinalEnergy)/z.n;
      z.meanMaterial+=(deltaMaterial-z.meanMaterial)/z.n;
      if(value>1e-10)z.positive++;else if(value< -1e-10)z.negative++;pairs++;
     }
    }
    snapshots++;
   }
   step244(x,'abstain');
  }
 }
 const table245=cells.map((bins,ci)=>bins.map((cell,bin)=>{
  const candidates=['prevent','rebuild'].map(action=>{
   const metrics=HORIZONS245.map(h=>{
    const z=cell[action][h],sd=z.n>1?Math.sqrt(z.m2/(z.n-1)):0;
    return {horizon:h,n:z.n,mean:+z.mean.toFixed(8),lower:z.n>1?+(z.mean-1.64*sd/Math.sqrt(z.n)).toFixed(8):null,meanReserve:+z.meanReserve.toFixed(6),meanAlive:+z.meanAlive.toFixed(6),meanFinalEnergy:+z.meanFinalEnergy.toFixed(6),meanMaterial:+z.meanMaterial.toFixed(6),positive:z.positive,negative:z.negative};
   });
   const short=metrics[0],mid=metrics[1],long=metrics[2];
   const accepted=long.n>=8&&long.lower!==null&&long.lower>.00005&&mid.lower!==null&&mid.lower>-.00015&&short.lower!==null&&short.lower>-.0002&&long.meanReserve>=-.003&&long.meanAlive>=-.003&&long.meanFinalEnergy>=-.035;
   return {action,accepted,metrics};
  });
  const candidate=candidates.filter(x=>x.accepted).sort((a,b)=>b.metrics[2].lower-a.metrics[2].lower)[0];
  return {capacity:CAP234[ci],bin,action:candidate?.action??'abstain',candidates};
 }));
 return {table:orig.table,table245,trainSeeds:TRAIN245,families:FAMILIES_TRAIN244,horizons:HORIZONS245,snapshots,pairs,selected:table245.flat().reduce((z,r)=>(z[r.action]=(z[r.action]||0)+1,z),{})};
}
function experiment245(){
 const model=train245(),oldPolicy=train244(),groups=[{name:'familiar',families:FAMILIES_TRAIN244},{name:'withheld',families:FAMILIES_HOLD244}],modes=['long','trained','hybrid','abstain'],rows=[],counterexamples=[],examples=[],comparison={};
 let runs=0,ticks=0,appliedPrevent=0,appliedRebuild=0,maxLedgerError=0;
 for(const duration of DUR245){
  comparison[duration]={familiar:{},withheld:{}};
  for(const group of groups){
   for(const b of ['trained','hybrid','abstain'])comparison[duration][group.name][b]={wins:0,losses:0,ties:0};
   for(const cap of CAP234)for(const family of group.families){
    const sums=Object.fromEntries(modes.map(m=>[m,{meanIntegrity:0,finalEnergy:0,finalIntegrity:0,aliveTicks:0,reserveTicks:0,materialUsed:0}]));
    for(const seed of TEST245){
     const p={long:simulate245(cap,family,seed,duration,'long',model),trained:simulate244(cap,family,seed,duration,'trained',oldPolicy),hybrid:simulate245(cap,family,seed,duration,'hybrid',model),abstain:simulate245(cap,family,seed,duration,'abstain',model)};
     runs+=4;ticks+=4*duration;const a=p.long;
     appliedPrevent+=a.maintenance.prevent;appliedRebuild+=a.maintenance.rebuild;maxLedgerError=Math.max(maxLedgerError,a.energyError,a.materialError);
     for(const m of modes)for(const k of Object.keys(sums[m]))sums[m][k]+=p[m][k];
     for(const b of ['trained','hybrid','abstain']){
      const delta=a.meanIntegrity-p[b].meanIntegrity,z=comparison[duration][group.name][b];
      if(delta>1e-6)z.wins++;else if(delta< -1e-6)z.losses++;else z.ties++;
     }
     if(a.meanIntegrity<p.abstain.meanIntegrity-1e-6||a.aliveTicks<p.abstain.aliveTicks||a.reserveTicks<p.abstain.reserveTicks)
      counterexamples.push({duration,group:group.name,capacity:cap,family,seed,policies:Object.fromEntries(modes.map(m=>[m,{integrity:p[m].meanIntegrity,energy:p[m].finalEnergy,alive:p[m].aliveTicks,reserve:p[m].reserveTicks,material:p[m].materialUsed}]))});
     if(seed===2501&&cap===13&&['scar','combined','famine'].includes(family))examples.push({duration,group:group.name,capacity:cap,family,long:{...a,trace:a.trace.filter((v,i)=>i%12===0||i===a.trace.length-1)},trained:{...p.trained,trace:undefined},hybrid:{...p.hybrid,trace:undefined},abstain:{...p.abstain,trace:undefined}});
    }
    rows.push({duration,group:group.name,capacity:cap,family,average:Object.fromEntries(modes.map(m=>[m,Object.fromEntries(Object.entries(sums[m]).map(([k,v])=>[k,+(v/TEST245.length).toFixed(6)]))]))});
   }
  }
 }
 return {bound:'WAG-245',training:model,testSeeds:TEST245,durations:DUR245,policyRuns:runs,ticks,appliedPrevent,appliedRebuild,maxLedgerError,comparison,rows,counterexamples,examples};
}
if(typeof module!=='undefined')module.exports={train245,simulate245,experiment245};
if(typeof require!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment245(),null,2));
