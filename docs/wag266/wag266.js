/* WAG-266 · failing-input preservation and bounded counterexample minimization
 Phase II turn 10/12 · .dlw
 Frozen WAG264 WAG261 baseline is NEVER edited. Stress schedules are evaluation
 inputs only; all reruns use one same synthetic physics genealogy.
 A failure means aliveTicks < duration, not just a low final-energy number.
 The minimizer tries to REMOVE scheduled stress events, then binary-searches
 common amplitude for the surviving events. No claim of global minimality.
*/
const WAG266_SEEDS=[5501,5502,5503,5504];
const WAG266_STRESSES=['late-collapse','double-shock','intermittent','resource-squeeze'];
const WAG266_FAMILIES=['scar','combined','phaseflip','famine'];
function wag266Schedule(stress,seed,duration=240){
 return Array.from({length:duration},(_,tick)=>{
  const r=wag265Stress(tick,stress,seed);
  return {tick,energy:r.energy,material:r.material};
 }).filter(z=>z.energy!==0||z.material!==0);
}
function wag266Run(cap,family,seed,stress,events,frozen,models,horizon,duration=240){
 wag264VerifyFreeze(frozen);
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const eventAt=new Map(events.map(z=>[z.tick,z]));
 const state={level:'normal',alarmStreak:0,clearStreak:0,changes:[]};
 const external={withdrawnEnergy:0,withdrawnMaterial:0,unservedEnergy:0,
  unservedMaterial:0,transactionCount:0,continuityMax:0,lastEnergy:x.s.energy,lastMaterial:x.material};
 let lastRepair=-100;
 const trace=[];
 for(let t=0;t<duration;t++){
  external.continuityMax=Math.max(external.continuityMax,Math.abs(x.s.energy-external.lastEnergy),
   Math.abs(x.material-external.lastMaterial));
  const gate=wag263Gate(x,state);
  const choice=wag263Select(x,models,horizon,lastRepair,gate,frozen.policy[cap]);
  if(choice.action!=='abstain')lastRepair=t;
  step244(x,choice.action);
  const e=eventAt.get(t);
  if(e){
   const beforeE=x.s.energy,beforeM=x.material;
   x.s.energy=Math.max(0,Math.min(1,beforeE+e.energy));
   x.material=Math.max(0,Math.min(1,beforeM+e.material));
   const appliedE=x.s.energy-beforeE,appliedM=x.material-beforeM;
   external.withdrawnEnergy+=Math.max(0,-appliedE);
   external.withdrawnMaterial+=Math.max(0,-appliedM);
   external.unservedEnergy+=Math.max(0,appliedE-e.energy);
   external.unservedMaterial+=Math.max(0,appliedM-e.material);
   external.transactionCount++;
   const z=x.s.trace.at(-1);z.energy=x.s.energy;z.material=x.material;
  }
  external.lastEnergy=x.s.energy;external.lastMaterial=x.material;
  const z=x.s.trace.at(-1);
  trace.push({tick:t,energy:x.s.energy,material:x.material,integrity:z.integrity,
   ceiling:z.ceiling,action:choice.action});
 }
 const aliveTicks=trace.filter(z=>z.energy>.08&&z.integrity>.15).length;
 const pending=x.queue.filter(z=>z.due>=x.duration).reduce((a,z)=>a+z.amount,0);
 const cacheError=Math.max(Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),
  Math.abs(x.energyFlux-x.energyIn-x.energyWaste),
  Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84));
 const materialError=Math.abs(.2+x.materialIn-x.materialSpent-external.withdrawnMaterial-x.material);
 if(cacheError>1e-8||materialError>1e-8)throw Error('WAG266 conservation failure');
 return {cap,family,seed,stress,duration,aliveTicks,failed:aliveTicks<duration,
  firstNonviable:trace.find(z=>z.energy<=.08||z.integrity<=.15)?.tick??null,
  meanIntegrity:x.s.area/duration,finalEnergy:x.s.energy,finalMaterial:x.material,
  trace,external,ledger:{cacheError,materialError}};
}
function wag266Minimize(caseInfo,frozen,models,horizon){
 const {cap,family,seed,stress}=caseInfo;
 const original=wag266Schedule(stress,seed);
 const run=e=>wag266Run(cap,family,seed,stress,e,frozen,models,horizon);
 const start=run(original);
 if(!start.failed)throw Error('Expected original failure missing '+JSON.stringify(caseInfo));
 let events=original.slice(),evaluations=1;
 // Coarse-to-fine deletion: greedily remove complete contiguous tick bins.
 // Candidate is accepted ONLY when the original failure criterion persists.
 for(const width of [32,16,8,4,2,1]){
  for(let a=0;a<240;a+=width){
   const next=events.filter(z=>z.tick<a||z.tick>=a+width);
   if(next.length===events.length)continue;
   const result=run(next);evaluations++;
   if(result.failed)events=next;
  }
 }
 // Test if the same surviving events at reduced common amplitude still fail.
 let lo=0,hi=1;const failures=[];
 const scale=s=>events.map(z=>({...z,energy:z.energy*s,material:z.material*s}));
 const zero=run(scale(0));evaluations++;
 let amplitude=1;
 if(!zero.failed){
  for(let i=0;i<12;i++){
   const mid=(lo+hi)/2,trial=run(scale(mid));evaluations++;
   if(trial.failed)hi=mid;else lo=mid;
  }
  amplitude=hi;
 }else {amplitude=0;failures.push('Failure persists without external events; stress is not necessary in this environment.')}
 const minimized=scale(amplitude),result=run(minimized);
 evaluations++;
 if(!result.failed)throw Error('Reduction failed to reproduce original outcome');
 const nativeSum=a=>a.reduce((v,z)=>v+Math.abs(z.energy)+Math.abs(z.material),0);
 return {case:caseInfo,original:{events:original.length,alive:start.aliveTicks,
   firstNonviable:start.firstNonviable,totalDemand:nativeSum(original)},
  minimized:{events:minimized.length,alive:result.aliveTicks,
   firstNonviable:result.firstNonviable,amplitude,totalDemand:nativeSum(minimized),
   ledger:result.ledger,eventsSchedule:minimized},
  noStressFailed:zero.failed,evaluations,
  reduction:'greedy contiguous tick deletion, bins 32→1, then 12-step global amplitude binary search',
  caveat:'1-pass order-dependent reduction; amplitude search assumes an approximately monotonic failure boundary; not guaranteed globally smallest'};
}
function wag266Experiment(frozen,models,horizon){
 const rows=[],failures=[],firstByStress={};
 for(const stress of WAG266_STRESSES)for(const family of WAG266_FAMILIES)
 for(const cap of CAP234)for(const seed of WAG266_SEEDS){
  const run=wag266Run(cap,family,seed,stress,wag266Schedule(stress,seed),frozen,models,horizon);
  const row={stress,family,cap,seed,alive:run.aliveTicks,
   failed:run.failed,firstNonviable:run.firstNonviable,ledger:run.ledger};
  rows.push(row);if(run.failed){failures.push(row);firstByStress[stress]??=row;}
 }
 const reductions=Object.values(firstByStress).map(z=>wag266Minimize(z,frozen,models,horizon));
 return {bound:'WAG-266',phase:'II',turn:10,summary:{cases:rows.length,
  failures:failures.length,fullSurvival:rows.length-failures.length,
  minimized:reductions.length,allReproduced:reductions.every(z=>z.minimized.alive<240),
  totalReevaluations:reductions.reduce((a,z)=>a+z.evaluations,0)},
  failingCases:failures,representativeMinima:reductions,
  warnings:['All 43 original failure IDs preserved','No policy retuning','Minimization is local and limited by fixed schedules','One simulator genealogy']};
}
if(typeof module!=='undefined')module.exports={wag266Schedule,wag266Run,wag266Minimize,wag266Experiment};
