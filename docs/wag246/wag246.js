/* WAG-246 · state-stratified recovery opportunities · synthetic deterministic lab · .dlw
   Load after ../wag245/wag245.js. Provenance: single synthetic engine, not independent evidence. */
const WAG246_PHASES=[{name:'early',t:36},{name:'middle',t:120},{name:'late',t:216}];
const WAG246_RESOURCES=[{name:'poor',energy:.24},{name:'rich',energy:.78}];
const WAG246_SEEDS=[2601,2602,2603,2604], WAG246_TEST=[2701,2702,2703,2704];
const WAG246_ACTIONS=['prevent','rebuild'];
function wag246Eligible(x,a){
 const s=x.s,obs=x.f[x.t].observed;
 return a==='prevent'?s.energy>.14&&s.integrity>.15&&obs>.55&&x.material>=.0015:
 s.energy>.35&&s.integrity>.15&&s.ceiling<.995&&x.material>=.0035;
}
function wag246Phase(t){return t<80?0:t<160?1:2}
function wag246Resources(e){return e<.43?0:1}
function wag246Key(x){return [CAP234.indexOf(x.cap),wag246Phase(x.t%240),wag246Resources(x.s.energy),bin244(x)].join(':')}
function wag246Value(a,b){
 return (a.meanIntegrity-b.meanIntegrity)+.25*(a.integralReserve-b.integralReserve)/a.horizon+
 .5*(a.integralAlive-b.integralAlive)/a.horizon+.18*(a.finalEnergy-b.finalEnergy)+.04*(a.finalMaterial-b.finalMaterial);
}
function wag246Branches(x,a,h){
 const aa=branchMetrics245(x,a,h),bb=branchMetrics245(x,'abstain',h);
 aa.horizon=Math.min(h,x.duration-x.t);
 return {value:wag246Value(aa,bb),alive:(aa.integralAlive-bb.integralAlive)/aa.horizon,
 reserve:(aa.integralReserve-bb.integralReserve)/aa.horizon,energy:aa.finalEnergy-bb.finalEnergy,
 integrity:aa.meanIntegrity-bb.meanIntegrity};
}
function wag246Stat(){return {n:0,mean:0,m2:0,alive:0,reserve:0,energy:0,integrity:0}}
function wag246Add(z,v){
 z.n++;const d=v.value-z.mean;z.mean+=d/z.n;z.m2+=d*(v.value-z.mean);
 for(const k of ['alive','reserve','energy','integrity'])z[k]+=(v[k]-z[k])/z.n;
}
function wag246Train(){
 const source=train235(),cells={},coverage={};
 for(const cap of CAP234)for(const family of FAMILIES_TRAIN244)for(const seed of WAG246_SEEDS)
 for(const resource of WAG246_RESOURCES){
  const x=start244(cap,family,seed,480);x.modelTable=source.table;
  x.s.energy=resource.energy; // explicit controlled initial-energy experiment; material ledger unchanged
  while(x.t<240){
   const p=WAG246_PHASES.find(z=>z.t===x.t);
   if(p){const key=wag246Key(x);coverage[key]=(coverage[key]||0)+1;
    for(const a of WAG246_ACTIONS){if(!wag246Eligible(x,a))continue;
      const entry=cells[key]??=(Object.fromEntries(WAG246_ACTIONS.map(k=>[k,Object.fromEntries(HORIZONS245.map(h=>[h,wag246Stat()]))])));
      for(const h of HORIZONS245)wag246Add(entry[a][h],wag246Branches(x,a,h));
    }
   }
   step244(x,'abstain');
  }
 }
 const table={};let approved=0,covered=0,missedCells=0;
 for(const [key,entry] of Object.entries(cells)){
  const ranked=WAG246_ACTIONS.map(a=>{
   const metrics=HORIZONS245.map(h=>{
     const z=entry[a][h],sd=z.n>1?Math.sqrt(z.m2/(z.n-1)):0;
     return {h,n:z.n,mean:z.mean,lower:z.n>1?z.mean-1.64*sd/Math.sqrt(z.n):null,
       alive:z.alive,reserve:z.reserve,energy:z.energy,integrity:z.integrity};
   });
   const [short,mid,long]=metrics;
   const safe=short.n>=4&&mid.n>=4&&long.n>=4&&
     short.lower>-.0002&&mid.lower>-.00015&&long.lower>.00005&&
     long.alive>=-.003&&long.reserve>=-.003&&long.energy>=-.035;
   return {action:a,metrics,safe};
  }).sort((a,b)=>b.metrics[2].lower-a.metrics[2].lower);
  const choice=ranked.find(z=>z.safe)?.action||'abstain';
  if(choice!=='abstain')approved++;else missedCells++;
  table[key]={choice,ranked};covered++;
 }
 return {table,source:source.table,coverage,approved,covered,missedCells,
   trainSeeds:WAG246_SEEDS,phaseWindows:WAG246_PHASES,resourceStarts:WAG246_RESOURCES,
   guarantee:'Only sampled synthetic conditions; no guarantee outside training'};
}
function wag246Run(cap,family,seed,duration,mode,model,reference244,reference245){
 if(mode==='wag244')return simulate244(cap,family,seed,duration,'trained',reference244);
 if(mode==='wag245')return simulate245(cap,family,seed,duration,'long',reference245);
 const x=start244(cap,family,seed,duration);x.modelTable=model.source;
 let approved=0,blocked=0,missed=0,repairOpportunity=0;
 while(x.t<duration){
  const key=wag246Key(x),entry=model.table[key];
  let a=mode==='wag246'?(entry?.choice||'abstain'):'abstain';
  if(a!=='abstain'&&!wag246Eligible(x,a)){blocked++;a='abstain'}
  if(a!=='abstain')approved++;
  // Local counterfactual: only sampled at 36,120,216 in each 240-tick block.
  if([36,120,216].includes(x.t%240)&&x.t+12<=duration){
   const possible=WAG246_ACTIONS.filter(z=>wag246Eligible(x,z));
   if(possible.length){const best=Math.max(...possible.map(z=>wag246Branches(x,z,12).value));
    if(best>.00005){repairOpportunity++;if(a==='abstain')missed++}
   }
  }
  step244(x,a);
 }
 const pending=x.queue.filter(z=>z.due>=duration).reduce((sum,z)=>sum+z.amount,0);
 const energyError=Math.max(Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),
 Math.abs(x.energyFlux-x.energyIn-x.energyWaste),
 Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84));
 const materialError=Math.max(Math.abs(.2+x.materialIn-x.materialSpent-x.material),
 Math.abs(duration*.0009-x.materialIn-x.materialWaste));
 if(energyError>1e-8||materialError>1e-8)throw Error('WAG-246 conservation failed');
 return {capacity:cap,scenario:family,seed,duration,mode,meanIntegrity:x.s.area/duration,
 finalIntegrity:x.s.integrity,finalEnergy:x.s.energy,aliveTicks:x.s.trace.filter(z=>z.energy>.08&&z.integrity>.15).length,
 reserveTicks:x.s.trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
 maintenance:x.choices,approved,blocked,missed,repairOpportunity,energyError,materialError,trace:x.s.trace};
}
function wag246Experiment(){
 const model=wag246Train(),ref244=train244(),ref245=train245(),cases=[],aggregate={};
 for(const duration of [240,480,960,1920])for(const cap of CAP234)
 for(const family of [...FAMILIES_TRAIN244,...FAMILIES_HOLD244])for(const seed of WAG246_TEST){
  const r={};for(const mode of ['wag246','wag244','wag245','abstain'])
   r[mode]=wag246Run(cap,family,seed,duration,mode,model,ref244,ref245);
  const group=FAMILIES_HOLD244.includes(family)?'withheld':'familiar',key=duration+':'+group;
  const z=aggregate[key]??={n:0,values:{},missed:0,opportunities:0,nonInferior:0,scarWins:0};
  z.n++;for(const mode of Object.keys(r)){
   const m=z.values[mode]??={integrity:0,alive:0,reserve:0,prevent:0,rebuild:0};
   m.integrity+=r[mode].meanIntegrity;m.alive+=r[mode].aliveTicks;m.reserve+=r[mode].reserveTicks;
   m.prevent+=r[mode].maintenance.prevent;m.rebuild+=r[mode].maintenance.rebuild;
  }
  z.missed+=r.wag246.missed;z.opportunities+=r.wag246.repairOpportunity;
  if(r.wag246.aliveTicks>=r.wag245.aliveTicks&&r.wag246.reserveTicks>=r.wag245.reserveTicks)z.nonInferior++;
  if(family==='scar'&&r.wag246.meanIntegrity>=r.wag245.meanIntegrity)z.scarWins++;
  if(seed===2701&&cap===13&&['scar','combined'].includes(family)&&duration===240)
   cases.push({duration,cap,family,seed,policies:Object.fromEntries(Object.entries(r).map(([k,v])=>[k,{
    integrity:v.meanIntegrity,alive:v.aliveTicks,reserve:v.reserveTicks,
    prevent:v.maintenance.prevent,rebuild:v.maintenance.rebuild,missed:v.missed??null}]))});
 }
 for(const z of Object.values(aggregate))for(const v of Object.values(z.values))
  for(const k of Object.keys(v))v[k]/=z.n;
 return {bound:'WAG-246',model:{...model,source:undefined},holdoutSeeds:WAG246_TEST,
  aggregate,cases,claim:'Results are synthetic; policy needs independent holdout confirmation'};
}
if(typeof module!=='undefined')module.exports={wag246Train,wag246Run,wag246Experiment};
