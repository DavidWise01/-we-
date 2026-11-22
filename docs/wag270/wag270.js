/* WAG-270 · Phase III turn 2/12 · case-level dominance and threshold robustness · .dlw
  Threshold grid PREDECLARED: low (energy .57/material .05/spacing 9),
  canonical WAG269 (.62/.06/9), high (.67/.07/9).
  Frozen baseline and noRepair are controls. Fresh 5701-5703 seeds,
  240/480 ticks, matched environment forcing.
  The online action reads current and preceding state only.
  No training, threshold selection, or retroactive policy promotion.
*/
const WAG270_SEEDS=[5701,5702,5703],WAG270_HORIZONS=[240,480];
const WAG270_FAMILIES=['scar','combined'];
const WAG270_STRESS=['late-collapse','double-shock','intermittent','resource-squeeze'];
const WAG270_CAP=[8,13];
const WAG270_POLICIES=Object.freeze({
 noRepair:null,
 frozen:null,
 low:Object.freeze({energyFloor:.57,materialFloor:.05,minimumSpacing:9}),
 canonical:Object.freeze({energyFloor:.62,materialFloor:.06,minimumSpacing:9}),
 high:Object.freeze({energyFloor:.67,materialFloor:.07,minimumSpacing:9})
});
function wag270Run(cap,family,seed,duration,stress,policy,frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 if(!Object.prototype.hasOwnProperty.call(WAG270_POLICIES,policy))throw Error('Invalid policy');
 if(!WAG270_HORIZONS.includes(duration))throw Error('Invalid duration');
 const cfg=WAG270_POLICIES[policy],x=start244(cap,family,seed,duration);
 x.modelTable=models.train250.source;
 const state={level:'normal',alarmStreak:0,clearStreak:0,changes:[]},
 ledger={withdrawnEnergy:0,withdrawnMaterial:0,injectedEnergy:0,injectedMaterial:0,
  lastEnergy:x.s.energy,lastMaterial:x.material,continuityMax:0,events:0};
 let lastRepair=-100,repairs=0,denied=0;
 const trace=[],chosen=[];
 for(let t=0;t<duration;t++){
  ledger.continuityMax=Math.max(ledger.continuityMax,
   Math.abs(x.s.energy-ledger.lastEnergy),Math.abs(x.material-ledger.lastMaterial));
  const gate=wag263Gate(x,state);
  const base=policy==='noRepair'?{action:'abstain'}:
   wag263Select(x,models,horizon,lastRepair,gate,'baseline');
  let action=base.action;
  if(cfg&&action!=='abstain'&&
   (x.s.energy<cfg.energyFloor||x.material<cfg.materialFloor||
    t-lastRepair<cfg.minimumSpacing)){action='abstain';denied++}
  if(action!=='abstain'){lastRepair=t;repairs++}
  chosen.push(action);
  step244(x,action);
  const forcing=wag269Stress(t,stress,seed),e0=x.s.energy,m0=x.material;
  x.s.energy=Math.max(0,Math.min(1,e0+forcing.energy));
  x.material=Math.max(0,Math.min(1,m0+forcing.material));
  const de=x.s.energy-e0,dm=x.material-m0;
  ledger.withdrawnEnergy+=Math.max(0,-de);
  ledger.withdrawnMaterial+=Math.max(0,-dm);
  ledger.injectedEnergy+=Math.max(0,de);
  ledger.injectedMaterial+=Math.max(0,dm);
  if(forcing.energy||forcing.material)ledger.events++;
  ledger.lastEnergy=x.s.energy;ledger.lastMaterial=x.material;
  const z=x.s.trace.at(-1);z.energy=x.s.energy;z.material=x.material;
  trace.push({tick:t,energy:x.s.energy,material:x.material,
   integrity:z.integrity,action});
 }
 const pending=x.queue.filter(z=>z.due>=x.duration).reduce((a,z)=>a+z.amount,0);
 const energyResidual=Math.max(Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),
   Math.abs(x.energyFlux-x.energyIn-x.energyWaste),
   Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84));
 const materialResidual=Math.abs(.2+x.materialIn+ledger.injectedMaterial-
   x.materialSpent-ledger.withdrawnMaterial-x.material);
 if(energyResidual>1e-8||materialResidual>1e-8)throw Error('Resource invariant failed');
 const aliveTicks=trace.filter(z=>z.energy>.08&&z.integrity>.15).length;
 return {policy,cap,family,seed,duration,stress,aliveTicks,
  fullSurvival:aliveTicks===duration,
  reserveTicks:trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  meanIntegrity:x.s.area/duration,repairs,denied,
  finalEnergy:x.s.energy,finalMaterial:x.material,trace,chosen,
  ledger:{...ledger,energyResidual,materialResidual}};
}
function wag270Dominates(a,b){
 const nonWorse=a.aliveTicks>=b.aliveTicks&&a.reserveTicks>=b.reserveTicks&&
  a.meanIntegrity>=b.meanIntegrity-1e-12;
 const strict=a.aliveTicks>b.aliveTicks||a.reserveTicks>b.reserveTicks||
  a.meanIntegrity>b.meanIntegrity+1e-12;
 return nonWorse&&strict;
}
function wag270Aggregate(rows){
 const n=rows.length;
 return {n,fullSurvival:rows.filter(r=>r.fullSurvival).length,
  meanAliveRatio:rows.reduce((v,r)=>v+r.aliveTicks/r.duration,0)/n,
  meanReserveRatio:rows.reduce((v,r)=>v+r.reserveTicks/r.duration,0)/n,
  meanIntegrity:rows.reduce((v,r)=>v+r.meanIntegrity,0)/n,
  meanRepairs:rows.reduce((v,r)=>v+r.repairs,0)/n};
}
function wag270Experiment(frozen,models,horizon){
 const rows=[],cases=[];
 for(const duration of WAG270_HORIZONS)for(const family of WAG270_FAMILIES)
 for(const stress of WAG270_STRESS)for(const cap of WAG270_CAP)
 for(const seed of WAG270_SEEDS){
  const group={};
  for(const policy of Object.keys(WAG270_POLICIES)){
   const r=wag270Run(cap,family,seed,duration,stress,policy,frozen,models,horizon);
   const row={policy,cap,family,seed,duration,stress,aliveTicks:r.aliveTicks,
    fullSurvival:r.fullSurvival,reserveTicks:r.reserveTicks,
    meanIntegrity:r.meanIntegrity,repairs:r.repairs,denied:r.denied,
    energyResidual:r.ledger.energyResidual,
    materialResidual:r.ledger.materialResidual,
    continuity:r.ledger.continuityMax};
   rows.push(row);group[policy]=row;
  }
  const candidates=['low','canonical','high'];
  cases.push({duration,family,stress,cap,seed,
   nonDominated:candidates.filter(p=>!Object.keys(group).some(q=>q!==p&&wag270Dominates(group[q],group[p]))),
   vsFrozen:Object.fromEntries(candidates.map(p=>[p,{
    aliveDelta:group[p].aliveTicks-group.frozen.aliveTicks,
    reserveDelta:group[p].reserveTicks-group.frozen.reserveTicks,
    integrityDelta:group[p].meanIntegrity-group.frozen.meanIntegrity,
    dominatesFrozen:wag270Dominates(group[p],group.frozen),
    dominatedByFrozen:wag270Dominates(group.frozen,group[p])
   }]))});
 }
 const aggregates={};
 for(const duration of WAG270_HORIZONS){
  aggregates[duration]=Object.fromEntries(Object.keys(WAG270_POLICIES).map(policy=>
   [policy,wag270Aggregate(rows.filter(r=>r.duration===duration&&r.policy===policy))]));
 }
 return {bound:'WAG-270',phase:'WAG-III',turn:2,policies:WAG270_POLICIES,
  seeds:WAG270_SEEDS,aggregates,rows,cases,
  summary:{policyRuns:rows.length,matchedConditions:cases.length,
   canonicalDominatesFrozen:cases.filter(c=>c.vsFrozen.canonical.dominatesFrozen).length,
   frozenDominatesCanonical:cases.filter(c=>c.vsFrozen.canonical.dominatedByFrozen).length,
   canonicalIntegrityRegressions:cases.filter(c=>c.vsFrozen.canonical.integrityDelta< -1e-12).length,
   canonicalAliveRegressions:cases.filter(c=>c.vsFrozen.canonical.aliveDelta<0).length,
   continuityMax:Math.max(...rows.map(r=>r.continuity)),
   maxEnergyResidual:Math.max(...rows.map(r=>r.energyResidual)),
   maxMaterialResidual:Math.max(...rows.map(r=>r.materialResidual))},
  limits:['Threshold variants are predetermined; this is not training or tuning on holdouts',
   'All policies share one synthetic engine ancestry',
   'Case-level dominance includes alive ticks, reserve ticks, and integrity; aggregate frontier is a different property',
   'No controller is promoted by this test']};
}
if(typeof module!=='undefined')module.exports={wag270Run,wag270Dominates,wag270Experiment};
