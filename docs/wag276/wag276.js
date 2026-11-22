/* WAG-276 FINAL CANDIDATE: {\a{b/}} crystalline neural mesh.
   Precommitted before held-out WAG277. Fixed coefficients and one action gate.
   Outer a and nested b exchange 8×8 opposed signals in 3 pulses.
   Neural signals never spend material. WAG244 authoritative step applies cost.
   Selection is deliberately non-trained and remains experimental.
*/
const WAG276_CONFIG=Object.freeze({
 primitive:'{\\a{b/}}',passes:3,railWeight:.125,
 permitted:['abstain','prevent','rebuild'],
 minPermit:.57,minRequest:.51,
 energyReserve:.4,materialReserve:.026,minRepairGap:7,
 comparisonSeeds:[6301,6302,6303],durations:[240,480],
 forceFamilies:['antiphase','surge-crash','shrinking-cycle','dual-burst']
});
function wag276Candidate(x,lastRepair,memory=null){
 const base=wag272Mesh(x,lastRepair,memory);
 const a=base.a,b=base.b,u=base.inputs;
 const av=[a.survive,a.reserve,a.risk,a.permit,u.energy,u.material,u.integrity,u.scar];
 const bv=[b.prevent,b.rebuild,b.urgency,b.request,u.pressure,u.scar,u.energy,u.material];
 const crystal=wag276CrystalPropagate(av,bv);
 // Crystal rails alter the proposed score, and thus the actual single action.
 const railPermit=wag272Clamp(.72*a.permit+.28*crystal.a[3]);
 const railRequest=wag272Clamp(.72*b.request+.28*crystal.b[3]);
 const preferred=base.prefer;
 const physical=base.reasons.eligible&&base.reasons.safety&&base.reasons.timing;
 const accept=physical&&base.reasons.worth&&
  railPermit>=WAG276_CONFIG.minPermit&&railRequest>=WAG276_CONFIG.minRequest;
 return {action:accept?preferred:'abstain',prefer:preferred,accept,
   railPermit,railRequest,physical,base,crystal,memory:base.memory};
}
function wag276Run(cap,family,seed,duration,force,mode,frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 if(!WAG276_CONFIG.durations.includes(duration)||
    !WAG276_CONFIG.forceFamilies.includes(force)||
    !['crystal','mesh','frozen'].includes(mode))throw Error('WAG276 invalid input');
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const gate={level:'normal',alarmStreak:0,clearStreak:0,changes:[]};
 const ledger={lastEnergy:x.s.energy,lastMaterial:x.material,
  externalEnergy:0,externalMaterial:0,externalEnergyIn:0,externalMaterialIn:0,
  internalMaterialCharge:0,continuity:0};
 let lastRepair=-100,neuralMemory=null,repairs=0,denied=0,crystalVeto=0;
 const trace=[],snapshots=[];
 for(let t=0;t<duration;t++){
  ledger.continuity=Math.max(ledger.continuity,Math.abs(ledger.lastEnergy-x.s.energy),
    Math.abs(ledger.lastMaterial-x.material));
  // Both experimental controllers read the identical original mesh activations.
  const c=wag276Candidate(x,lastRepair,neuralMemory);neuralMemory=c.memory;
  const requested=mode==='crystal'?c.action:mode==='mesh'?c.base.action:
   wag263Select(x,models,horizon,lastRepair,wag263Gate(x,gate),'baseline').action;
  if(mode==='crystal'&&c.base.action!=='abstain'&&requested==='abstain')crystalVeto++;
  const before=x.materialSpent;
  step244(x,requested);
  const actual=x.s.trace.at(-1).maintenance;
  if(requested!=='abstain'&&actual!==requested)denied++;
  if(actual!=='abstain'){repairs++;lastRepair=t}
  ledger.internalMaterialCharge+=x.materialSpent-before;
  const z=wag274Force(t,force,seed),e0=x.s.energy,m0=x.material;
  x.s.energy=wag272Clamp(e0+z.energy);x.material=wag272Clamp(m0+z.material);
  const de=x.s.energy-e0,dm=x.material-m0;
  ledger.externalEnergy+=Math.max(0,-de);ledger.externalMaterial+=Math.max(0,-dm);
  ledger.externalEnergyIn+=Math.max(0,de);ledger.externalMaterialIn+=Math.max(0,dm);
  ledger.lastEnergy=x.s.energy;ledger.lastMaterial=x.material;
  const after=x.s.trace.at(-1);after.energy=x.s.energy;after.material=x.material;
  trace.push({tick:t,energy:x.s.energy,integrity:after.integrity,
   material:x.material,action:actual,
   railPermit:c.railPermit,railRequest:c.railRequest});
  if(t%24===0)snapshots.push({tick:t,action:actual,meshProposed:c.base.action,
   crystalProposed:c.action,railPermit:c.railPermit,railRequest:c.railRequest});
 }
 const pending=x.queue.filter(q=>q.due>=duration).reduce((s,q)=>s+q.amount,0);
 const conservation=Math.max(
  Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),
  Math.abs(x.energyFlux-x.energyIn-x.energyWaste),
  Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84),
  Math.abs(.2+x.materialIn+ledger.externalMaterialIn-
   x.materialSpent-ledger.externalMaterial-x.material),
  Math.abs(ledger.internalMaterialCharge-x.materialSpent));
 if(conservation>1e-8)throw Error('WAG276 conservation failure');
 const alive=trace.filter(z=>z.energy>.08&&z.integrity>.15).length;
 return {mode,cap,family,seed,duration,force,aliveTicks:alive,
  fullSurvival:alive===duration,
  reserveTicks:trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  meanIntegrity:x.s.area/duration,repairs,denied,crystalVeto,
  conservation,continuity:ledger.continuity,ledger,trace,snapshots};
}
function wag276Experiment(frozen,models,horizon){
 const rows=[],cases=[];
 for(const duration of WAG276_CONFIG.durations)
 for(const family of ['scar','combined'])
 for(const force of WAG276_CONFIG.forceFamilies)
 for(const cap of [8,13])
 for(const seed of WAG276_CONFIG.comparisonSeeds){
  const group={};
  for(const mode of ['frozen','mesh','crystal']){
   const r=wag276Run(cap,family,seed,duration,force,mode,frozen,models,horizon);
   const row={mode,duration,family,force,cap,seed,aliveTicks:r.aliveTicks,
    fullSurvival:r.fullSurvival,reserveTicks:r.reserveTicks,
    meanIntegrity:r.meanIntegrity,repairs:r.repairs,crystalVeto:r.crystalVeto,
    conservation:r.conservation,continuity:r.continuity};
   rows.push(row);group[mode]=row;
  }
  cases.push({duration,family,force,cap,seed,
   crystalAliveDelta:group.crystal.aliveTicks-group.frozen.aliveTicks,
   crystalIntegrityDelta:group.crystal.meanIntegrity-group.frozen.meanIntegrity,
   vsMeshIntegrity:group.crystal.meanIntegrity-group.mesh.meanIntegrity});
 }
 const aggregate={};
 for(const d of WAG276_CONFIG.durations)aggregate[d]=Object.fromEntries(['frozen','mesh','crystal'].map(mode=>{
  const r=rows.filter(z=>z.duration===d&&z.mode===mode),n=r.length;
  return [mode,{n,fullSurvival:r.filter(z=>z.fullSurvival).length,
   meanAliveRatio:r.reduce((a,z)=>a+z.aliveTicks/z.duration,0)/n,
   meanReserveRatio:r.reduce((a,z)=>a+z.reserveTicks/z.duration,0)/n,
   meanIntegrity:r.reduce((a,z)=>a+z.meanIntegrity,0)/n,
   meanRepairs:r.reduce((a,z)=>a+z.repairs,0)/n,
   totalCrystalVeto:r.reduce((a,z)=>a+z.crystalVeto,0)}];
 }));
 return {bound:'WAG-276',phase:'WAG-III',turn:8,primitive:WAG276_CONFIG.primitive,
  contract:WAG276_CONFIG,aggregate,rows,cases,
  summary:{policyRuns:rows.length,matchedConditions:cases.length,
   crystalIntegrityRegressions:cases.filter(c=>c.crystalIntegrityDelta< -1e-12).length,
   crystalAliveRegressions:cases.filter(c=>c.crystalAliveDelta<0).length,
   maxConservation:Math.max(...rows.map(r=>r.conservation)),
   maxContinuity:Math.max(...rows.map(r=>r.continuity))},
  cautions:['Candidate coefficients predeclared, not learned',
   'Comparison observations not permission to revise this frozen candidate',
   'Physical transfer remains WAG244 only',
   'One synthetic simulator ancestry, not an independent physics test']};
}
if(typeof module!=='undefined')module.exports={
 WAG276_CONFIG,wag276Candidate,wag276Run,wag276Experiment};
