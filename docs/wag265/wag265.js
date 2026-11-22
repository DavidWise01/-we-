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
if(typeof module!=='undefined')module.exports={wag265Stress,wag265Apply,wag265Run,wag265Pair};
