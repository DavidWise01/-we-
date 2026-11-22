/* WAG-267 · ranked performance & falsification · Phase II turn 11/12 · .dlw
  PREDECLARED RANKING before evaluation:
  1. more full-survival episodes, 2. mean alive ticks,
  3. mean reserve ticks, 4. mean structural integrity.
  Exact ties choose the frozen policy, then rejected adaptive, then no-repair.
  Compare three predetermined policies across the SAME 256 synthetic cases.
  Ranking is DIAGNOSTIC, not permission to alter WAG264's frozen policy.
*/
const WAG267_MODES=['frozen','rejectedAdaptive','noRepair'];
const WAG267_RANK_KEYS=['fullSurvival','meanAlive','meanReserve','meanIntegrity'];
function wag267NoRepair(cap,family,seed,duration,stress,models){
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const ext={withdrawnEnergy:0,injectedEnergy:0,withdrawnMaterial:0,
  injectedMaterial:0,stresses:[],continuityMax:0,lastEnergy:x.s.energy,lastMaterial:x.material};
 const trace=[];
 for(let t=0;t<duration;t++){
  ext.continuityMax=Math.max(ext.continuityMax,Math.abs(x.s.energy-ext.lastEnergy),
   Math.abs(x.material-ext.lastMaterial));
  step244(x,'abstain');wag265Apply(x,stress,seed,t,ext);
  ext.lastEnergy=x.s.energy;ext.lastMaterial=x.material;
  const z=x.s.trace.at(-1);
  trace.push({tick:t,energy:x.s.energy,material:x.material,integrity:z.integrity,
   ceiling:z.ceiling,action:'abstain'});
 }
 const pending=x.queue.filter(z=>z.due>=x.duration).reduce((a,z)=>a+z.amount,0);
 const cacheError=Math.max(Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),
  Math.abs(x.energyFlux-x.energyIn-x.energyWaste),
  Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84));
 const materialError=Math.abs(.2+x.materialIn+ext.injectedMaterial-
  x.materialSpent-ext.withdrawnMaterial-x.material);
 if(cacheError>1e-8||materialError>1e-8)throw Error('No-repair conservation failed');
 return {mode:'noRepair',capacity:cap,family,seed,duration,stress,
  meanIntegrity:x.s.area/duration,aliveTicks:trace.filter(z=>z.energy>.08&&z.integrity>.15).length,
  reserveTicks:trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  finalEnergy:x.s.energy,finalMaterial:x.material,
  repairs:0,trace,external:ext,ledger:{cacheError,materialError}};
}
function wag267Run(cap,family,seed,duration,stress,mode,frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 if(mode==='noRepair')return wag267NoRepair(cap,family,seed,duration,stress,models);
 if(mode==='frozen'||mode==='rejectedAdaptive')
   return wag265Run(cap,family,seed,duration,stress,mode,frozen,models,horizon);
 throw Error('Unrecognized ranked policy');
}
function wag267Summary(rows,mode){
 const r=rows.filter(x=>x.mode===mode),n=r.length;
 if(!n)throw Error('No ranking evidence '+mode);
 return {mode,n,fullSurvival:r.filter(z=>z.aliveTicks===240).length,
  survivalFailures:r.filter(z=>z.aliveTicks<240).length,
  meanAlive:r.reduce((v,z)=>v+z.aliveTicks,0)/n,
  meanReserve:r.reduce((v,z)=>v+z.reserveTicks,0)/n,
  meanIntegrity:r.reduce((v,z)=>v+z.meanIntegrity,0)/n,
  meanRepairs:r.reduce((v,z)=>v+z.repairs,0)/n};
}
function wag267Rank(summaries){
 return summaries.slice().sort((a,b)=>{
  for(const key of WAG267_RANK_KEYS){
   const delta=b[key]-a[key];
   if(Math.abs(delta)>1e-12)return delta;
  }
  return WAG267_MODES.indexOf(a.mode)-WAG267_MODES.indexOf(b.mode);
 }).map((z,i)=>({...z,rank:i+1}));
}
function wag267Experiment(frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 const rows=[],cases=[];
 for(const stress of WAG265_STRESS)for(const family of WAG265_FAMILIES)
 for(const cap of CAP234)for(const seed of WAG265_TEST){
  const results={};
  for(const mode of WAG267_MODES){
   const r=wag267Run(cap,family,seed,240,stress,mode,frozen,models,horizon);
   const row={cap,family,seed,stress,mode,aliveTicks:r.aliveTicks,
    reserveTicks:r.reserveTicks,meanIntegrity:r.meanIntegrity,repairs:r.repairs,
    finalEnergy:r.finalEnergy,finalMaterial:r.finalMaterial,
    energyLedgerResidual:r.ledger.nativeEnergyResidual??r.ledger.cacheError,
    materialLedgerResidual:r.ledger.externalMaterialResidual??r.ledger.materialError,
    continuity:r.external.continuityMax};
   rows.push(row);results[mode]=row;
  }
  cases.push({cap,family,seed,stress,
    aliveDifferenceAdaptive:results.rejectedAdaptive.aliveTicks-results.frozen.aliveTicks,
    aliveDifferenceNoRepair:results.noRepair.aliveTicks-results.frozen.aliveTicks,
    integrityDifferenceAdaptive:results.rejectedAdaptive.meanIntegrity-results.frozen.meanIntegrity,
    integrityDifferenceNoRepair:results.noRepair.meanIntegrity-results.frozen.meanIntegrity});
 }
 const ranking=wag267Rank(WAG267_MODES.map(mode=>wag267Summary(rows,mode)));
 const maxLedger=Math.max(...rows.map(z=>Math.max(Math.abs(z.energyLedgerResidual),
  Math.abs(z.materialLedgerResidual),z.continuity)));
 return {bound:'WAG-267',phase:'II',turn:11,rankingRule:WAG267_RANK_KEYS,
  frozenPolicy:frozen.policy,ranking,rows,cases,
  summary:{matchedScenarios:cases.length,policyRuns:rows.length,
   frozenFailures:ranking.find(z=>z.mode==='frozen').survivalFailures,
   maxResourceResidual:maxLedger},
  caveats:['Ranked outcomes are synthetic, not independent physical validation',
   'No repair is a comparator, not a deployable recommendation',
   'Ranking does not change the WAG264 precommitted policy',
   'Equal ranks resolved by declared stable order; cannot claim superiority from ties']};
}
if(typeof module!=='undefined')module.exports={wag267NoRepair,wag267Run,wag267Rank,wag267Experiment};
