/* WAG-265 · precommitted out-of-distribution stress · Phase II 9/12 · .dlw
  Controller policy frozen in WAG-264 before these tests. Four entirely new
  synthetic schedules add environmental energy and material losses to WAG244.
  No online access to stress schedule or holdout outcomes. An exploratory
  rejected-adaptive comparator is evaluated but never selected retroactively.
  This tests stress robustness inside ONE common simulator, not physical transfer.
*/
const WAG265_TEST=[5501,5502,5503,5504];
const WAG265_STRESS=['late-collapse','double-shock','intermittent','resource-squeeze'];
const WAG265_FAMILIES=['scar','combined','phaseflip','famine'];
function wag265Stress(t,kind,seed){
 const phase=seed%11;
 if(kind==='late-collapse')return {energy:t>=145&&t<224?-.0058:0,material:0};
 if(kind==='double-shock')return {energy:[82,83,144,145,191].includes(t)?-.11:0,material:0};
 if(kind==='intermittent')return {energy:t>=50&&t<225&&((t+phase)%34)<13?-.0046:0,material:0};
 if(kind==='resource-squeeze')return {energy:t>=94&&t<205?-.0023:0,
   material:t>=62&&t<198?-.00125:0};
 throw Error('unknown stress schedule');
}
function wag265Apply(x,kind,seed,t,ledger){
 const requested=wag265Stress(t,kind,seed),beforeEnergy=x.s.energy,beforeMaterial=x.material;
 const energy=Math.max(0,Math.min(1,beforeEnergy+requested.energy));
 const material=Math.max(0,Math.min(1,beforeMaterial+requested.material));
 const dEnergy=energy-beforeEnergy,dMaterial=material-beforeMaterial;
 x.s.energy=energy;x.material=material;
 ledger.withdrawnEnergy+=Math.max(0,-dEnergy);
 ledger.injectedEnergy+=Math.max(0,dEnergy);
 ledger.withdrawnMaterial+=Math.max(0,-dMaterial);
 ledger.injectedMaterial+=Math.max(0,dMaterial);
 const z=x.s.trace.at(-1);z.energy=energy;z.material=material;
 const receipt={tick:t,energyBefore:beforeEnergy,energyAfter:energy,
  materialBefore:beforeMaterial,materialAfter:material,requested,applied:{energy:dEnergy,material:dMaterial}};
 if(requested.energy||requested.material)ledger.stresses.push(receipt);
 return receipt;
}
function wag265Run(cap,family,seed,duration,stress,mode,frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 if(!WAG265_STRESS.includes(stress))throw Error('unsupported stress');
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const fixed=frozen.policy[cap];
 const selectMode=mode==='frozen'?fixed:mode==='rejectedAdaptive'?'adaptive':null;
 if(!selectMode)throw Error('unknown evaluation comparator');
 const gateState={level:'normal',alarmStreak:0,clearStreak:0,changes:[]};
 const ledger={withdrawnEnergy:0,injectedEnergy:0,withdrawnMaterial:0,
  injectedMaterial:0,stresses:[],continuityMax:0,lastEnergy:x.s.energy,lastMaterial:x.material};
 let lastRepair=-100,repairs=0,suppressed=0;
 const trace=[],actions=[],counts={wait:0,prevent:0,rebuild:0},snapshots=[];
 for(let t=0;t<duration;t++){
  ledger.continuityMax=Math.max(ledger.continuityMax,
   Math.abs(ledger.lastEnergy-x.s.energy),Math.abs(ledger.lastMaterial-x.material));
  const gate=wag263Gate(x,gateState);
  const d=wag263Select(x,models,horizon,lastRepair,gate,selectMode);
  const action=d.action;if(action!=='abstain'){lastRepair=t;repairs++}
  if(d.suppressed)suppressed++;
  counts[action==='abstain'?'wait':action]++;
  actions.push(action);
  step244(x,action);
  wag265Apply(x,stress,seed,t,ledger);
  ledger.lastEnergy=x.s.energy;ledger.lastMaterial=x.material;
  const z=x.s.trace.at(-1);
  trace.push({tick:t,energy:x.s.energy,material:x.material,integrity:z.integrity,
   ceiling:z.ceiling,pressure:z.pressure,action,level:gate.level});
  if([48,96,144,192,239].includes(t))snapshots.push({tick:t,energy:x.s.energy,
   material:x.material,integrity:z.integrity,level:gate.level});
 }
 const pending=x.queue.filter(z=>z.due>=x.duration).reduce((a,z)=>a+z.amount,0);
 const energy=Math.max(Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),
  Math.abs(x.energyFlux-x.energyIn-x.energyWaste),
  Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84));
 if(energy>1e-8)throw Error('native cache conservation failed');
 // WAG248 native material invariant excludes external losses, so reconcile
 // the new physical material ledger explicitly (without rewriting the original).
 const matResidual=Math.abs(.2+x.materialIn+ledger.injectedMaterial-
   x.materialSpent-ledger.withdrawnMaterial-x.material);
 const internalMaterialResidual=Math.abs(x.duration*.0009-x.materialIn-x.materialWaste);
 if(matResidual>1e-8||internalMaterialResidual>1e-8)throw Error('external material conservation failed');
 return {mode,selected:selectMode,family,capacity:cap,seed,duration,stress,
  meanIntegrity:x.s.area/duration,finalIntegrity:x.s.integrity,
  finalEnergy:x.s.energy,finalMaterial:x.material,
  aliveTicks:trace.filter(z=>z.energy>.08&&z.integrity>.15).length,
  reserveTicks:trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  repairs,suppressed,counts,trace,actions,snapshots,
  modeChanges:gateState.changes,external:ledger,
  ledger:{nativeEnergyResidual:energy,externalMaterialResidual:matResidual,
   internalMaterialResidual},
  note:'New external energy and material changes are physically persistent. WAG244 native energy conservation accounts for its internal cache only.'};
}
function wag265Pair(cap,family,seed,duration,stress,frozen,models,horizon){
 const frozenRun=wag265Run(cap,family,seed,duration,stress,'frozen',frozen,models,horizon);
 const rejected=wag265Run(cap,family,seed,duration,stress,'rejectedAdaptive',frozen,models,horizon);
 return {cap,family,seed,duration,stress,frozen:frozenRun,rejected,
  adaptiveIntegrityDelta:rejected.meanIntegrity-frozenRun.meanIntegrity,
  adaptiveAliveDelta:rejected.aliveTicks-frozenRun.aliveTicks,
  adaptiveReserveDelta:rejected.reserveTicks-frozenRun.reserveTicks};
}
function wag265Experiment(frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 const rows=[];
 for(const stress of WAG265_STRESS)for(const family of WAG265_FAMILIES)
 for(const cap of CAP234)for(const seed of WAG265_TEST){
  const p=wag265Pair(cap,family,seed,240,stress,frozen,models,horizon);
  rows.push({stress,family,cap,seed,alive:p.frozen.aliveTicks,
   reserve:p.frozen.reserveTicks,integrity:p.frozen.meanIntegrity,
   adaptiveIntegrityDelta:p.adaptiveIntegrityDelta,
   adaptiveAliveDelta:p.adaptiveAliveDelta,adaptiveReserveDelta:p.adaptiveReserveDelta,
   energy:p.frozen.finalEnergy,material:p.frozen.finalMaterial,
   energyResidual:p.frozen.ledger.nativeEnergyResidual,
   materialResidual:p.frozen.ledger.externalMaterialResidual,
   continuity:p.frozen.external.continuityMax});
 }
 const metrics=z=>({cases:z.length,fullSurvival:z.filter(v=>v.alive===240).length,
  meanAlive:z.reduce((a,v)=>a+v.alive,0)/z.length,
  meanReserve:z.reduce((a,v)=>a+v.reserve,0)/z.length,
  meanIntegrity:z.reduce((a,v)=>a+v.integrity,0)/z.length,
  adaptiveImproved:z.filter(v=>v.adaptiveIntegrityDelta>1e-10).length,
  adaptiveRegressed:z.filter(v=>v.adaptiveIntegrityDelta< -1e-10).length,
  adaptiveMeanIntegrityDelta:z.reduce((a,v)=>a+v.adaptiveIntegrityDelta,0)/z.length});
 return {bound:'WAG-265',frozenPolicy:frozen.policy,rows,
  summary:{...metrics(rows),byStress:Object.fromEntries(WAG265_STRESS.map(k=>
   [k,metrics(rows.filter(v=>v.stress===k))])),
   maxContinuity:Math.max(...rows.map(v=>v.continuity)),
   maxCacheResidual:Math.max(...rows.map(v=>Math.abs(v.energyResidual))),
   maxMaterialResidual:Math.max(...rows.map(v=>Math.abs(v.materialResidual)))}};
}
if(typeof module!=='undefined')module.exports={wag265Stress,wag265Apply,wag265Run,wag265Pair,wag265Experiment};
