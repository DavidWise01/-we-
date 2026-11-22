/* WAG-279 · Ranked single-action counterfactual falsification · .dlw
   Surgical tick-55 override of frozen crystalline controller, using frozen WAG261
   reference action observed at that tick in the matched simulator.
   No policy weight changes, no interventions at later ticks.
   This is a deterministic within-model intervention, not outside-model causality.
*/
const WAG279_INTERVENTION_TICK=55;
function wag279SurgicalRun(cap,family,seed,duration,force,at,override,frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 if(!WAG277_HOLDOUT.durations.includes(duration)||!WAG277_HOLDOUT.seeds.includes(seed)||
    !WAG277_HOLDOUT.families.includes(family)||!WAG277_HOLDOUT.forces.includes(force)||
    !WAG277_HOLDOUT.capacities.includes(cap)||!WAG276_CONFIG.permitted.includes(override)||
    at<0||at>=duration)throw Error('invalid intervention');
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 let memory=null,lastRepair=-100,repairs=0;
 let actionAt=null,actualAt=null,normalAt=null;
 const ledger={lastEnergy:x.s.energy,lastMaterial:x.material,energyOut:0,energyIn:0,
   materialOut:0,materialIn:0,charged:0,continuity:0};
 const trace=[];
 for(let t=0;t<duration;t++){
  ledger.continuity=Math.max(ledger.continuity,
    Math.abs(ledger.lastEnergy-x.s.energy),Math.abs(ledger.lastMaterial-x.material));
  const c=wag276Candidate(x,lastRepair,memory);memory=c.memory;
  normalAt=t===at?c.action:normalAt;
  const proposal=t===at?override:c.action;
  const before=x.materialSpent;
  step244(x,proposal);
  const applied=x.s.trace.at(-1).maintenance;
  if(t===at){actionAt=proposal;actualAt=applied}
  if(applied!=='abstain'){repairs++;lastRepair=t}
  ledger.charged+=x.materialSpent-before;
  const v=wag274Force(t,force,seed),e0=x.s.energy,m0=x.material;
  x.s.energy=wag272Clamp(e0+v.energy);x.material=wag272Clamp(m0+v.material);
  const dE=x.s.energy-e0,dM=x.material-m0;
  ledger.energyOut+=Math.max(0,-dE);ledger.energyIn+=Math.max(0,dE);
  ledger.materialOut+=Math.max(0,-dM);ledger.materialIn+=Math.max(0,dM);
  ledger.lastEnergy=x.s.energy;ledger.lastMaterial=x.material;
  const z=x.s.trace.at(-1);z.energy=x.s.energy;z.material=x.material;
  trace.push({tick:t,energy:x.s.energy,material:x.material,integrity:z.integrity,action:applied});
 }
 const pending=x.queue.filter(z=>z.due>=duration).reduce((s,z)=>s+z.amount,0);
 const residual=Math.max(
  Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),
  Math.abs(x.energyFlux-x.energyIn-x.energyWaste),
  Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84),
  Math.abs(.2+x.materialIn+ledger.materialIn-x.materialSpent-ledger.materialOut-x.material),
  Math.abs(ledger.charged-x.materialSpent));
 if(residual>1e-8||ledger.continuity>1e-8)throw Error('reconciliation failed');
 const alive=trace.filter(z=>z.energy>.08&&z.integrity>.15).length;
 return {trace,aliveTicks:alive,fullSurvival:alive===duration,
  meanIntegrity:x.s.area/duration,
  reserveTicks:trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  repairs,actionAt,actualAt,normalAt,residual};
}
function wag279SingleCase(z,frozen,models,horizon){
 const id=z.case,at=z.earliestActionDisagreementTick;
 if(at!==WAG279_INTERVENTION_TICK)throw Error('case does not share fixed intervention tick');
 const args=[id.cap,id.family,id.seed,id.duration,id.force];
 const reference=wag277Run(...args,'frozen',frozen,models,horizon);
 const original=wag277Run(...args,'crystal',frozen,models,horizon);
 const refAction=reference.trace[at].action;
 const override=wag279SurgicalRun(...args,at,refAction,frozen,models,horizon);
 const identicalPrefix=original.trace.slice(0,at)
   .every((r,i)=>JSON.stringify(r)===JSON.stringify(override.trace[i]));
 if(!identicalPrefix)throw Error('prefix mismatch before intervention');
 const later=override.trace.slice(at+1);
 const originalLater=original.trace.slice(at+1);
 const firstAltered=original.trace.findIndex((r,i)=>i>=at&&JSON.stringify(r)!==JSON.stringify(override.trace[i]));
 const didApply=override.actualAt!==original.trace[at].action;
 const originalFailedAt=z.firstFailureTick;
 const survivedOriginalFailure=originalFailedAt<id.duration?
   (override.trace[originalFailedAt].energy>.08&&override.trace[originalFailedAt].integrity>.15):null;
 const integrityDelta=override.meanIntegrity-original.meanIntegrity;
 const aliveDelta=override.aliveTicks-original.aliveTicks;
 const reserveDelta=override.reserveTicks-original.reserveTicks;
 const atFailureIntegrityGain=override.trace[originalFailedAt].integrity-
   original.trace[originalFailedAt].integrity;
 const delayedIntegrityGain=Object.fromEntries([24,48,96].map(l=>[l,at+l<id.duration?
  override.trace[at+l].integrity-original.trace[at+l].integrity:null]));
 const reproduced=wag279SurgicalRun(...args,at,refAction,frozen,models,horizon);
 if(JSON.stringify(reproduced.trace)!==JSON.stringify(override.trace))throw Error('intervention nondeterministic');
 return {id,kind:z.kind,interventionTick:at,
   requestedReferenceAction:refAction,originalCrystalAction:original.trace[at].action,
   actualOverrideAction:override.actualAt,didApply,
   identicalPrefix,firstAltered,
   aliveDelta,reserveDelta,integrityDelta,atFailureIntegrityGain,
   survivedOriginalFailure,delayedIntegrityGain,
   original:{aliveTicks:original.aliveTicks,fullSurvival:original.fullSurvival,
    meanIntegrity:original.meanIntegrity},
   intervention:{aliveTicks:override.aliveTicks,fullSurvival:override.fullSurvival,
    meanIntegrity:override.meanIntegrity},
   maxResidual:Math.max(original.residual,override.residual),
   replayDeterministic:true,
   traceAtIntervention:{original:original.trace[at],counterfactual:override.trace[at]},
   traceAtFailure:{original:original.trace[originalFailedAt],
    counterfactual:override.trace[originalFailedAt]}};
}
function wag279Experiment(frozen,models,horizon,previous){
 if(previous?.bound!=='WAG-278'||previous.examples.length!==8)
  throw Error('requires immutable WAG278 receipt');
 const rows=previous.examples.map(z=>wag279SingleCase(z,frozen,models,horizon));
 // Lexicographic ranking with survival first, then structural integrity,
 // then shorter reproducible failure onset, all preserved in the receipt.
 const ranked=rows.slice().sort((a,b)=>
  b.aliveDelta-a.aliveDelta||b.integrityDelta-a.integrityDelta||
  a.id.seed-b.id.seed).map((z,i)=>({...z,rank:i+1}));
 return {bound:'WAG-279',phase:'WAG-III',turn:11,
  primitive:'---@---@---@---@---{} → {\\a{b/}}',
  intervention:{tick:55,type:'single action from frozen matched WAG261 arm',
   allLaterDecisions:'original crystalline decision law, evolving state',
   noTuning:true},
  ranked,
  summary:{cases:rows.length,applicableOverrides:rows.filter(z=>z.didApply).length,
   survivalImprovements:rows.filter(z=>z.aliveDelta>0).length,
   survivalRegressions:rows.filter(z=>z.aliveDelta<0).length,
   integrityImprovements:rows.filter(z=>z.integrityDelta>1e-12).length,
   integrityRegressions:rows.filter(z=>z.integrityDelta< -1e-12).length,
   restoredSurvivalAtOriginalFailure:rows.filter(z=>z.kind==='survival-loss'&&z.survivedOriginalFailure).length,
   maxResidual:Math.max(...rows.map(z=>z.maxResidual)),
   deterministic:rows.every(z=>z.replayDeterministic&&z.identicalPrefix)},
  cautions:['Results are within-model causal interventions conditional on this synthetic simulator',
   'One action at tick 55 is not proof of a generalizable repair policy',
   'The selected cases reuse WAG277 withheld evidence; no new holdout',
   'Frozen candidate and WAG261 reference left unchanged']};
}
if(typeof module!=='undefined')module.exports={wag279SurgicalRun,wag279SingleCase,wag279Experiment};
