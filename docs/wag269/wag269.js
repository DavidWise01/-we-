/* WAG-269 · Phase III turn 1 · survival-integrity Pareto exploration · .dlw
 Phase II WAG-268 archive / WAG-264 frozen policy are read-only.
 Candidate controller is PREDECLARED: only execute the original WAG261
 repair choice when the current operational energy >= .62 and material >= .06.
 No future forcing or evaluation labels enter online decisions.
 Four policy points, two horizons, new seed cohort and periodically replayed
 WAG265-style synthetic stress. Pareto in (full-survival fraction,mean integrity).
 This is exploration, not policy promotion.
*/
const WAG269_SEEDS=[5601,5602,5603];
const WAG269_HORIZONS=[240,480];
const WAG269_STRESS=['late-collapse','double-shock','intermittent','resource-squeeze'];
const WAG269_FAMILIES=['scar','combined','phaseflip','famine'];
const WAG269_MODES=['noRepair','frozen','rejectedAdaptive','conditional'];
const WAG269_CONDITIONAL={energyFloor:.62,materialFloor:.06,minimumSpacing:9};
function wag269Stress(t,kind,seed){
 // Repeated physical pressure per 240-tick cycle, offset 17 ticks
 // on alternating cycles; no access to this schedule from controller.
 const cycle=Math.floor(t/240),local=(t+17*(cycle%2))%240;
 return wag265Stress(local,kind,seed+101*cycle);
}
function wag269Run(cap,family,seed,duration,stress,mode,frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 if(!WAG269_MODES.includes(mode)||!WAG269_HORIZONS.includes(duration))throw Error('invalid WAG269 test');
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const state={level:'normal',alarmStreak:0,clearStreak:0,changes:[]},
 ledger={withdrawnEnergy:0,withdrawnMaterial:0,injectedEnergy:0,injectedMaterial:0,
  continuityMax:0,lastEnergy:x.s.energy,lastMaterial:x.material,events:0};
 let lastRepair=-100,repairs=0,rejectedByFloor=0;
 const trace=[],snapshots=[],chosen=[];
 for(let t=0;t<duration;t++){
  ledger.continuityMax=Math.max(ledger.continuityMax,Math.abs(ledger.lastEnergy-x.s.energy),
    Math.abs(ledger.lastMaterial-x.material));
  const gate=wag263Gate(x,state);
  const baseMode=mode==='rejectedAdaptive'?'adaptive':'baseline';
  const old=mode==='noRepair'?{action:'abstain'}:wag263Select(x,models,horizon,lastRepair,gate,baseMode);
  let action=old.action;
  if(mode==='conditional'&&action!=='abstain'){
   if(x.s.energy<WAG269_CONDITIONAL.energyFloor||
     x.material<WAG269_CONDITIONAL.materialFloor||
     t-lastRepair<WAG269_CONDITIONAL.minimumSpacing){
     action='abstain';rejectedByFloor++;
   }
  }
  if(action!=='abstain'){repairs++;lastRepair=t}
  chosen.push(action);
  step244(x,action);
  const stressEvent=wag269Stress(t,stress,seed);
  const preE=x.s.energy,preM=x.material;
  x.s.energy=Math.max(0,Math.min(1,preE+stressEvent.energy));
  x.material=Math.max(0,Math.min(1,preM+stressEvent.material));
  const de=x.s.energy-preE,dm=x.material-preM;
  ledger.withdrawnEnergy+=Math.max(0,-de);
  ledger.withdrawnMaterial+=Math.max(0,-dm);
  ledger.injectedEnergy+=Math.max(0,de);
  ledger.injectedMaterial+=Math.max(0,dm);
  if(stressEvent.energy||stressEvent.material)ledger.events++;
  ledger.lastEnergy=x.s.energy;ledger.lastMaterial=x.material;
  const z=x.s.trace.at(-1);z.energy=x.s.energy;z.material=x.material;
  trace.push({tick:t,energy:x.s.energy,material:x.material,integrity:z.integrity,
    ceiling:z.ceiling,action,pressure:z.pressure});
  if(t%60===59||t===duration-1)snapshots.push({tick:t,energy:x.s.energy,
    integrity:z.integrity,material:x.material});
 }
 const pending=x.queue.filter(z=>z.due>=x.duration).reduce((a,z)=>a+z.amount,0);
 const cacheResidual=Math.max(Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),
  Math.abs(x.energyFlux-x.energyIn-x.energyWaste),
  Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84));
 const materialResidual=Math.abs(.2+x.materialIn+ledger.injectedMaterial-
  x.materialSpent-ledger.withdrawnMaterial-x.material);
 if(cacheResidual>1e-8||materialResidual>1e-8)throw Error('resource reconciliation failure');
 const aliveTicks=trace.filter(z=>z.energy>.08&&z.integrity>.15).length;
 return {cap,family,seed,duration,stress,mode,aliveTicks,
  fullSurvival:aliveTicks===duration,meanIntegrity:x.s.area/duration,
  reserveTicks:trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  finalEnergy:x.s.energy,finalMaterial:x.material,repairs,rejectedByFloor,
  ledger:{...ledger,cacheResidual,materialResidual},trace,snapshots,chosen};
}
function wag269Metrics(rows){
 const n=rows.length;
 return {n,fullSurvival:rows.filter(z=>z.fullSurvival).length,
  survivalRate:rows.filter(z=>z.fullSurvival).length/n,
  meanAliveRatio:rows.reduce((s,z)=>s+z.aliveTicks/z.duration,0)/n,
  meanReserveRatio:rows.reduce((s,z)=>s+z.reserveTicks/z.duration,0)/n,
  meanIntegrity:rows.reduce((s,z)=>s+z.meanIntegrity,0)/n,
  meanRepairs:rows.reduce((s,z)=>s+z.repairs,0)/n};
}
function wag269Frontier(points){
 return points.map(p=>({...p,
  dominated:points.some(q=>q.mode!==p.mode&&
   q.survivalRate>=p.survivalRate-1e-12&&q.meanIntegrity>=p.meanIntegrity-1e-12&&
   (q.survivalRate>p.survivalRate+1e-12||q.meanIntegrity>p.meanIntegrity+1e-12))
 })).map(p=>({...p,pareto:!p.dominated}));
}
function wag269Experiment(frozen,models,horizon){
 const rows=[];
 for(const duration of WAG269_HORIZONS)for(const family of WAG269_FAMILIES)
 for(const stress of WAG269_STRESS)for(const cap of [8,13])
 for(const seed of WAG269_SEEDS)for(const mode of WAG269_MODES){
  const r=wag269Run(cap,family,seed,duration,stress,mode,frozen,models,horizon);
  rows.push({duration,family,stress,cap,seed,mode,
    aliveTicks:r.aliveTicks,fullSurvival:r.fullSurvival,
    meanIntegrity:r.meanIntegrity,reserveTicks:r.reserveTicks,
    repairs:r.repairs,rejectedByFloor:r.rejectedByFloor,
    maxContinuity:r.ledger.continuityMax,
    cacheResidual:r.ledger.cacheResidual,materialResidual:r.ledger.materialResidual});
 }
 const frontier=Object.fromEntries(WAG269_HORIZONS.map(duration=>[duration,
  wag269Frontier(WAG269_MODES.map(mode=>({mode,duration,
   ...wag269Metrics(rows.filter(z=>z.mode===mode&&z.duration===duration))})))]));
 return {bound:'WAG-269',phase:'WAG-III',turn:1,
  frozenPolicy:frozen.policy,candidateContract:WAG269_CONDITIONAL,
  seeds:WAG269_SEEDS,frontier,rows,
  summary:{policyRuns:rows.length,matchedConditions:rows.length/WAG269_MODES.length,
   durationList:WAG269_HORIZONS,maxContinuity:Math.max(...rows.map(z=>z.maxContinuity)),
   maxCacheResidual:Math.max(...rows.map(z=>Math.abs(z.cacheResidual))),
   maxMaterialResidual:Math.max(...rows.map(z=>Math.abs(z.materialResidual)))},
  caveats:['One synthetic source ancestry; no general physical claim',
   'Conditional candidate thresholds predeclared, not selected from holdouts',
   '240/480 use periodically recycled stress shapes, not fully novel physics',
   'This Pareto analysis is descriptive; no controller is promoted']};
}
if(typeof module!=='undefined')module.exports={wag269Stress,wag269Run,wag269Metrics,wag269Frontier,wag269Experiment};
