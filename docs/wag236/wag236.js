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
s.ceiling=clamp234(s.ceiling-damage*scar);s.energy=clamp234(s.energy+gen-cost-.011*raw-repair*.35-mod);s.integrity=Math.min(s.ceiling,clamp234(s.integrity-damage+repair));s.protection=p;s.history=c.history;s.stress=c.stress;s.lastObserved=observed;s.area+=s.integrity;const alive=s.integrity>.15&&s.energy>.08;if(alive)s.alive++;if(s.energy>.25&&s.integrity>.30)s.reserve++;const band=p<.12?'REST':p<.4?'GUARD':'DEFEND';if(band!==s.lastBand)s.transitions++;s.lastBand=band;s.trace.push({t,pressure:+pressure.toFixed(5),energy:+s.energy.toFixed(5),integrity:+s.integrity.toFixed(5),protection:+p.toFixed(5),action:a,alive});if(s.energy<0||s.energy>1||s.integrity<0||s.integrity>s.ceiling+1e-10||p>shield234(cap)+1e-10)throw Error('bounds')}
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
const TEST236=[1401,1402,1403,1404,1405,1406,1407,1408];
function experiment236(){
 const model=train235(),groups=[{name:'known',families:FAMTRAIN235},{name:'withheld',families:FAMTEST235}],modes=['viability','learned','graded'];
 const rows=[],negative=[],examples=[],comparison={known:{graded:{wins:0,losses:0,ties:0},wag235:{wins:0,losses:0,ties:0}},withheld:{graded:{wins:0,losses:0,ties:0},wag235:{wins:0,losses:0,ties:0}}};
 let runs=0,blocked=0,boosts=0;
 for(const group of groups)for(const cap of CAP234)for(const family of group.families){
  const sum=Object.fromEntries(modes.map(m=>[m,{meanIntegrity:0,finalEnergy:0,aliveTicks:0,reserveTicks:0}]));
  for(const seed of TEST236){
   const policies=Object.fromEntries(modes.map(m=>[m,simulate236(cap,family,seed,m,model)]));runs+=3;
   blocked+=policies.viability.blocked;boosts+=policies.viability.choices.boost;
   for(const m of modes)for(const key of Object.keys(sum[m]))sum[m][key]+=policies[m][key];
   for(const [name,baseline]of [['graded','graded'],['wag235','learned']]){
    const d=policies.viability.meanIntegrity-policies[baseline].meanIntegrity,stat=comparison[group.name][name];
    if(d>1e-6)stat.wins++;else if(d< -1e-6)stat.losses++;else stat.ties++;
   }
   if(policies.viability.meanIntegrity<policies.graded.meanIntegrity-1e-6||policies.viability.aliveTicks<policies.graded.aliveTicks||policies.viability.reserveTicks<policies.graded.reserveTicks||policies.viability.meanIntegrity<policies.learned.meanIntegrity-1e-6)negative.push({group:group.name,capacity:cap,scenario:family,seed,viability:{meanIntegrity:policies.viability.meanIntegrity,finalEnergy:policies.viability.finalEnergy,aliveTicks:policies.viability.aliveTicks,reserveTicks:policies.viability.reserveTicks},graded:{meanIntegrity:policies.graded.meanIntegrity,finalEnergy:policies.graded.finalEnergy,aliveTicks:policies.graded.aliveTicks,reserveTicks:policies.graded.reserveTicks},wag235:{meanIntegrity:policies.learned.meanIntegrity,finalEnergy:policies.learned.finalEnergy,aliveTicks:policies.learned.aliveTicks,reserveTicks:policies.learned.reserveTicks}});
   if(seed===1401)examples.push({group:group.name,capacity:cap,scenario:family,viability:policies.viability,graded:{...policies.graded,trace:undefined},wag235:{...policies.learned,trace:undefined}});
  }
  rows.push({group:group.name,capacity:cap,scenario:family,average:Object.fromEntries(modes.map(m=>[m,Object.fromEntries(Object.entries(sum[m]).map(([k,v])=>[k,+(v/8).toFixed(6)]))]))});
 }
 return {bound:'WAG-236',training:model,testSeeds:TEST236,policyRuns:runs,ticks:runs*240,boosts,blocked,comparison,rows,counterexamples:negative,examples};
}
if(typeof module!=='undefined')module.exports={simulate236,experiment236};
if(typeof require!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment236(),null,2));