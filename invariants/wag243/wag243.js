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
function simulate242(cap,family,seed,duration,mode,model){
 const f=forcing240(family,seed,duration),s=init234(),ci=CAP234.indexOf(cap),queue=[],history=[],choices={baseline:0,boost:0,hold:0,conserve:0};
 let deniedPrevent=0,deniedRebuild=0,affordabilityDecisions=0,observedScar=0,scarSamples=0,previousCeiling=1;let material=.20,materialIn=0,materialSpilled=0,materialUsed=0,preventTicks=0,rebuildTicks=0,avoidedScar=0,reconstructed=0,repairEnergy=0;let cache=.20,harvested=0,sourceFlux=0,sourceSpilled=0,withdrawn=0,delivered=0,loss=0,fees=0,overflow=0,requests=0,throttled=0,minEnergy=1,belowSafety=0;
 for(let t=0;t<duration;t++){
  const flux=supply240(t,(seed%29)*Math.PI/29);sourceFlux+=flux;
  const matter=.0009,matGain=Math.min(matter,Math.max(0,.5-material));material+=matGain;materialIn+=matGain;materialSpilled+=matter-matGain;
  const harvest=Math.min(flux,Math.max(0,.45-cache));harvested+=harvest;cache+=harvest;sourceSpilled+=flux-harvest;
  const due=queue.filter(x=>x.due===t),arrival=due.reduce((a,b)=>a+b.quantity*.84,0);delivered+=arrival;
  const before=s.energy,recent=history.filter(x=>x.valid),short=recent.slice(-10),long=recent.slice(-24);
  const avg=xs=>xs.length?xs.reduce((a,b)=>a+b,0)/xs.length:0,minimumCost=.0025+.011*f[t].observed;
  const shortNet=avg(short.map(x=>x.generated))-minimumCost,longNet=avg(long.map(x=>x.generated))-minimumCost;
  const status=long.length<12?'unknown':shortNet<-.001?(longNet<-.001?'insufficient':'temporary'):'sufficient';
  const trend=avg(history.slice(-8).map(x=>x.delta)),forecast=before+12*Math.min(0,trend),decision=choices234(s,f[t].observed,cap);
  let action='baseline';
  if(!decision.emergency){action=model.table[ci][bin234(s,f[t].observed)].choice;if(Math.abs(choice235(s,decision,cap,action)-decision.baseline)<.004)action='baseline'}
  const demand=before<.49||status==='insufficient'||status==='temporary';
  if(demand&&!decision.emergency){throttled++;if(action==='boost')action='baseline'}
  let request=false;
  if(cache>=.002&&before<.68&&(status==='insufficient'||status==='temporary'||forecast<.36)){
   const quantity=Math.min(cache,.012);cache-=quantity;withdrawn+=quantity;loss+=quantity*.16;queue.push({due:t+3,quantity});requests++;fees+=.001;request=true;
  }
  const preCeiling=s.ceiling;
  // The controller uses only historic realized ceiling loss, not simulator family identity.
  // An initial scar observation takes time: the gate deliberately starts uncertain.
  if(t>0){const observedLoss=Math.max(0,previousCeiling-s.ceiling);observedScar=.93*observedScar+.07*observedLoss;scarSamples++}
  const estimate=before+24*Math.min(0,trend);
  const energyFloor=.57+(s.integrity<.60?.10:0);
  const affordability=before>energyFloor&&estimate>.43&&material>.035&&status!=='insufficient';
  const indication=observedScar>.00004;
  const wantsPrevent=f[t].observed>.55&&material>=.0015;
  const wantsRebuild=s.ceiling<.995&&s.integrity>.15&&material>=.0035;
  const selective=mode==='selective';
  if(selective)affordabilityDecisions++;
  const preventive=(mode==='prevent'||mode==='hybrid'||selective)&&wantsPrevent&&(selective?(affordability&&indication):before>.12);
  const rebuild=(mode==='rebuild'||mode==='hybrid'||selective)&&wantsRebuild&&(selective?(affordability&&s.ceiling<.985):before>.35)&&material>=.0035+(preventive?.0015:0);
  if(selective&&wantsPrevent&&!preventive)deniedPrevent++;
  if(selective&&wantsRebuild&&!rebuild)deniedRebuild++;
  let extraCost=0;
  if(preventive){material-=.0015;materialUsed+=.0015;extraCost+=.0012;preventTicks++}
  if(rebuild){material-=.0035;materialUsed+=.0035;extraCost+=.004;rebuildTicks++}
  choices[action]++;const spent=step239(s,f,t,cap,family,action,demand&&!decision.emergency);
  const scar=Math.max(0,preCeiling-s.ceiling),saved=preventive?scar*.72:0;
  s.ceiling=clamp234(s.ceiling+saved);avoidedScar+=saved;
  const built=rebuild?Math.min(.0025,1-s.ceiling):0;
  s.ceiling=clamp234(s.ceiling+built);s.integrity=Math.min(s.ceiling,s.integrity+Math.min(.0012,built));reconstructed+=built;
  s.area+=s.integrity-s.trace.at(-1).integrity;
  s.energy=clamp234(s.energy-extraCost);repairEnergy+=extraCost;
  const gross=s.energy+arrival-(request?.001:0);if(gross>1)overflow+=gross-1;s.energy=clamp234(gross);
  const valid=before>.02&&before<.98&&s.energy>.02&&s.energy<.98&&!request&&arrival===0;
  history.push({valid,generated:valid?s.energy-before+spent+extraCost:null,delta:s.energy-before});
  const last=s.trace.at(-1);last.energy=+s.energy.toFixed(5);last.cache=+cache.toFixed(5);last.resourceState=status;last.sourceFlux=+flux.toFixed(5);last.arrival=+arrival.toFixed(5);last.demand=demand;last.ceiling=+s.ceiling.toFixed(5);last.integrity=+s.integrity.toFixed(5);last.material=+material.toFixed(5);last.prevent=preventive;last.rebuild=rebuild;
  previousCeiling=s.ceiling;last.affordability=mode==='selective'?affordability:null;last.scarEstimate=+observedScar.toFixed(7);
  minEnergy=Math.min(minEnergy,s.energy);if(s.energy<.27)belowSafety++;
 }
 const pending=queue.filter(x=>x.due>=duration).reduce((a,b)=>a+b.quantity,0);
 const ledgerError=Math.max(Math.abs(.20+harvested-withdrawn-cache),Math.abs(sourceFlux-harvested-sourceSpilled),Math.abs(withdrawn-delivered-loss-pending*.84),Math.abs(.20+materialIn-materialUsed-material),Math.abs(duration*.0009-materialIn-materialSpilled));
 if(ledgerError>1e-8||cache< -1e-9||cache>.45+1e-9)throw Error('ledger invalid '+ledgerError);
 // Score survival from corrected post-arrival energies, not pre-arrival bookkeeping.
 const aliveTicks=s.trace.filter(x=>x.integrity>.15&&x.energy>.08).length;
 const reserveTicks=s.trace.filter(x=>x.integrity>.30&&x.energy>.25).length;
 return {capacity:cap,scenario:family,seed,duration,mode,meanIntegrity:+(s.area/duration).toFixed(6),finalEnergy:+s.energy.toFixed(6),finalIntegrity:+s.integrity.toFixed(6),aliveTicks,reserveTicks,minEnergy:+minEnergy.toFixed(6),belowSafety,sourceFlux:+sourceFlux.toFixed(6),harvested:+harvested.toFixed(6),sourceSpilled:+sourceSpilled.toFixed(6),cacheRemaining:+cache.toFixed(6),withdrawn:+withdrawn.toFixed(6),delivered:+delivered.toFixed(6),loss:+loss.toFixed(6),pending:+pending.toFixed(6),fees:+fees.toFixed(6),overflow:+overflow.toFixed(6),requests,throttled,ledgerError:+ledgerError.toFixed(12),choices,deniedPrevent,deniedRebuild,affordabilityDecisions,materialRemaining:+material.toFixed(6),materialIn:+materialIn.toFixed(6),materialUsed:+materialUsed.toFixed(6),materialSpilled:+materialSpilled.toFixed(6),preventTicks,rebuildTicks,avoidedScar:+avoidedScar.toFixed(6),reconstructed:+reconstructed.toFixed(6),repairEnergy:+repairEnergy.toFixed(6),recoverableCeiling:+s.ceiling.toFixed(6),trace:s.trace};
}

function simulate243(cap,family,seed,duration,mode,model){
 const f=forcing240(family,seed,duration),s=init234(),ci=CAP234.indexOf(cap),queue=[],history=[],choices={baseline:0,boost:0,hold:0,conserve:0};
 let deniedPrevent=0,deniedRebuild=0,affordabilityDecisions=0,observedScar=0,scarSamples=0,previousCeiling=1,priorityPrevent=0,priorityRebuild=0,priorityAbstain=0,skippedUnprofitable=0;let material=.20,materialIn=0,materialSpilled=0,materialUsed=0,preventTicks=0,rebuildTicks=0,avoidedScar=0,reconstructed=0,repairEnergy=0;let cache=.20,harvested=0,sourceFlux=0,sourceSpilled=0,withdrawn=0,delivered=0,loss=0,fees=0,overflow=0,requests=0,throttled=0,minEnergy=1,belowSafety=0;
 for(let t=0;t<duration;t++){
  const flux=supply240(t,(seed%29)*Math.PI/29);sourceFlux+=flux;
  const matter=.0009,matGain=Math.min(matter,Math.max(0,.5-material));material+=matGain;materialIn+=matGain;materialSpilled+=matter-matGain;
  const harvest=Math.min(flux,Math.max(0,.45-cache));harvested+=harvest;cache+=harvest;sourceSpilled+=flux-harvest;
  const due=queue.filter(x=>x.due===t),arrival=due.reduce((a,b)=>a+b.quantity*.84,0);delivered+=arrival;
  const before=s.energy,recent=history.filter(x=>x.valid),short=recent.slice(-10),long=recent.slice(-24);
  const avg=xs=>xs.length?xs.reduce((a,b)=>a+b,0)/xs.length:0,minimumCost=.0025+.011*f[t].observed;
  const shortNet=avg(short.map(x=>x.generated))-minimumCost,longNet=avg(long.map(x=>x.generated))-minimumCost;
  const status=long.length<12?'unknown':shortNet<-.001?(longNet<-.001?'insufficient':'temporary'):'sufficient';
  const trend=avg(history.slice(-8).map(x=>x.delta)),forecast=before+12*Math.min(0,trend),decision=choices234(s,f[t].observed,cap);
  let action='baseline';
  if(!decision.emergency){action=model.table[ci][bin234(s,f[t].observed)].choice;if(Math.abs(choice235(s,decision,cap,action)-decision.baseline)<.004)action='baseline'}
  const demand=before<.49||status==='insufficient'||status==='temporary';
  if(demand&&!decision.emergency){throttled++;if(action==='boost')action='baseline'}
  let request=false;
  if(cache>=.002&&before<.68&&(status==='insufficient'||status==='temporary'||forecast<.36)){
   const quantity=Math.min(cache,.012);cache-=quantity;withdrawn+=quantity;loss+=quantity*.16;queue.push({due:t+3,quantity});requests++;fees+=.001;request=true;
  }
  const preCeiling=s.ceiling;
  // WAG-243 uses only causal observed loss, no future forcing or scenario label.
  // Each tick has one maintenance slot: prevention OR reconstruction OR abstention.
  if(t>0){const loss=Math.max(0,previousCeiling-s.ceiling);observedScar=.93*observedScar+.07*loss;scarSamples++}
  const shortEnergy=history.slice(-12).map(x=>x.delta);
  const avgLoss=shortEnergy.length?shortEnergy.reduce((a,b)=>a+b,0)/shortEnergy.length:0;
  const projected=before+24*Math.min(0,avgLoss);
  const floor=s.integrity<.60?.52:.40;
  const canSpend=before>floor&&projected>floor-.055&&material>.025&&status!=='insufficient';
  const beforeRepairCost=.0012,afterRepairCost=.004;
  const expectedSaved=.72*observedScar*12;
  const structuralGap=Math.max(0,1-s.ceiling);
  // Priority is per-energy expected structural benefit, discounted for low reserve.
  const uncertaintyDiscount=scarSamples<8?.30:1;
  const preserveValue=uncertaintyDiscount*expectedSaved/(beforeRepairCost+0.0015);
  const rebuildValue=Math.min(.0025,structuralGap)/(afterRepairCost+0.0035);
  const eligiblePreserve=f[t].observed>.55&&material>=.0015&&observedScar>.000025;
  const eligibleRebuild=structuralGap>.012&&s.integrity>.18&&material>=.0035;
  const affordable=canSpend&&(mode==='priority');
  const reservePressure=clamp234((.74-before)/.54);
  const threshold=.13+.32*reservePressure;
  const wantPreserve=affordable&&eligiblePreserve&&preserveValue>threshold;
  const wantRebuild=affordable&&eligibleRebuild&&rebuildValue>threshold;
  let preventive=false,rebuild=false;
  if(mode==='priority'){
    affordabilityDecisions++;
    if(wantPreserve||wantRebuild){
      // Scar prevention wins only if its expected resource-adjusted value is larger.
      preventive=wantPreserve&&(!wantRebuild||preserveValue>=rebuildValue);
      rebuild=wantRebuild&&!preventive;
    }
    if(preventive)priorityPrevent++;else if(rebuild)priorityRebuild++;else priorityAbstain++;
    if(eligiblePreserve&&!preventive)deniedPrevent++;
    if(eligibleRebuild&&!rebuild)deniedRebuild++;
    if(canSpend&&(eligiblePreserve||eligibleRebuild)&&!preventive&&!rebuild)skippedUnprofitable++;
  }else{
    preventive=(mode==='hybrid'||mode==='selective')&&f[t].observed>.55&&before>.12&&material>=.0015;
    rebuild=(mode==='hybrid'||mode==='selective'||mode==='rebuild')&&s.ceiling<.995&&s.integrity>.15&&before>.35&&material>=.0035+(preventive?.0015:0);
    if(mode==='selective'){
      const low=before<=.57||projected<=.43||material<=.035||status==='insufficient';
      preventive=preventive&&!low&&observedScar>.00004;
      rebuild=rebuild&&!low&&s.ceiling<.985;
    }
  }
  let extraCost=0;
  if(preventive){material-=.0015;materialUsed+=.0015;extraCost+=.0012;preventTicks++}
  if(rebuild){material-=.0035;materialUsed+=.0035;extraCost+=.004;rebuildTicks++}
  choices[action]++;const spent=step239(s,f,t,cap,family,action,demand&&!decision.emergency);
  const scar=Math.max(0,preCeiling-s.ceiling),saved=preventive?scar*.72:0;
  s.ceiling=clamp234(s.ceiling+saved);avoidedScar+=saved;
  const built=rebuild?Math.min(.0025,1-s.ceiling):0;
  s.ceiling=clamp234(s.ceiling+built);s.integrity=Math.min(s.ceiling,s.integrity+Math.min(.0012,built));reconstructed+=built;
  s.area+=s.integrity-s.trace.at(-1).integrity;
  s.energy=clamp234(s.energy-extraCost);repairEnergy+=extraCost;
  const gross=s.energy+arrival-(request?.001:0);if(gross>1)overflow+=gross-1;s.energy=clamp234(gross);
  const valid=before>.02&&before<.98&&s.energy>.02&&s.energy<.98&&!request&&arrival===0;
  history.push({valid,generated:valid?s.energy-before+spent+extraCost:null,delta:s.energy-before});
  const last=s.trace.at(-1);last.energy=+s.energy.toFixed(5);last.cache=+cache.toFixed(5);last.resourceState=status;last.sourceFlux=+flux.toFixed(5);last.arrival=+arrival.toFixed(5);last.demand=demand;last.ceiling=+s.ceiling.toFixed(5);last.integrity=+s.integrity.toFixed(5);last.material=+material.toFixed(5);last.prevent=preventive;last.rebuild=rebuild;
  previousCeiling=s.ceiling;last.affordability=mode==='priority'?canSpend:null;last.scarEstimate=+observedScar.toFixed(7);
  minEnergy=Math.min(minEnergy,s.energy);if(s.energy<.27)belowSafety++;
 }
 const pending=queue.filter(x=>x.due>=duration).reduce((a,b)=>a+b.quantity,0);
 const ledgerError=Math.max(Math.abs(.20+harvested-withdrawn-cache),Math.abs(sourceFlux-harvested-sourceSpilled),Math.abs(withdrawn-delivered-loss-pending*.84),Math.abs(.20+materialIn-materialUsed-material),Math.abs(duration*.0009-materialIn-materialSpilled));
 if(ledgerError>1e-8||cache< -1e-9||cache>.45+1e-9)throw Error('ledger invalid '+ledgerError);
 // Score survival from corrected post-arrival energies, not pre-arrival bookkeeping.
 const aliveTicks=s.trace.filter(x=>x.integrity>.15&&x.energy>.08).length;
 const reserveTicks=s.trace.filter(x=>x.integrity>.30&&x.energy>.25).length;
 return {capacity:cap,scenario:family,seed,duration,mode,meanIntegrity:+(s.area/duration).toFixed(6),finalEnergy:+s.energy.toFixed(6),finalIntegrity:+s.integrity.toFixed(6),aliveTicks,reserveTicks,minEnergy:+minEnergy.toFixed(6),belowSafety,sourceFlux:+sourceFlux.toFixed(6),harvested:+harvested.toFixed(6),sourceSpilled:+sourceSpilled.toFixed(6),cacheRemaining:+cache.toFixed(6),withdrawn:+withdrawn.toFixed(6),delivered:+delivered.toFixed(6),loss:+loss.toFixed(6),pending:+pending.toFixed(6),fees:+fees.toFixed(6),overflow:+overflow.toFixed(6),requests,throttled,ledgerError:+ledgerError.toFixed(12),choices,deniedPrevent,deniedRebuild,affordabilityDecisions,priorityPrevent,priorityRebuild,priorityAbstain,skippedUnprofitable,materialRemaining:+material.toFixed(6),materialIn:+materialIn.toFixed(6),materialUsed:+materialUsed.toFixed(6),materialSpilled:+materialSpilled.toFixed(6),preventTicks,rebuildTicks,avoidedScar:+avoidedScar.toFixed(6),reconstructed:+reconstructed.toFixed(6),repairEnergy:+repairEnergy.toFixed(6),recoverableCeiling:+s.ceiling.toFixed(6),trace:s.trace};
}

const SEEDS243=[2101,2102,2103,2104],DURATIONS243=[240,480,960,1920],MODES243=['priority','selective','hybrid','baseline'];
function experiment243(){
 const model=train235(),scenarios=['chirp','scar','famine','friction','combined','phaseflip','bursts'],rows=[],examples=[],counterexamples=[],comparison={};
 let runs=0,ticks=0,priorityPrevent=0,priorityRebuild=0,priorityAbstain=0,materialUsed=0,maxLedgerError=0,energyViolations=0;
 for(const duration of DURATIONS243){comparison[duration]={baseline:{wins:0,losses:0,ties:0},selective:{wins:0,losses:0,ties:0},hybrid:{wins:0,losses:0,ties:0}};
 for(const capacity of CAP234)for(const scenario of scenarios){
 const sums=Object.fromEntries(MODES243.map(m=>[m,{meanIntegrity:0,finalEnergy:0,finalIntegrity:0,aliveTicks:0,reserveTicks:0,recoverableCeiling:0,materialUsed:0}]));
 for(const seed of SEEDS243){
  const p=Object.fromEntries(MODES243.map(m=>[m,simulate243(capacity,scenario,seed,duration,m,model)]));runs+=4;ticks+=4*duration;
  const a=p.priority;priorityPrevent+=a.priorityPrevent;priorityRebuild+=a.priorityRebuild;priorityAbstain+=a.priorityAbstain;materialUsed+=a.materialUsed;maxLedgerError=Math.max(maxLedgerError,a.ledgerError);energyViolations+=a.belowSafety;
  for(const m of MODES243)for(const k of Object.keys(sums[m]))sums[m][k]+=p[m][k];
  for(const baseline of ['baseline','selective','hybrid']){const d=a.meanIntegrity-p[baseline].meanIntegrity,c=comparison[duration][baseline];if(d>1e-6)c.wins++;else if(d< -1e-6)c.losses++;else c.ties++}
  if(a.meanIntegrity<p.baseline.meanIntegrity-1e-6||a.aliveTicks<p.baseline.aliveTicks||a.reserveTicks<p.baseline.reserveTicks||a.meanIntegrity<p.selective.meanIntegrity-1e-6)counterexamples.push({duration,capacity,scenario,seed,policies:Object.fromEntries(MODES243.map(m=>[m,{integrity:p[m].meanIntegrity,aliveTicks:p[m].aliveTicks,reserveTicks:p[m].reserveTicks,finalEnergy:p[m].finalEnergy,ceiling:p[m].recoverableCeiling}]))});
  if(capacity===13&&['scar','famine','combined'].includes(scenario)&&seed===2101)examples.push({duration,capacity,scenario,priority:{...a,trace:a.trace.filter((v,i)=>i%12===0||i===a.trace.length-1)},selective:{...p.selective,trace:undefined},hybrid:{...p.hybrid,trace:undefined},baseline:{...p.baseline,trace:undefined}});
 }
 rows.push({duration,capacity,scenario,average:Object.fromEntries(MODES243.map(m=>[m,Object.fromEntries(Object.entries(sums[m]).map(([k,v])=>[k,+(v/SEEDS243.length).toFixed(6)]))]))});
 }}
 return {bound:'WAG-243',seeds:SEEDS243,durations:DURATIONS243,scenarioFamilies:scenarios,policyRuns:runs,ticks,comparison,actions:{prevent:priorityPrevent,rebuild:priorityRebuild,abstain:priorityAbstain},priorityMaterialUsed:+materialUsed.toFixed(5),maxLedgerError,energyViolations,rows,counterexamples,examples};
}
if(typeof module!=='undefined')module.exports={simulate243,experiment243};
if(typeof require!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment243(),null,2));